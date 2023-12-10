"""Primary class for stimulus data specific to locally sparse images."""
import numpy
import h5py
from pynwb.file import NWBFile
from pynwb.image import Images, Image, IndexSeries
from neuroconv.basedatainterface import BaseDataInterface


class LocallySparseNoiseStimulusInterface(BaseDataInterface):
    """Stimulus interface specific to the locally sparse scenes for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        name_variations = ["", "_4deg", "_8deg"]

        for name_variation in name_variations:
            presentation_name = f"locally_sparse_noise{name_variation}_stimulus"
            template_name = f"locally_sparse_noise{name_variation}_image_stack"

            if presentation_name not in self.v1_nwbfile["stimulus"]["presentation"]:
                continue

            # Template
            template_source = self.v1_nwbfile["stimulus"]["templates"][template_name]

            # Data should always be able to fit into RAM
            source_images = template_source["data"][:]
            # max_frames_per_chunk = int(
            #     10e6 / (source_images.dtype.itemsize * source_images.shape[1] * source_images.shape[2])
            # )
            # image_chunks = (
            #     min(source_images.shape[0], max_frames_per_chunk),
            #     source_images.shape[1],
            #     source_images.shape[2],
            # )

            all_images = Images(
                name=template_name,
                description="A collection of locally sparse noise images presented to the subject.",
                images=[
                    Image(
                        name=f"LocallySparseImage{image_index}",
                        description="A locally sparse image presented to the subject.",
                        data=source_images[image_index, :, :],
                    )
                    for image_index in range(source_images.shape[0])
                ],
            )
            nwbfile.add_stimulus_template(all_images)

            # Presentation
            presentation_source = self.v1_nwbfile["stimulus"]["presentation"][presentation_name]

            # Original dtype was int64, but there will never be negative values
            # and the were only be at most hundreds of templates
            natural_scenes_presentation_data = numpy.array(presentation_source["data"], dtype="uint16")
            # max_frames_per_chunk = int(10e6 / natural_scenes_presentation_data.dtype.itemsize)
            # natural_scenes_presentation_data_chunks = min(
            #     natural_scenes_presentation_data.shape[0], max_frames_per_chunk
            # )

            natural_scenes_presentation_timestamps = presentation_source["timestamps"]
            # timestamp_chunks = min(
            #     natural_scenes_presentation_timestamps.shape[0],
            #     int(10e6 / natural_scenes_presentation_timestamps.dtype.itemsize),
            # )

            index_series = IndexSeries(
                name=presentation_name,
                description="The order and timing for presentation of the locally sparse noise templates.",
                data=natural_scenes_presentation_data,
                indexed_images=all_images,
                unit="n.a.",
                timestamps=natural_scenes_presentation_timestamps,
            )
            nwbfile.add_stimulus(timeseries=index_series)
