"""Primary class for two photon series."""

from typing import Union

import h5py
import numpy
from hdmf.common import DynamicTable, VectorData
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module
from pynwb.file import NWBFile
from pynwb.image import Image, Images
from pynwb.ophys import (
    DfOverF,
    Fluorescence,
    ImageSegmentation,
    PlaneSegmentation,
    RoiResponseSeries,
)

from .shared_methods import add_imaging_device, add_imaging_plane


class VisualCodingProcessedOphysInterface(BaseDataInterface):
    """Two photon calcium imaging interface for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str, df_over_f_events_file_path: Union[str, None] = None):
        self.v1_nwbfile = h5py.File(name=v1_nwbfile_path, mode="r")
        self.df_over_f_events_file_path = df_over_f_events_file_path
        super().__init__(v1_nwbfile_path=v1_nwbfile_path, df_over_f_events_file_path=df_over_f_events_file_path)

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict, stub_test: bool = False):
        ophys_module = get_module(
            nwbfile=nwbfile, name="ophys", description="Contains processed optical physiology data."
        )

        # Shorter aliases to locations in source data file
        source_ophys_module = self.v1_nwbfile["processing"]["brain_observatory_pipeline"]
        source_plane_segmentation = source_ophys_module["ImageSegmentation"]["imaging_plane_1"]
        source_reference_image = source_plane_segmentation["reference_images"]

        # Add reference image
        maximum_intensity_projection_data = source_reference_image["maximum_intensity_projection_image"]["data"][:]
        maximum_intensity_projection_image = Image(
            name="maximum_intensity_projection",
            description="Summary image calculated from maximum intensity of the plane.",
            data=maximum_intensity_projection_data,
        )
        reference_images = Images(
            name="SummaryImages",
            description="Summary images derived from the two-photon calcium imaging.",
            images=[maximum_intensity_projection_image],
        )

        ophys_module.add(data_interfaces=[reference_images])

        # Fetch ophys metadata from source
        local_roi_ids = [int(roi_id.decode("utf-8")) for roi_id in source_ophys_module["ImageSegmentation"]["roi_ids"]]
        local_roi_keys = [
            roi_id.decode("utf-8") for roi_id in source_ophys_module["Fluorescence"]["imaging_plane_1"]["roi_names"][:]
        ]
        number_of_rois = len(local_roi_ids)

        pixel_masks = list()
        for local_roi_key in local_roi_keys:
            pixel_mask = source_plane_segmentation[local_roi_key]["pix_mask"][:]
            pixel_weights = source_plane_segmentation[local_roi_key]["pix_mask_weight"][:]
            # The pix_masks in the source data are transposed compared to their image_mask, so undo that here
            pixel_masks.append([(y, x, w) for (x, y), w in zip(pixel_mask, pixel_weights)])
        global_roi_ids = source_ophys_module["ImageSegmentation"]["cell_specimen_ids"][:]

        # Set or fetch imaging metadata
        if "Microscope" not in nwbfile.devices:
            add_imaging_device(nwbfile=nwbfile)
        if "ImagingPlane" not in nwbfile.imaging_planes:
            source_imaging_plane = self.v1_nwbfile["general"]["optophysiology"]["imaging_plane_1"]
            add_imaging_plane(
                nwbfile=nwbfile,
                depth=source_imaging_plane["imaging depth"][()].decode("utf-8").strip(" microns"),
                location=source_imaging_plane["location"][()].decode("utf-8"),
            )
        imaging_plane = nwbfile.imaging_planes["ImagingPlane"]

        # Add segmentation metadata
        plane_segmentation = PlaneSegmentation(
            name="PlaneSegmentation",
            description="Segmented regions of interest (ROI).",
            imaging_plane=imaging_plane,
            # reference_images=reference_images,  # Only supports linking ImageSeries; to be fixed in ndx-microscopy
        )
        plane_segmentation.add_column(
            name="global_roi_id", description="The global ID assigned to each unique ROI across sessions."
        )

        for global_roi_id, pixel_mask, global_roi_id in zip(local_roi_ids, pixel_masks, global_roi_ids):
            plane_segmentation.add_roi(
                id=global_roi_id,
                pixel_mask=pixel_mask,
                global_roi_id=global_roi_id,
            )

        ophys_module.add(
            data_interfaces=[ImageSegmentation(name="ImageSegmentation", plane_segmentations=plane_segmentation)]
        )

        # Add fluorescence, neuropil response, and demixed signal
        # Small enough to fit in RAM

        neuropil_data = source_ophys_module["Fluorescence"]["imaging_plane_1_neuropil_response"]["data"][:].T
        corrected_fluorescence_data = source_ophys_module["Fluorescence"]["imaging_plane_1"]["data"][:].T
        timestamps = source_ophys_module["Fluorescence"]["imaging_plane_1"]["timestamps"][:]

        region_indices = list(range(number_of_rois))  # Indices into plane segmentation table that uses global IDs
        roi_table_region = plane_segmentation.create_roi_table_region(
            region=region_indices,
            description="The regions of interest (ROIs) this response series refers to.",
        )

        corrected_series = RoiResponseSeries(
            name="Corrected",
            description=(
                "Fluorescence per region of interest (ROI) from the raw imaging after spatial demixing and subtraction "
                "of neuropil background, but prior to dF/F normalization."
            ),
            data=corrected_fluorescence_data,
            timestamps=timestamps,
            unit="n.a.",
            rois=roi_table_region,
        )
        neuropil_series = RoiResponseSeries(
            name="Neuropil",
            description="Fluorescence contaminated by background neuropil.",
            data=neuropil_data,
            timestamps=corrected_series,  # Link timestamps
            unit="n.a.",
            rois=roi_table_region,
        )

        roi_response_series = [neuropil_series, corrected_series]

        # Demixed is occasionally missing; e.g., session ID 507691476
        if "imaging_plane_1_demixed_signal" in source_ophys_module["Fluorescence"]:
            demixed_data = source_ophys_module["Fluorescence"]["imaging_plane_1_demixed_signal"]["data"][:].T
            demixed_series = RoiResponseSeries(
                name="Demixed",
                description="Spatially demixed traces of potentially overlapping masks.",
                data=demixed_data,
                timestamps=corrected_series,  # Link timestamps
                unit="n.a.",
                rois=roi_table_region,
            )
            roi_response_series.append(demixed_series)

        fluorescence = Fluorescence(name="Fluorescence", roi_response_series=roi_response_series)
        ophys_module.add(data_interfaces=[fluorescence])

        # Add dF/F
        df_over_f_data = source_ophys_module["DfOverF"]["imaging_plane_1"]["data"][:].T

        df_over_f_series = RoiResponseSeries(
            name="DfOverF",
            description=(
                "The normalized ΔF/F trace calculated using the AllenSDK. "
                "Please consult the AllenSDK for details of the calculation."
            ),
            data=df_over_f_data,
            timestamps=corrected_series,  # Link timestamps
            unit="a.u.",
            rois=roi_table_region,
        )

        all_df_over_f_series = [df_over_f_series]

        # Add dF/F events
        if self.df_over_f_events_file_path is not None:
            df_over_f_events_data = numpy.load(file=self.df_over_f_events_file_path)

            df_over_f_event_series = RoiResponseSeries(
                name="DfOverFEvents",
                description=(
                    "Events from the ΔF/F detected using the L0 method from the AllenSDK. "
                    "Please consult the AllenSDK for more details of the calculation."
                ),
                data=df_over_f_events_data,
                timestamps=corrected_series,  # Link timestamps
                unit="a.u.",
                rois=roi_table_region,
            )

            all_df_over_f_series.append(df_over_f_event_series)

        df_over_f = DfOverF(name="DfOverF", roi_response_series=all_df_over_f_series)
        ophys_module.add(data_interfaces=[df_over_f])

        # Include contamination ratio
        contamination_ratio_data = source_ophys_module["Fluorescence"]["imaging_plane_1"]["r"][:]
        contamination_ratio_mse_data = source_ophys_module["Fluorescence"]["imaging_plane_1"]["rmse"][:]

        contamination_ratio_table = DynamicTable(
            name="ContaminationRatios",
            description="Pre-calculated statistics quantifying the effectiveness of the neuropil subtraction.",
            columns=[
                VectorData(
                    name="ratios",
                    description=(
                        "The vector of contamination ratios resulting from numerical approximation of the "
                        "equation `RoiResponseSeriesCorrected = RoiResponseSeriesDemixed  - ratios * "
                        " RoiResponseSeriesNeuropil`."
                    ),
                    data=contamination_ratio_data,
                ),
                VectorData(
                    name="ratios_rmse",
                    description=(
                        "The root mean squared error (RMSE) of the contamination ratios scaled by the demixed signal. "
                        " Derived using the equation ` np.sqrt(np.mean(np.square(RoiResponseSeriesCorrected - "
                        "(RoiResponseSeriesDemixed - ratios * RoiResponseSeriesNeuropil)))) / "
                        " np.mean(F_M)`"
                    ),
                    data=contamination_ratio_mse_data,
                ),
            ],
        )
        ophys_module.add(data_interfaces=[contamination_ratio_table])
