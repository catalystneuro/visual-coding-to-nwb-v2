"""Script for parallel conversion of multiple processed sessions of the Visual Coding - Optical Physiology dataset."""

import json
import os
import pathlib
import shutil
from typing import List, Union

import natsort
import tqdm
from dandi.dandiapi import DandiAPIClient

from visual_coding_to_nwb_v2.visual_coding_ophys import (
    safe_download_convert_and_upload_raw_session,
)


def _get_completed_session_ids(base_folder_path: Union[str, pathlib.Path]) -> List[str]:
    # Previous implementation using local files
    # completed_file_paths = list(base_folder_path.rglob("completed_*.txt"))
    # completed_session_ids = [x.name.removeprefix("completed_").removesuffix(".txt") for x in completed_file_paths]

    client = DandiAPIClient()

    dandiset_id = "000728"
    dandiset = client.get_dandiset(dandiset_id=dandiset_id)

    completed_session_ids = [
        asset.path.split("_")[1].split("-")[1] for asset in dandiset.get_assets() if "behavior" not in asset.path
    ]

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


if __name__ == "__main__":
    assert "DANDI_API_KEY" in os.environ

    if "jovyan" in str(pathlib.Path.cwd()):
        base_folder_path = pathlib.Path("/home/jovyan/visual_coding")
        slice_range = slice(759, None)
    else:
        # base_folder_path = pathlib.Path("G:/visual_coding")
        # slice_range = slice(0, 500)

        # base_folder_path = pathlib.Path("E:/visual_coding")
        # slice_range = slice(500, 1_000)

        base_folder_path = pathlib.Path("F:/visual_coding/raw")
        slice_range = slice(1_000, None)

    # session_ids_file_path = base_folder_path / "session_ids.json"
    # with open(file=session_ids_file_path, mode="r") as fp:
    #     all_session_ids = json.load(fp=fp)

    client = DandiAPIClient()

    dandiset_id = "000728"
    dandiset = client.get_dandiset(dandiset_id=dandiset_id)

    all_session_ids = [
        asset.path.split("_")[1].split("-")[1] for asset in dandiset.get_assets() if "behavior" in asset.path
    ]

    completed_session_ids = _get_completed_session_ids(base_folder_path=base_folder_path)
    uncompleted_session_ids = natsort.natsorted(list(set(all_session_ids) - set(completed_session_ids)))[slice_range]
    for uncompleted_session_id in tqdm.tqdm(
        iterable=uncompleted_session_ids,
        total=len(uncompleted_session_ids),
        desc="Converting raw visual coding dataset...",
    ):
        _clean_past_sessions(base_folder_path=base_folder_path)
        safe_download_convert_and_upload_raw_session(
            session_id=uncompleted_session_id, base_folder_path=base_folder_path, log=False
        )
