from pathlib import Path

import h5py

base_path = Path("G:/visual-coding/ophys_experiment_data")
v1_nwbfile_paths = base_path.rglob("*.nwb")

all_duplication_testing = list()
for v1_nwbfile_path in v1_nwbfile_paths:
    with h5py.File(name=v1_nwbfile_path, mode="r") as v1_nwbfile:
        ophys_experiment_id = v1_nwbfile["general"]["ophys_experiment_id"][()].decode("utf-8")
        session_id = v1_nwbfile["general"]["ophys_experiment_id"][()].decode("utf-8")
    all_duplication_testing.append((ophys_experiment_id, session_id))

for ophys_experiment_id, session_id in all_duplication_testing:
    assert ophys_experiment_id == session_id
