"""Script for parallel conversion of multiple processed sessions of the Visual Coding - Optical Physiology dataset."""

import json
import os
import pathlib
import shutil
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Union

import natsort
import tqdm
from neuroconv.tools.processes import deploy_process


def _get_completed_session_ids(base_folder_path: Union[str, pathlib.Path]) -> List[str]:
    completed_file_paths = list(base_folder_path.rglob("completed_*.txt"))
    completed_session_ids = [x.name.removeprefix("completed_").removesuffix(".txt") for x in completed_file_paths]
    return completed_session_ids


def _clean_past_sessions(base_folder_path: Union[str, pathlib.Path]):
    base_folder_path = pathlib.Path(base_folder_path)

    completed_session_ids = _get_completed_session_ids(base_folder_path=base_folder_path)
    for completed_session_id in completed_session_ids:
        session_subfolder = base_folder_path / completed_session_id
        shutil.rmtree(path=session_subfolder, ignore_errors=True)

    # remove empty folders too
    for folder_path in base_folder_path.iterdir():
        if folder_path.is_dir() and len(list(folder_path.iterdir())) == 0:
            shutil.rmtree(path=folder_path, ignore_errors=True)


def _safe_convert_raw_session(session_id: str, base_folder_path: Union[str, pathlib.Path]):
    """
    When running in parallel, traceback to stderr per worker is not captured.

    Also, deploying using subprocesses as a way to more easily release file handles for cleanup.
    """
    base_folder_path = pathlib.Path(base_folder_path)

    _clean_past_sessions(base_folder_path=base_folder_path)

    deploy_process(
        command=f"python visual_coding_ophys_download_convert_and_upload_raw_session.py {session_id} {base_folder_path}"
    )


if __name__ == "__main__":
    assert "DANDI_API_KEY" in os.environ
    import dandi  # noqa: To ensure installation before upload attempt

    number_of_jobs = 1

    # base_folder_path = pathlib.Path("/home/jovyan/visual_coding")
    base_folder_path = pathlib.Path("G:/visual_coding")

    session_ids_file_path = base_folder_path / "session_ids.json"
    with open(file=session_ids_file_path, mode="r") as fp:
        all_session_ids = json.load(fp=fp)

    futures = list()
    completed_session_ids = _get_completed_session_ids(base_folder_path=base_folder_path)
    uncompleted_session_ids = natsort.natsorted(list(set(all_session_ids) - set(completed_session_ids)))[:759]
    with ProcessPoolExecutor(max_workers=number_of_jobs) as executor:
        for session_id in uncompleted_session_ids:
            futures.append(
                executor.submit(_safe_convert_raw_session, session_id=session_id, base_folder_path=base_folder_path)
            )

        for _ in tqdm.tqdm(
            iterable=as_completed(futures), total=len(futures), desc="Converting raw visual coding dataset..."
        ):
            pass
