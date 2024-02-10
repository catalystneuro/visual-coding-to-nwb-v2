"""Primary class for stimulus data specific to a spontaneous stimulus."""

import h5py
from neuroconv.basedatainterface import BaseDataInterface
from pynwb.file import NWBFile, TimeIntervals


class SpontaneousStimulusInterface(BaseDataInterface):
    """Tnterface specific to a spontaneous stimulus for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        if "spontaneous_stimulus" not in self.v1_nwbfile["stimulus"]["presentation"]:
            return

        spontaneous_stimulus_source = self.v1_nwbfile["stimulus"]["presentation"]["spontaneous_stimulus"]

        spontaneous_stimulus = TimeIntervals(name="spontaneous_stimulus", description="Mean luminance gray image.")

        # Source data alternates on/off timings; roughly 5 minutes each time
        durations = spontaneous_stimulus_source["timestamps"][1::2] - spontaneous_stimulus_source["timestamps"][0::2]
        for start_time, duration in zip(spontaneous_stimulus_source["timestamps"][0::2], durations):
            spontaneous_stimulus.add_interval(start_time=start_time, stop_time=start_time + duration)

        nwbfile.add_stimulus(spontaneous_stimulus)
