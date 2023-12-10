from pathlib import Path

import h5py

base_path = Path("G:/visual-coding/ophys_experiment_data")

v1_nwbfiles = list(base_path.rglob("*.nwb"))

all_specimen_names_and_genotypes = list()
for v1_nwbfile in v1_nwbfiles:
    file = h5py.File(name=v1_nwbfile, mode="r")

    all_specimen_names_and_genotypes.append(
        (
            file["general"]["specimen_name"][()].decode("utf-8"),
            file["general"]["subject"]["genotype"][()].decode("utf-8"),
        )
    )

all_unique_specimen_names = list(set([x[0] for x in all_specimen_names_and_genotypes]))
all_unique_genotypes = list(set([x[1] for x in all_specimen_names_and_genotypes]))
all_unique_pairs = list(set(all_specimen_names_and_genotypes))
