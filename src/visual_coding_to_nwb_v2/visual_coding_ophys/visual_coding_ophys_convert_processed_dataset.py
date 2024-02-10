"""Script for parallel conversion of multiple processed sessions of the Visual Coding - Optical Physiology dataset."""

import pathlib
import traceback
import typing
from concurrent.futures import ProcessPoolExecutor, as_completed

import tqdm

import visual_coding_to_nwb_v2


def safe_convert_processed_session(
    session_id: str,
    data_folder_path: typing.Union[str, pathlib.Path],
    output_folder_path: typing.Union[str, pathlib.Path],
    stub_test: bool = False,
):
    """When running in parallel, traceback to stderr per worker is not captured."""
    try:
        visual_coding_to_nwb_v2.visual_coding_ophys.convert_processed_session(
            session_id=session_id,
            data_folder_path=data_folder_path,
            output_folder_path=output_folder_path,
            stub_test=stub_test,
        )
    except Exception as exception:
        log_folder_path = output_folder_path / "logs"
        log_folder_path.mkdir(exist_ok=True)

        with open(file=log_folder_path / f"{session_id}.txt", mode="w") as io:
            io.write(f"{type(exception)}: {str(exception)}\n{traceback.format_exc()}")


if __name__ == "__main__":
    number_of_jobs = 2

    data_folder_path = pathlib.Path("F:/visual-coding/cache/ophys_experiment_data")
    output_folder_path = pathlib.Path("F:/visual-coding/v2_nwbfiles")
    stub_test = False

    futures = list()
    with ProcessPoolExecutor(max_workers=number_of_jobs) as executor:
        for v1_nwbfile_path in data_folder_path.iterdir():
            session_id = v1_nwbfile_path.stem

            futures.append(
                executor.submit(
                    safe_convert_processed_session,
                    session_id=session_id,
                    data_folder_path=data_folder_path,
                    output_folder_path=output_folder_path,
                    stub_test=stub_test,
                )
            )

        for _ in tqdm.tqdm(
            iterable=as_completed(futures), total=len(futures), desc="Converting processed visual coding dataset..."
        ):
            pass
