"""Primary class for stimulus data specific to natural movies."""

import h5py
import numpy
from neuroconv.basedatainterface import BaseDataInterface
from pynwb.file import NWBFile
from pynwb.image import ImageSeries, IndexSeries

from .shared_methods import add_stimulus_device


class NaturalMovieStimulusInterface(BaseDataInterface):
    """Stimulus interface specific to the natural movies for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        if "StimulusDisplay" not in nwbfile.devices:
            add_stimulus_device(nwbfile=nwbfile)
        stimulus_device = nwbfile.devices["StimulusDisplay"]

        possible_template_name_map = dict(
            natural_movie_one_image_stack="natural_movie_one",
            natural_movie_two_image_stack="natural_movie_two",
            natural_movie_three_image_stack="natural_movie_three",
        )
        possible_presentation_names = [
            "natural_movie_one_stimulus",
            "natural_movie_two_stimulus",
            "natural_movie_three_stimulus",
        ]

        for (source_name, image_series_name), presentation_name in zip(
            possible_template_name_map.items(), possible_presentation_names
        ):
            if source_name not in self.v1_nwbfile["stimulus"]["templates"]:
                continue

            # Template
            natural_movie_template_source = self.v1_nwbfile["stimulus"]["templates"][source_name]
            natural_movie_data = natural_movie_template_source["data"][:]

            image_series = ImageSeries(
                name=image_series_name,
                description="A natural movie presented to the subject.",
                data=natural_movie_data,
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
            natural_movie_presentation_timestamps = natural_movie_presentation_source["timestamps"][:]

            index_series = IndexSeries(
                name=presentation_name,
                description="The order and timing for presentation of frames from the the natural movie templates.",
                data=natural_movie_presentation_data,
                indexed_timeseries=image_series,
                unit="n.a.",
                timestamps=natural_movie_presentation_timestamps,
            )
            nwbfile.add_stimulus(timeseries=index_series)
