from pathlib import Path

import h5py

base_path = Path("G:/visual-coding/ophys_experiment_data")
v1_nwbfile_paths = base_path.rglob("*.nwb")

all_duplication_testing = list()
for v1_nwbfile_path in v1_nwbfile_paths:
    with h5py.File(name=v1_nwbfile_path, mode="r") as v1_nwbfile:
        targeted_structure = v1_nwbfile["general"]["targeted_structure"][()].decode("utf-8")
        imaging_plane_location = v1_nwbfile["general"]["optophysiology"]["imaging_plane_1"]["location"][()].decode(
            "utf-8"
        )
    all_duplication_testing.append((targeted_structure, imaging_plane_location))

for targeted_structure, imaging_plane_location in all_duplication_testing:
    assert targeted_structure == imaging_plane_location
