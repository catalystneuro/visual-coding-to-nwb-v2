"""Primary class for stimulus data specific to static gratings."""

import h5py
from neuroconv.basedatainterface import BaseDataInterface
from pynwb.file import NWBFile, TimeIntervals


class StaticGratingStimuliInterface(BaseDataInterface):
    """Stimulus interface specific to the natural scenes for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        if "static_gratings_stimulus" not in self.v1_nwbfile["stimulus"]["presentation"]:
            return

        static_gratings_source = self.v1_nwbfile["stimulus"]["presentation"]["static_gratings_stimulus"]

        static_gratings = TimeIntervals(
            name="static_gratings", description="Parameterizations of visual non-moving gratings shown to the subject."
        )
        static_gratings.add_column(
            name="orientation", description="The angle of the line"  # TODO: angle relative to what?
        )
        static_gratings.add_column(name="spatial_frequency", description="")
        static_gratings.add_column(name="phase", description="")

        # TODO: make sure that these feature orders are the same in all files
        frames_per_second = 60  # as taken from the 'cycle' value in the Allen SDK
        for timestamp, (frame_start, frame_stop), (orientation, spatial_frequency, phase) in zip(
            static_gratings_source["timestamps"][:],
            static_gratings_source["frame_duration"][:],
            static_gratings_source["data"][:],
        ):
            static_gratings.add_interval(
                start_time=timestamp,
                stop_time=timestamp + (frame_stop - frame_start) / frames_per_second,
                orientation=orientation,
                spatial_frequency=spatial_frequency,
                phase=phase,
            )

        # TODO: when NWB Schema allows, add these to stimuli
        nwbfile.add_acquisition(static_gratings)
