"""Primary class for stimulus data specific to a spontaneous stimulus."""
import h5py
from neuroconv.basedatainterface import BaseDataInterface
from pynwb.file import NWBFile, TimeSeries


class SpontaneousStimulusInterface(BaseDataInterface):
    """Tnterface specific to a spontaneous stimulus for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        if "spontaneous_stimulus" not in self.v1_nwbfile["stimulus"]["presentation"]:
            return

        spontaneous_stimulus_source = self.v1_nwbfile["stimulus"]["presentation"]["spontaneous_stimulus"]

        spontaneous_stimulus = TimeSeries(
            name="spontaneous_stimulus",
            description="A spontaneous stimuli presented to the subject.",
            # TODO: along with general description; have no idea how to interpret this value...
            data=spontaneous_stimulus_source["data"][:],
            unit="n.a.",
            timestamps=spontaneous_stimulus_source["timestamps"][:],
        )

        nwbfile.add_stimulus(spontaneous_stimulus)
