"""Primary class for running speed data."""

import h5py
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module
from pynwb import TimeSeries
from pynwb.behavior import BehavioralTimeSeries
from pynwb.file import NWBFile


class RunningSpeedInterface(BaseDataInterface):
    """Running speed interface for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        processing_source = self.v1_nwbfile["processing"]["brain_observatory_pipeline"]
        if (
            "BehavioralTimeSeries" not in processing_source
            or "running_speed" not in processing_source["BehavioralTimeSeries"]
        ):
            return
        running_speed_source = processing_source["BehavioralTimeSeries"]["running_speed"]

        # x, y grid
        running_speed_data = running_speed_source["data"][:]
        running_speed_timestamps = running_speed_source["timestamps"][:]

        running_speed_time_series = TimeSeries(
            name="running_speed",
            description=(
                "Velocity of the subject over time. Mice were positioned on a running disk during the imaging "
                "sessions, and a magnetic shaft encoder (US Digital) attached to this disk recorded the running speed "
                "of the mouse during the experiment at 60 samples per second. The running speed was down-sampled to "
                "match the timing of the 2-photon imaging (30 Hz)."
            ),
            data=running_speed_data,
            timestamps=running_speed_timestamps,
            unit="cm/s",  # Note, original data said 'frame' but SDK docs said 'cm/s' and did not modify source
        )
        behavioral_time_series = BehavioralTimeSeries(time_series=running_speed_time_series)

        behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="Processed behavioral data.")
        behavior_module.add(behavioral_time_series)
