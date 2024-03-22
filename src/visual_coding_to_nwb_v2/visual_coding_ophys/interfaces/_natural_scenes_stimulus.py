"""Primary class for stimulus data specific to natural scenes."""

import h5py
import numpy
from neuroconv.basedatainterface import BaseDataInterface
from pynwb.file import NWBFile
from pynwb.image import Image, Images, IndexSeries


class NaturalSceneStimulusInterface(BaseDataInterface):
    """Stimulus interface specific to the natural scenes for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        # Early exit based on template presence
        if "natural_scenes_image_stack" not in self.v1_nwbfile["stimulus"]["templates"]:
            return

        # Template
        natural_scenes_template_source = self.v1_nwbfile["stimulus"]["templates"]["natural_scenes_image_stack"]

        # Original data was in float32 for some reason, even though data values were uint8
        # Data should always be able to fit into RAM
        source_images = numpy.array(natural_scenes_template_source["data"], dtype="uint8")
        images = [
            Image(
                name=f"NaturalScene{image_index}",
                description="A natural scene presented to the subject. Lasted for exactly 7 frames.",
                data=source_images[image_index, :, :],
            )
            for image_index in range(source_images.shape[0])
        ]
        all_images = Images(
            name="natural_scenes_template",
            description="A collection of natural scenes presented to the subject. Lasted for exactly 7 frames.",
            images=images,
        )
        nwbfile.add_stimulus_template(all_images)

        # Presentation
        natural_scenes_presentation_source = self.v1_nwbfile["stimulus"]["presentation"]["natural_scenes_stimulus"]

        # Original dtype was int64, but there will never be negative values
        # and the were only be at most hundreds of templates
        # Would go with uint16, but HDMF coerces to uint32 anyway
        natural_scenes_presentation_data = numpy.array(natural_scenes_presentation_source["data"], dtype="uint32")
        natural_scenes_presentation_timestamps = natural_scenes_presentation_source["timestamps"][:]

        # The data consists of many repeated presentations, so an IndexSeries is ideal
        # However, there is also a duration at which each image was presented...
        index_series_description = "The order and timing for presentation of the natural scene templates."

        unique_frame_duration = numpy.unique(numpy.diff(natural_scenes_presentation_source["frame_duration"]))
        if unique_frame_duration.shape[0] == 1:
            frames_per_second = 60  # as taken from the 'cycle' value in the Allen SDK
            duration_in_seconds = unique_frame_duration[0] / frames_per_second
            index_series_description += f"Each scene was presented for {duration_in_seconds} seconds."

        index_series = IndexSeries(
            name="natural_scenes_stimulus",
            description="The order and timing for presentation of the natural scene templates.",
            data=natural_scenes_presentation_data,
            indexed_images=all_images,
            unit="n.a.",
            timestamps=natural_scenes_presentation_timestamps,
        )
        nwbfile.add_stimulus(timeseries=index_series)
