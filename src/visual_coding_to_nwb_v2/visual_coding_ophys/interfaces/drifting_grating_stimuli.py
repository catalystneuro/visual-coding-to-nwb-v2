"""Primary class for stimulus data specific to drifting gratings."""

import h5py
from neuroconv.basedatainterface import BaseDataInterface
from pynwb.file import NWBFile, TimeIntervals


class DriftingGratingStimuliInterface(BaseDataInterface):
    """Stimulus interface specific to the natural scenes for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        if "drifting_gratings_stimulus" not in self.v1_nwbfile["stimulus"]["presentation"]:
            return

        drifting_gratings_source = self.v1_nwbfile["stimulus"]["presentation"]["drifting_gratings_stimulus"]

        drifting_gratings = TimeIntervals(
            name="drifting_gratings",
            description="Parameterizations of visual drifting gratings shown to the subject.",
        )
        drifting_gratings.add_column(
            name="orientation", description="The angle of the line"  # TODO: angle relative to what?
        )
        drifting_gratings.add_column(name="temporal_frequency", description="")
        drifting_gratings.add_column(name="blank_sweep", description="")

        # TODO: make sure that these feature orders are the same in all files
        # In particular, notice how compared to the static_grating, the orientation is second
        frames_per_second = 60  # as taken from the 'cycle' value in the Allen SDK
        for timestamp, (frame_start, frame_stop), (temporal_frequency, orientation, blank_sweep) in zip(
            drifting_gratings_source["timestamps"][:],
            drifting_gratings_source["frame_duration"][:],
            drifting_gratings_source["data"][:],
        ):
            drifting_gratings.add_interval(
                start_time=timestamp,
                stop_time=timestamp + (frame_stop - frame_start) / frames_per_second,
                orientation=orientation,
                temporal_frequency=temporal_frequency,
                blank_sweep=blank_sweep,
            )

        # TODO: when NWB Schema allows, add these to stimuli
        nwbfile.add_acquisition(drifting_gratings)
