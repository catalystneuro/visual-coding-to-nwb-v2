"""
The demo notebook uses several commands in the AllenSDK to add some summary information about the experiment as a whole.

Due to incompatabilies in secondary packages between HDMF and the AllenSDK, it is recommended to run this script
in a separate environment, store the results, and use those in the conversion process.

Much of this could technically be scrubbed from the NWB files.

For now, these outputs will simply be bundled with the example notebooks. Going forward, I'll try to document how I'd
prefer that it be a part of the DANDI metadata files (might require some 'extra' fields).
"""

import json
import pathlib

from allensdk.core.brain_observatory_cache import BrainObservatoryCache

brain_observatory_metadata_folder_path = pathlib.Path("F:/visual-coding/notebooks/asset_metadata")
brain_observatory_metadata_folder_path.mkdir(exist_ok=True)

manifest_file = pathlib.Path("F:/visual-coding/cache/manifest.json")
brain_observatory_cache = BrainObservatoryCache(manifest_file=manifest_file)

experiments_containers = brain_observatory_cache.get_experiment_containers()
sessions = brain_observatory_cache.get_ophys_experiments()

# This technically only gives 1368 sessions but there should be 1518 total
# So pre-cached summary metadata via AllenSDK is not always available
# This is also confirmed by directly comparing the'id' between the ophys_experiment_data and the ones here
visual_coding_sessions = [x for x in sessions if "three_session" in x["session_type"]]


# Container call can be subset in the following way
# experiments_subset = brain_observatory_cache.get_experiment_containers(
#     targeted_structures=["VISp"],
#     cre_lines=["Cux2-CreERT2"],
# )

# These fields are in the API but are immediately derivable from the visual_coding_sessions
# all_stimuli = brain_observatory_cache.get_all_stimuli()
# all_session_types = brain_observatory_cache.get_all_session_types()


# These fields are in the API but are immediately derivable from the experiment containers
# all_targeted_structures = brain_observatory_cache.get_all_targeted_structures()
# all_cre_lines = brain_observatory_cache.get_all_cre_lines()
# all_reporter_lines = brain_observatory_cache.get_all_reporter_lines()

experiment_containers_json_file_path = brain_observatory_metadata_folder_path / "experiment_containers_metadata.json"
visual_coding_sessions_json_file_path = brain_observatory_metadata_folder_path / "visual_coding_sessions_metadata.json"
with open(file=experiment_containers_json_file_path, mode="w") as fp:
    json.dump(obj=experiments_containers, fp=fp, indent=4)
with open(file=visual_coding_sessions_json_file_path, mode="w") as fp:
    json.dump(obj=visual_coding_sessions, fp=fp, indent=4)
