"""Primary class for stimulus data specific to spontaneous stimuli."""
import h5py
from neuroconv.basedatainterface import BaseDataInterface
from pynwb.file import DynamicTable, NWBFile


class SpontaneousStimuliInterface(BaseDataInterface):
    """Stimulus interface specific to the natural scenes for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        if "spontaneous_stimuli" not in self.v1_nwbfile["stimulus"]["presentation"]:
            return

        spontaneous_stimuli_source = self.v1_nwbfile["stimulus"]["presentation"]["spontaneous_stimuli"]

        spontaneous_stimuli = DynamicTable(
            name="spontaneous_stimuli",
            description="A spontaneous stimuli presented to the subject.",
        )
        # TODO: along with general description; have no idea how to interpret this value...
        spontaneous_stimuli.add_column(name="value", description="A signed value")

        for timestamp, value in zip(spontaneous_stimuli_source["timestamps"][:], spontaneous_stimuli_source["data"][:]):
            spontaneous_stimuli.add_row(start_time=timestamp, value=value)
