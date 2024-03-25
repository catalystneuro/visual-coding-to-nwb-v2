"""
In the October 2018 data release, they added an AllenSDK method for additional data not contained in the NWB files.

In particular, this is for 'events' identified from the DFOverF traces using an L0 method.

Note that not all sessions have events classified. 1413 sessions have it.
"""

import pathlib

import numpy
from allensdk.core.brain_observatory_cache import BrainObservatoryCache

ophys_experiment_base_folder = pathlib.Path("F:/visual_coding/cache/ophys_experiment_data")
session_ids = [int(file.stem) for file in ophys_experiment_base_folder.rglob("*.nwb")]

manifest_file = pathlib.Path("F:/visual_coding/cache/manifest.json")
brain_observatory_cache = BrainObservatoryCache(manifest_file=manifest_file)

df_over_f_events_folder = pathlib.Path("F:/visual_coding/cache/df_over_f_events")
df_over_f_events_folder.mkdir(exist_ok=True)
for session_id in session_ids:
    try:
        df_over_f_events = brain_observatory_cache.get_ophys_experiment_events(ophys_experiment_id=session_id).T

        df_over_f_events_file_path = df_over_f_events_folder / f"{session_id}.npy"
        if df_over_f_events_file_path.exists():
            continue

        numpy.save(file=df_over_f_events_file_path, arr=df_over_f_events)
    except Exception as exception:
        # Cannot figure out how to properly import this error class...
        if type(exception).__name__ == "Exception" and "has no events file" in str(exception):
            print(f"Skipping session {session_id} due to missing events!")
            continue
        else:
            raise exception
