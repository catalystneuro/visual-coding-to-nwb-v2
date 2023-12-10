from pathlib import Path

import h5py

base_path = Path("F:/visual-coding/ophys_experiment_data")

v1_nwbfiles = list(base_path.rglob("*.nwb"))

all_excitation_and_emission_lambdas = list()
for v1_nwbfile in v1_nwbfiles:
    file = h5py.File(name=v1_nwbfile, mode="r")

    all_excitation_and_emission_lambdas.append(
        (
            file["general"]["optophysiology"]["imaging_plane_1"]["excitation_lambda"][()].decode("utf-8"),
            file["general"]["optophysiology"]["imaging_plane_1"]["channel-1"]["emission_lambda"][()].decode("utf-8"),
        )
    )

all_unique_excitation = list(set([x[0] for x in all_excitation_and_emission_lambdas]))
all_unique_emission = list(set([x[1] for x in all_excitation_and_emission_lambdas]))
all_unique_excitation_and_emission_pairs = list(set(all_excitation_and_emission_lambdas))
