"""Primary class for running speed data."""
from pathlib import Path

import h5py
from pynwb import H5DataIO, TimeSeries
from pynwb.file import NWBFile
from pynwb.behavior import BehavioralTimeSeries
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module


class RunningSpeedInterface(BaseDataInterface):
    """Running speed interface for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: Path):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        with h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r") as v1_nwbfile:
            processing_source = v1_nwbfile["processing"]["brain_observatory_pipeline"]
            running_speed_source = processing_source["BehavioralTimeSeries"]["running_speed"]

            # x, y grid
            running_speed_data = running_speed_source["data"]
            max_frames_per_chunk = int(10e6 / running_speed_data.dtype.itemsize)
            data_chunks = min(running_speed_data.shape[0], max_frames_per_chunk)

            running_speed_timestamps = running_speed_source["timestamps"]
            timestamp_chunks = min(
                running_speed_timestamps.shape[0], int(10e6 / running_speed_timestamps.dtype.itemsize)
            )

            running_speed_time_series = list(
                TimeSeries(
                    name="running_speed",
                    description="Velocity of the running wheel.",
                    data=H5DataIO(data=running_speed_data, compression=True, chunks=data_chunks),
                    timestamps=H5DataIO(data=running_speed_timestamps, compression=True, chunks=timestamp_chunks),
                    unit="cm/s",  # Note, original data said 'frame' but SDK docs said 'cm/s' and did not modify source
                )
            )
            behavioral_time_series = BehavioralTimeSeries(spatial_series=running_speed_time_series)

            behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="Processed behavioral data.")
            behavior_module.add(behavioral_time_series)
