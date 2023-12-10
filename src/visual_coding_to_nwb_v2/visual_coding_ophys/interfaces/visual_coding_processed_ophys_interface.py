"""Primary class for two photon series."""
import h5py
from hdmf.common import DynamicTable, VectorData
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module
from pynwb import H5DataIO
from pynwb.file import NWBFile
from pynwb.image import Image, Images
from pynwb.ophys import (DfOverF, Fluorescence, ImageSegmentation,
                         PlaneSegmentation, RoiResponseSeries)

from .shared_methods import add_imaging_device, add_imaging_plane


class VisualCodingProcessedOphysInterface(BaseDataInterface):
    """Two photon calcium imaging interface for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        self.v1_nwbfile = h5py.File(name=v1_nwbfile_path, mode="r")
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)

    def __del__(self):
        """
        The HDF5 files must remain open for buffered writing (they are not read all at once into RAM).

        Garbage collection should close the I/O no matter what, but doesn't hurt to additionally specify here.
        """
        self.v1_nwbfile.close()

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict, stub_test: bool = False):
        ophys_module = get_module(
            nwbfile=nwbfile, name="ophys", description="Contains processed optical physiology data."
        )

        # Shorter aliases to locations in source data file
        source_ophys_module = self.v1_nwbfile["processing"]["brain_observatory_pipeline"]
        source_plane_segmentation = source_ophys_module["ImageSegmentation"]["imaging_plane_1"]
        source_reference_image = source_plane_segmentation["reference_images"]

        # Add reference image
        reference_image_data = source_reference_image["maximum_intensity_projection_image"]["data"][:]
        reference_image = Image(
            name="maximum_intensity_projection",
            description="Summary image calculated from maximum intensity of the plane.",
            data=H5DataIO(reference_image_data, chunks=tuple(reference_image_data.shape), compression=True),
        )
        reference_images = Images(
            name="SummaryImages",
            description="Summary images derived from the two-photon calcium imaging.",
            images=[reference_image],
        )

        ophys_module.add(reference_images)

        # Fetch ophys metadata from source
        source_ophys_module = self.v1_nwbfile["processing"]["brain_observatory_pipeline"]

        global_roi_ids = [int(roi_id.decode("utf-8")) for roi_id in source_ophys_module["ImageSegmentation"]["roi_ids"]]
        local_roi_keys = [
            roi_id.decode("utf-8") for roi_id in source_ophys_module["Fluorescence"]["imaging_plane_1"]["roi_names"][:]
        ]
        number_of_rois = len(global_roi_ids)

        pixel_masks = list()
        for local_roi_key in local_roi_keys:
            pixel_mask = source_plane_segmentation[local_roi_key]["pix_mask"][:]
            pixel_weights = source_plane_segmentation[local_roi_key]["pix_mask_weight"][:]
            pixel_masks.append([(x, y, w) for (x, y), w in zip(pixel_mask, pixel_weights)])
        cell_specimen_ids = source_ophys_module["ImageSegmentation"]["cell_specimen_ids"][:]

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
            name="cell_specimen_id", description="The ID assigned to each unique cell specimen."
        )

        for global_roi_id, pixel_mask, cell_specimen_id in zip(global_roi_ids, pixel_masks, cell_specimen_ids):
            plane_segmentation.add_roi(
                id=global_roi_id,
                pixel_mask=pixel_mask,
                cell_specimen_id=cell_specimen_id,
            )

        ophys_module.add(ImageSegmentation(name="ImageSegmentation", plane_segmentations=plane_segmentation))

        # Add fluorescence, neuropil response, and demixed signal
        # Small enough to fit in RAM
        demixed_data = source_ophys_module["Fluorescence"]["imaging_plane_1_demixed_signal"]["data"][:].T
        neuropil_data = source_ophys_module["Fluorescence"]["imaging_plane_1_neuropil_response"]["data"][:].T
        corrected_fluorescence_data = source_ophys_module["Fluorescence"]["imaging_plane_1"]["data"][:].T

        # All series are the same shape
        max_frames_per_chunk = int(10e6 / (demixed_data.dtype.itemsize * demixed_data.shape[1]))
        data_chunk_shape = (min(demixed_data.shape[0], max_frames_per_chunk), demixed_data.shape[1])

        timestamps = source_ophys_module["Fluorescence"]["imaging_plane_1_demixed_signal"]["timestamps"][:]
        timestamps_chunk_shape = (min(timestamps.shape[0], int(10e6 / timestamps.dtype.itemsize)),)

        region_indices = list(range(number_of_rois))  # Indices into plane segmentation table that uses global IDs
        roi_table_region = plane_segmentation.create_roi_table_region(
            region=region_indices,
            description="The regions of interest (ROIs) this response series refers to.",
        )

        demixed_series = RoiResponseSeries(
            name="RoiResponseSeriesDemixed",
            description="Spatially demixed traces of potentially overlapping masks.",
            data=H5DataIO(data=demixed_data, chunks=data_chunk_shape, compression=True),
            timestamps=H5DataIO(data=timestamps, chunks=timestamps_chunk_shape, compression=True),
            unit="n.a.",
            rois=roi_table_region,
        )
        neuropil_series = RoiResponseSeries(
            name="RoiResponseSeriesNeuropil",
            description="Fluorescence contaminated by background neuropil.",
            data=H5DataIO(data=neuropil_data, chunks=data_chunk_shape, compression=True),
            timestamps=demixed_series,  # Link timestamps
            unit="n.a.",
            rois=roi_table_region,
        )
        corrected_series = RoiResponseSeries(
            name="RoiResponseSeriesCorrected",
            description=(
                "Fluorescence per region of interest (ROI) from the raw imaging after spatial demixing and subtraction "
                "of neuropil background, but prior to normalization."
            ),
            data=H5DataIO(data=corrected_fluorescence_data, chunks=data_chunk_shape, compression=True),
            timestamps=demixed_series,  # Link timestamps
            unit="n.a.",
            rois=roi_table_region,
        )

        fluorescence = Fluorescence(
            name="Fluorescence",
            roi_response_series=[
                demixed_series,
                neuropil_series,
                corrected_series,
            ],
        )
        ophys_module.add(fluorescence)

        # Add dF/F
        df_over_f_data = source_ophys_module["DfOverF"]["imaging_plane_1"]["data"][:].T

        # All series are the same shape
        max_frames_per_chunk = int(10e6 / (demixed_data.dtype.itemsize * demixed_data.shape[1]))
        data_chunk_shape = (min(demixed_data.shape[0], max_frames_per_chunk), demixed_data.shape[1])

        df_over_f_series = RoiResponseSeries(
            name="DfOverF",
            description=("The ΔF/F trace calculated using the AllenSDK. Please consult the AllenSDK for details."),
            data=H5DataIO(data=df_over_f_data, chunks=data_chunk_shape, compression=True),
            timestamps=demixed_series,  # Link timestamps
            unit="n.a.",
            rois=roi_table_region,
        )

        df_over_f = DfOverF(name="DfOVerF", roi_response_series=df_over_f_series)
        ophys_module.add(df_over_f)

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
                    data=H5DataIO(data=contamination_ratio_data, chunks=(number_of_rois,), compression=True),
                ),
                VectorData(
                    name="ratios_rmse",
                    description=(
                        "The root mean squared error (RMSE) of the contamination ratios scaled by the demixed signal. "
                        " Derived using the equation ` np.sqrt(np.mean(np.square(RoiResponseSeriesCorrected - "
                        "(RoiResponseSeriesDemixed - ratios * RoiResponseSeriesNeuropil)))) / "
                        " np.mean(F_M)`"
                    ),
                    data=H5DataIO(data=contamination_ratio_mse_data, chunks=(number_of_rois,), compression=True),
                ),
            ],
        )
        ophys_module.add(contamination_ratio_table)
