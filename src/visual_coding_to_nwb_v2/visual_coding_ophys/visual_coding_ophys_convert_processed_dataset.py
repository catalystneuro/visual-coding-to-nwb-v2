"""Primary script to run to convert an entire session for of data using the NWBConverter."""

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from traceback import format_exc
from typing import Union

from tqdm import tqdm

from visual_coding_to_nwb_v2.visual_coding_ophys.visual_coding_ophys_convert_session import (
    convert_session,
)


def safe_convert_session(
    session_id: str, data_folder_path: Union[str, Path], output_folder_path: Union[str, Path], stub_test: bool = False
):
    """When running in parallel, traceback to stderr per worker is not captured."""
    try:
        convert_session(
            session_id=session_id,
            data_folder_path=data_folder_path,
            output_folder_path=output_folder_path,
            stub_test=stub_test,
        )
    except Exception as exception:
        log_folder_path = output_folder_path.parent / "logs"
        log_folder_path.mkdir(exist_ok=True)

        with open(file=log_folder_path / f"{session_id}.txt", mode="w") as io:
            io.write(f"{type(exception): str(exceeption)\n{format_exc()}}")


if __name__ == "__main__":
    number_of_jobs = 2

    data_folder_path = Path("F:/visual-coding/cache/ophys_experiment_data")
    output_folder_path = Path("F:/visual-coding/v2_nwbfiles")
    stub_test = False

    futures = list()
    with ProcessPoolExecutor(max_workers=number_of_jobs) as executor:
        for v1_nwbfile_path in data_folder_path.iterdir():
            session_id = v1_nwbfile_path.stem

            futures.append(
                executor.submit(
                    convert_session,
                    session_id=session_id,
                    data_folder_path=data_folder_path,
                    output_folder_path=output_folder_path,
                    stub_test=stub_test,
                )
            )

        for _ in tqdm(
            iterable=as_completed(futures), total=len(futures), desc="Converting processed visual coding dataset..."
        ):
            pass
