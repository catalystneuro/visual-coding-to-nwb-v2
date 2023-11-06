import json
from pathlib import Path
from collections import defaultdict

import h5py

base_path = Path("G:/visual-coding/ophys_experiment_data")
v1_nwbfile_paths = base_path.rglob("*.nwb")

all_duplication_testing = list()
for v1_nwbfile_path in v1_nwbfile_paths:
    with h5py.File(name=v1_nwbfile_path, mode="r") as v1_nwbfile:
        ophys_experiment_name = v1_nwbfile["general"]["ophys_experiment_name"][()].decode("utf-8")
        session_type = v1_nwbfile["general"]["session_type"][()].decode("utf-8")
    all_duplication_testing.append((ophys_experiment_name, session_type))

unique_session_types = defaultdict(list)
for ophys_experiment_name, session_type in all_duplication_testing:
    unique_session_types[session_type].append(ophys_experiment_name)


unique_stripped_experiment_names = defaultdict(list)
for ophys_experiment_name, _ in all_duplication_testing:
    experiment_name_split = ophys_experiment_name.split("_")

    number_of_parts = len(experiment_name_split)  # Huge variability here...
    descriptor_point = min(number_of_parts - 1, 2)

    session_id = "_".join(experiment_name_split[:descriptor_point])
    session_descriptor = "_".join(experiment_name_split[descriptor_point:])
    unique_stripped_experiment_names[session_descriptor].append(session_id)

with open(Path(__file__).parent / "stripped_experiment_names.json", mode="w") as io:
    json.dump(obj=unique_stripped_experiment_names, fp=io, indent=4)
