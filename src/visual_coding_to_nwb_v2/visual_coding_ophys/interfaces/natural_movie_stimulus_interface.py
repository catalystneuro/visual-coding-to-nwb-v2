"""Primary class for stimulus data specific to natural movies."""
import numpy
import h5py
from pynwb import H5DataIO
from pynwb.file import NWBFile
from pynwb.image import ImageSeries, IndexSeries
from neuroconv.basedatainterface import BaseDataInterface

from .shared_methods import add_stimulus_device


class NaturalMovieStimulusInterface(BaseDataInterface):
    """Stimulus interface specific to the natural movies for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        # TODO - assess consistency of stim template types
        # TODO - the templates have a field of view set, but these would be more properties of an OpticalSeries
        #        but they also don't seem to be used at all in the SDK (FoV for ophys is used commonly though)
        if "StimulusDisplay" not in nwbfile.devices:
            add_stimulus_device(nwbfile=nwbfile)
        stimulus_device = nwbfile.devices["StimulusDisplay"]

        possible_template_name_map = dict(
            natural_movie_one_image_stack="natural_movie_one", natural_movie_two_image_stack="natural_movie_two"
        )
        possible_presentation_names = ["natural_movie_one_stimulus", "natural_movie_two_stimulus"]

        for (source_name, image_series_name), presentation_name in zip(
            possible_template_name_map.items(), possible_presentation_names
        ):
            if source_name not in self.v1_nwbfile["stimulus"]["templates"]:
                continue

            # Template
            natural_movie_template_source = self.v1_nwbfile["stimulus"]["templates"][source_name]

            natural_movie_data = natural_movie_template_source["data"][:]
            max_frames_per_chunk = int(
                10e6 / (natural_movie_data.dtype.itemsize * natural_movie_data.shape[1] * natural_movie_data.shape[2])
            )
            movie_chunks = (
                min(natural_movie_data.shape[0], max_frames_per_chunk),
                natural_movie_data.shape[1],
                natural_movie_data.shape[2],
            )

            image_series = ImageSeries(
                name=image_series_name,
                description="A natural movie presented to the subject.",
                data=H5DataIO(data=natural_movie_data, compression=True, chunks=movie_chunks),
                unit="n.a.",
                # Closest core approximation to their ImageStack that allows efficient packaging of movie
                starting_time=numpy.nan,
                rate=numpy.nan,
                device=stimulus_device,
            )
            nwbfile.add_stimulus_template(timeseries=image_series)

            # Presentation
            natural_movie_presentation_source = self.v1_nwbfile["stimulus"]["presentation"][presentation_name]

            # Original dtype was int64, but there will never be negative values
            # and the were only be at most thousands of frames in the template movies...
            # However, minimal data type for IndexSeries data is uint32, otherwise PyNWB throws warning
            natural_movie_presentation_data = numpy.array(natural_movie_presentation_source["data"][:], dtype="uint32")
            max_frames_per_chunk = int(10e6 / natural_movie_presentation_data.dtype.itemsize)
            natural_movie_presentation_data_chunks = (
                min(natural_movie_presentation_data.shape[0], max_frames_per_chunk),
            )

            natural_movie_presentation_timestamps = natural_movie_presentation_source["timestamps"][:]
            timestamp_chunks = (
                min(
                    natural_movie_presentation_timestamps.shape[0],
                    int(10e6 / natural_movie_presentation_timestamps.dtype.itemsize),
                ),
            )

            index_series = IndexSeries(
                name=presentation_name,
                description="The order and timing for presentation of frames from the the natural movie templates.",
                data=H5DataIO(
                    data=natural_movie_presentation_data,
                    compression=True,
                    chunks=natural_movie_presentation_data_chunks,
                ),
                indexed_timeseries=image_series,
                unit="n.a.",
                timestamps=H5DataIO(
                    data=natural_movie_presentation_timestamps, compression=True, chunks=timestamp_chunks
                ),
            )
            nwbfile.add_stimulus(timeseries=index_series)
