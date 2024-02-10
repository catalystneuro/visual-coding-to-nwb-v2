"""Primary class for pupil tracking data."""

import h5py
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module
from pynwb.base import TimeSeries
from pynwb.behavior import PupilTracking
from pynwb.file import NWBFile

from .shared_methods import add_eye_tracking_device


class PupilTrackingInterface(BaseDataInterface):
    """Pupil tracking interface for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        if "Camera" not in nwbfile.devices:
            add_eye_tracking_device(nwbfile=nwbfile)

        processing_source = self.v1_nwbfile["processing"]["brain_observatory_pipeline"]
        if "PupilTracking" not in processing_source:
            return
        pupil_size_data = processing_source["PupilTracking"]["pupil_size"]["data"][:]
        pupil_size_timestamps = self.v1_nwbfile["processing"]["brain_observatory_pipeline"]["PupilTracking"][
            "pupil_size"
        ]["timestamps"][:]

        pupil_time_series = TimeSeries(
            name="pupil_size",
            description="Size of pupil dilation in units pixels.",
            data=pupil_size_data,
            timestamps=pupil_size_timestamps,
            unit="px",
        )
        pupil_tracking = PupilTracking(time_series=[pupil_time_series])

        behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="Processed behavioral data.")
        behavior_module.add(pupil_tracking)
