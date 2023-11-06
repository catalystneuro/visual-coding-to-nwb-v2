"""Primary class for pupil data."""
from pathlib import Path

import h5py
from pynwb import H5DataIO
from pynwb.file import NWBFile
from pynwb.base import TimeSeries
from pynwb.behavior import PupilTracking
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module


class VisualCodingPupilInterface(BaseDataInterface):
    """Pupil tracking interface for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: Path):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        with h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r") as v1_nwbfile:
            pupil_size_data = v1_nwbfile["processing"]["brain_observatory_pipeline"]["PupilTracking"]["pupil_size"][
                "data"
            ]
            pupil_size_timestamps = v1_nwbfile["processing"]["brain_observatory_pipeline"]["PupilTracking"][
                "pupil_size"
            ]["timestamps"]
            data_chunks = min(pupil_size_data.shape[0], int(10e6 // pupil_size_data.dtype.itemsize))
            timestamps_chunks = min(pupil_size_timestamps.shape[0], int(10e6 // pupil_size_timestamps.dtype.itemsize))

            pupil_time_series = list(
                TimeSeries(
                    name="pupil_size",
                    description="Size of pupil dilation in units pixels.",
                    data=H5DataIO(data=pupil_size_data, compression=True, chunks=data_chunks),
                    timestamps=H5DataIO(data=pupil_size_timestamps, compression=True, chunks=timestamps_chunks),
                    unit="px",
                )
            )
            pupil_tracking = PupilTracking(time_series=pupil_time_series)

            behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="Processed behavioral data.")
            behavior_module.add(pupil_tracking)