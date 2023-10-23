"""Primary class for pupil data."""
from pathlib import Path
from datetime import datetime

import h5py
from pynwb.file import NWBFile
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.utils import DeepDict


class VisualCodingPupilInterface(BaseDataInterface):
    """Pupil tracking interface for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: Path):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        with h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r") as v1_nwbfile:
            pass
