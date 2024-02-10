"""Primary class for stimulus data specific to drifting gratings."""

import json

import h5py
from neuroconv.basedatainterface import BaseDataInterface
from pynwb.file import NWBFile, TimeIntervals


class EpochsInterface(BaseDataInterface):
    """Stimulus interface specific to the natural scenes for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str, epoch_table_file_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path, epoch_table_file_path=epoch_table_file_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        with open(file=self.source_data["epoch_table_file_path"], mode="r") as io:
            epochs_table_json = json.load(fp=io)

        # The 'start' and 'end' values in this JSON file are the frame indices aligned to the ophys
        # So without loss of generality, choose them to come from the DfOverF
        source_ophys_module = self.v1_nwbfile["processing"]["brain_observatory_pipeline"]
        ophys_timestamps = source_ophys_module["DfOverF"]["imaging_plane_1"]["timestamps"][:]

        epoch_table = TimeIntervals(
            name="epochs",
            description="Coarse grain experiment structure in the alternating presentations of visual stimuli.",
        )
        epoch_table.add_column(name="stimulus_type", description="Type of visual stimuli.")

        for start_frame, stop_frame, stimulus_type in zip(
            epochs_table_json["start"], epochs_table_json["end"], epochs_table_json["stimulus"]
        ):
            epoch_table.add_interval(
                start_time=ophys_timestamps[start_frame],
                stop_time=ophys_timestamps[stop_frame],
                stimulus_type=stimulus_type,
            )

        nwbfile.epochs = epoch_table
