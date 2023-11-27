from pathlib import Path
from collections import defaultdict
from typing import Union, List

import h5py
from natsort.natsort import natsorted

SKIP_KEYS = ["timeseries", "corrected", "original"]
ABBREVIATE_KEYS = ["imaging_plane_1"]


def _recurse_structure(dataset_list: list, group: h5py.Group, key: Union[str, None]):
    if isinstance(group[key], h5py.Group):
        next_group = group[key]
        for next_key in next_group:
            if next_key in SKIP_KEYS:
                continue
            if next_key in ABBREVIATE_KEYS:
                dataset_list.append(next_group.name)
                continue
            _recurse_structure(dataset_list=dataset_list, group=next_group, key=next_key)
    else:
        dataset_list.append(group[key].name)  # Is the full path within the HDF5 file, including '/'


def _find_all_datasets(file: h5py.File) -> List[str]:
    dataset_list = list()
    for key in file:
        _recurse_structure(dataset_list=dataset_list, group=file, key=key)
    return dataset_list


base_path = Path("G:/visual-coding/ophys_experiment_data")

v1_nwbfiles = list(base_path.rglob("*.nwb"))

datasets_per_file = defaultdict(list)
for v1_nwbfile in v1_nwbfiles:
    file = h5py.File(name=v1_nwbfile, mode="r")

    datasets_per_file[v1_nwbfile] = _find_all_datasets(file=file)

all_datasets = list()
for datasets in datasets_per_file.values():
    all_datasets.extend(datasets)

unique_datasets = natsorted(list(set(all_datasets)))

# import json
# print(json.dumps(unique_datasets, indent=4))

unique_counts = {key: 0 for key in unique_datasets}
for datasets in datasets_per_file.values():
    for dataset in datasets:
        unique_counts[dataset] += 1
