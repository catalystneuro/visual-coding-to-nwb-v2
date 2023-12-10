"""Primary class for stimulus data specific to locally sparse images."""
import h5py
import numpy
from neuroconv.basedatainterface import BaseDataInterface
from pynwb import H5DataIO
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
            template_name = f"locally_sparse_noise{name_variation}_image_stack"

            if presentation_name not in self.v1_nwbfile["stimulus"]["presentation"]:
                continue

            # Template
            template_source = self.v1_nwbfile["stimulus"]["templates"][template_name]

            # Original data was in float32 for some reason, even though data values were uint8
            # Data should always be able to fit into RAM
            source_images = numpy.array(template_source["data"], dtype="uint8")
            max_frames_per_chunk = int(
                10e6 / (source_images.dtype.itemsize * source_images.shape[1] * source_images.shape[2])
            )
            image_chunks = (
                min(source_images.shape[0], max_frames_per_chunk),
                source_images.shape[1],
                source_images.shape[2],
            )

            all_images = Images(
                name=template_name,
                description="A collection of locally sparse noise images presented to the subject.",
                images=[Image(H5DataIO(data=source_images, compression=True, chunks=image_chunks))],
            )
            nwbfile.add_stimulus_template(all_images)

            # Presentation
            presentation_source = self.v1_nwbfile["stimulus"]["templates"][presentation_name]

            # Original dtype was int64, but there will never be negative values
            # and the were only be at most hundreds of templates
            natural_scenes_presentation_data = numpy.array(presentation_source["data"], dtype="uint16")
            max_frames_per_chunk = int(10e6 / natural_scenes_presentation_data.dtype.itemsize)
            natural_scenes_presentation_data_chunks = min(
                natural_scenes_presentation_data.shape[0], max_frames_per_chunk
            )

            natural_scenes_presentation_timestamps = presentation_source["timestamps"]
            timestamp_chunks = min(
                natural_scenes_presentation_timestamps.shape[0],
                int(10e6 / natural_scenes_presentation_timestamps.dtype.itemsize),
            )

            index_series = IndexSeries(
                name=presentation_name,
                description="The order and timing for presentation of the locally sparse noise templates.",
                data=H5DataIO(
                    data=natural_scenes_presentation_data,
                    compression=True,
                    chunks=natural_scenes_presentation_data_chunks,
                ),
                indexed_images=all_images,
                unit="n.a.",
                timestamps=H5DataIO(
                    data=natural_scenes_presentation_timestamps, compression=True, chunks=timestamp_chunks
                ),
            )
            nwbfile.add_stimulus(timeseries=index_series)
