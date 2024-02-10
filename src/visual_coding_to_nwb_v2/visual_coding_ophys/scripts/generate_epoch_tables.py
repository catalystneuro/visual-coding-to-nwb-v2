"""
The source files have an 'epoch' group but it is generally empty and not a table as shown through the AllenSDK.

Instead, the AllenSDK calculates it through a complicated procedure.

Reference: https://github.com/AllenInstitute/AllenSDK/blob/a9b5c685396126d9748f1ccecf7c00f440569f69/allensdk/core/brain_observatory_nwb_data_set.py#L156

Due to incompatabilies in secondary packages between HDMF and the AllenSDK, it is recommended to run this script
in a separate environment, store the results, and use those in the conversion process.
"""

import json
import pathlib

from allensdk.core.brain_observatory_cache import BrainObservatoryCache

ophys_experiment_base_folder = pathlib.Path("F:/visual-coding/cache/ophys_experiment_data")
session_ids = [int(file.stem) for file in ophys_experiment_base_folder.rglob("*.nwb")]

manifest_file = pathlib.Path("F:/visual-coding/cache/manifest.json")
brain_observatory_cache = BrainObservatoryCache(manifest_file=manifest_file)

epoch_table_folder = pathlib.Path("F:/visual-coding/cache/epoch_tables")
epoch_table_folder.mkdir(exist_ok=True)
for session_id in session_ids:
    data_set = brain_observatory_cache.get_ophys_experiment_data(ophys_experiment_id=session_id)

    # The `get_stimulus_epoch_table` method occasionally fails due to 'more than X epochs cut'
    try:
        epoch_table_file_path = epoch_table_folder / f"{session_id}.json"
        if epoch_table_file_path.exists():
            continue

        stim_epoch = data_set.get_stimulus_epoch_table()
        stim_epoch_json = {column_name: stim_epoch[column_name].values.tolist() for column_name in stim_epoch}

        with open(file=epoch_table_file_path, mode="w") as io:
            json.dump(obj=stim_epoch_json, fp=io, indent=4)
    except Exception as exception:
        # Cannot figure out how to properly import this error class...
        if type(exception).__name__ == "EpochSeparationException":
            print(f"Skipping session {session_id} due to problem calculating epochs table!")
            continue
        else:
            raise Exception
