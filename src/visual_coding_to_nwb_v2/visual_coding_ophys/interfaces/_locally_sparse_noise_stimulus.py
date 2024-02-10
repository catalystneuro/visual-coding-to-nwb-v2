"""Primary class for stimulus data specific to locally sparse images."""

import h5py
import numpy
from neuroconv.basedatainterface import BaseDataInterface
from pynwb.file import NWBFile
from pynwb.image import Image, Images, IndexSeries


class LocallySparseNoiseStimulusInterface(BaseDataInterface):
    """Stimulus interface specific to the locally sparse scenes for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        name_variations = ["", "_4deg", "_8deg"]

        for name_variation in name_variations:
            presentation_name = f"locally_sparse_noise{name_variation}_stimulus"

            if presentation_name not in self.v1_nwbfile["stimulus"]["presentation"]:
                continue

            # Template
            template_source_name = f"locally_sparse_noise{name_variation}_image_stack"
            template_source = self.v1_nwbfile["stimulus"]["templates"][template_source_name]

            # Data should always be able to fit into RAM
            source_images = template_source["data"][:]

            images = [
                Image(
                    name=f"LocallySparseImage{image_index}",
                    description="A locally sparse image presented to the subject.",
                    data=source_images[image_index, :, :],
                )
                for image_index in range(source_images.shape[0])
            ]
            all_images = Images(
                name=f"locally_sparse_noise{name_variation}_template",
                description="A collection of locally sparse noise images presented to the subject.",
                images=images,
            )
            nwbfile.add_stimulus_template(all_images)

            # Presentation
            presentation_source = self.v1_nwbfile["stimulus"]["presentation"][presentation_name]

            # Original dtype was int64, but there will never be negative values
            # and the were only be at most hundreds of templates
            # Would go with uint16, but HDMF coerces to uint32 anyway
            natural_scenes_presentation_data = numpy.array(presentation_source["data"], dtype="uint32")
            natural_scenes_presentation_timestamps = presentation_source["timestamps"][:]

            index_series = IndexSeries(
                name=presentation_name,
                description="The order and timing for presentation of the locally sparse noise templates.",
                data=natural_scenes_presentation_data,
                indexed_images=all_images,
                unit="n.a.",
                timestamps=natural_scenes_presentation_timestamps,
            )
            nwbfile.add_stimulus(timeseries=index_series)
