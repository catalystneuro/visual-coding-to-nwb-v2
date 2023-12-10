"""Primary class for stimulus data specific to natural scenes."""
import h5py
import numpy
from neuroconv.basedatainterface import BaseDataInterface
from pynwb import H5DataIO
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
        max_frames_per_chunk = int(
            10e6 / (source_images.dtype.itemsize * source_images.shape[1] * source_images.shape[2])
        )
        image_chunks = (
            min(source_images.shape[0], max_frames_per_chunk),
            source_images.shape[1],
            source_images.shape[2],
        )

        all_images = Images(
            name="natural_scenes_template",
            description="A collection of natural scenes presented to the subject.",
            images=[Image(H5DataIO(data=source_images, compression=True, chunks=image_chunks))],
        )
        nwbfile.add_stimulus_template(all_images)

        # Presentation
        # TODO - need to figure out a way to encode duration of a presentation since that did seem to vary
        #        (probably need an extension)
        natural_scenes_presentation_source = self.v1_nwbfile["stimulus"]["templates"]["natural_scenes_stimulus"]

        # Original dtype was int64, but there will never be negative values
        # and the were only be at most hundreds of templates
        natural_scenes_presentation_data = numpy.array(natural_scenes_presentation_source["data"], dtype="uint16")
        max_frames_per_chunk = int(10e6 / natural_scenes_presentation_data.dtype.itemsize)
        natural_scenes_presentation_data_chunks = min(natural_scenes_presentation_data.shape[0], max_frames_per_chunk)

        natural_scenes_presentation_timestamps = natural_scenes_presentation_source["timestamps"]
        timestamp_chunks = min(
            natural_scenes_presentation_timestamps.shape[0],
            int(10e6 / natural_scenes_presentation_timestamps.dtype.itemsize),
        )

        index_series = IndexSeries(
            name="natural_scenes_stimulus",
            description="The order and timing for presentation of the natural scene templates.",
            data=H5DataIO(
                data=natural_scenes_presentation_data,
                compression=True,
                chunks=natural_scenes_presentation_data_chunks,
            ),
            indexed_images=all_images,
            unit="n.a.",
            timestamps=H5DataIO(data=natural_scenes_presentation_timestamps, compression=True, chunks=timestamp_chunks),
        )
        nwbfile.add_stimulus(timeseries=index_series)
