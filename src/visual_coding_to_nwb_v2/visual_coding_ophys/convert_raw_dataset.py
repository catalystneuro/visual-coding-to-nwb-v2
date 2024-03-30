"""Script for parallel conversion of multiple processed sessions of the Visual Coding - Optical Physiology dataset."""

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
        pause_file_path = pathlib.Path("G:/visual_coding/pause.txt")

        # base_folder_path = pathlib.Path("G:/visual_coding")
        # slice_range = slice(0, 150)

        # base_folder_path = pathlib.Path("E:/visual_coding")
        # slice_range = slice(150, 300)

        # base_folder_path = pathlib.Path("F:/visual_coding/raw")
        # slice_range = slice(300, 450)

        base_folder_path = pathlib.Path("D:/visual_coding")
        slice_range = slice(450, 600)

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
