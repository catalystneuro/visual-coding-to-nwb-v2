"""Primary script for converting a single processed-only session of the Visual Coding - Optical Physiology dataset."""

import os
import pathlib
import shutil
import sys
import time
import traceback
from typing import Union

import boto3
import h5py
import neuroconv
from botocore import UNSIGNED
from botocore.client import Config
from neuroconv.tools.data_transfers import automatic_dandi_upload

from visual_coding_to_nwb_v2.visual_coding_ophys import VisualCodingOphysNWBConverter

# Every real session of this dataset is on the order of 100,000 frames; `stub_test=True` writes 10.
MINIMUM_PLAUSIBLE_NUMBER_OF_FRAMES = 10_000


def _check_for_pause(pause_file_path: Union[pathlib.Path, None] = None) -> None:
    if pause_file_path is None:
        return

    while pause_file_path.exists():
        time.sleep(60)


def _validate_raw_nwbfile(v2_nwbfile_path: pathlib.Path, expected_number_of_frames: Union[int, None] = None) -> None:
    """
    Ensure the converted file holds the complete recording before it is uploaded.

    Without this, a `stub_test=True` run silently uploads a 10-frame file that is
    indistinguishable from a real one by path alone.
    See https://github.com/dandi/helpdesk/discussions/209

    When the source movie is still on disk, pass its frame count as `expected_number_of_frames` for an
    exact check. When resuming an upload the source is already cleaned up, so fall back to rejecting
    anything implausibly short; real sessions in this dataset run to roughly 100,000 frames.
    """
    with h5py.File(name=v2_nwbfile_path, mode="r") as nwbfile:
        number_of_frames = nwbfile["acquisition"]["MotionCorrectedTwoPhotonSeries"]["data"].shape[0]
        number_of_shifts = nwbfile["acquisition"]["MotionCorrectionShiftsPerFrame"]["data"].shape[0]

    if number_of_shifts != number_of_frames:
        raise RuntimeError(
            f"Refusing to upload {v2_nwbfile_path.name}: {number_of_frames} imaging frames but "
            f"{number_of_shifts} motion correction shifts."
        )

    if expected_number_of_frames is not None and number_of_frames != expected_number_of_frames:
        raise RuntimeError(
            f"Refusing to upload {v2_nwbfile_path.name}: found {number_of_frames} frames, but the "
            f"source movie has {expected_number_of_frames}. This looks like a stub conversion."
        )

    if expected_number_of_frames is None and number_of_frames < MINIMUM_PLAUSIBLE_NUMBER_OF_FRAMES:
        raise RuntimeError(
            f"Refusing to upload {v2_nwbfile_path.name}: only {number_of_frames} frames, which is "
            f"below the {MINIMUM_PLAUSIBLE_NUMBER_OF_FRAMES} expected of any real session. "
            "This looks like a stub conversion."
        )


def safe_download_convert_and_upload_raw_session(
    session_id: str,
    base_folder_path: Union[str, pathlib.Path],
    log: bool = True,
    pause_file_path: Union[pathlib.Path, None] = None,
) -> None:
    """Convert a single session of the visual coding ophys dataset."""
    assert "DANDI_API_KEY" in os.environ
    import dandi  # noqa: To ensure installation before upload attempt

    try:
        base_folder_path = pathlib.Path(base_folder_path)

        session_subfolder = base_folder_path / session_id

        source_subfolder = session_subfolder / "source_data"
        source_subfolder.mkdir(exist_ok=True, parents=True)
        v1_nwbfile_path = source_subfolder / f"{session_id}.nwb"
        ophys_movie_file_path = source_subfolder / f"ophys_experiment_{session_id}.h5"

        output_subfolder = session_subfolder / "v2_nwbfile"
        output_subfolder.mkdir(exist_ok=True, parents=True)
        v2_nwbfile_path = output_subfolder / f"ses-{session_id}_desc-raw.nwb"

        _check_for_pause(pause_file_path=pause_file_path)

        if v2_nwbfile_path.exists():
            _validate_raw_nwbfile(v2_nwbfile_path=v2_nwbfile_path)
            automatic_dandi_upload(dandiset_id="000728", nwb_folder_path=output_subfolder)
            return

        if not v1_nwbfile_path.exists():
            s3 = boto3.resource("s3", region_name="us-west-2", config=Config(signature_version=UNSIGNED))
            bucket = s3.Bucket(name="allen-brain-observatory")
            bucket.download_file(
                Key=f"visual-coding-2p/ophys_experiment_data/{v1_nwbfile_path.name}",
                Filename=source_subfolder / v1_nwbfile_path.name,
            )

        if not ophys_movie_file_path.exists():
            s3 = boto3.resource("s3", region_name="us-west-2", config=Config(signature_version=UNSIGNED))
            bucket = s3.Bucket(name="allen-brain-observatory")
            bucket.download_file(
                Key=f"visual-coding-2p/ophys_movies/{ophys_movie_file_path.name}",
                Filename=source_subfolder / ophys_movie_file_path.name,
            )

        _check_for_pause(pause_file_path=pause_file_path)

        source_data = dict(
            TwoPhotonSeries=dict(
                v1_nwbfile_path=str(v1_nwbfile_path), ophys_movie_file_path=str(ophys_movie_file_path)
            ),
            Metadata=dict(v1_nwbfile_path=str(v1_nwbfile_path)),
        )

        with h5py.File(name=ophys_movie_file_path, mode="r") as ophys_movie:
            expected_number_of_frames = ophys_movie["data"].shape[0]

        converter = VisualCodingOphysNWBConverter(source_data=source_data, verbose=False)
        metadata = converter.get_metadata()

        with neuroconv.tools.nwb_helpers.make_or_load_nwbfile(
            nwbfile_path=v2_nwbfile_path, metadata=metadata, overwrite=True, verbose=False
        ) as nwbfile:
            converter.add_to_nwbfile(nwbfile=nwbfile, metadata=metadata)
            default_backend_configuration = neuroconv.tools.nwb_helpers.get_default_backend_configuration(
                nwbfile=nwbfile, backend="hdf5"
            )

            neuroconv.tools.nwb_helpers.configure_backend(
                nwbfile=nwbfile, backend_configuration=default_backend_configuration
            )

        _validate_raw_nwbfile(v2_nwbfile_path=v2_nwbfile_path, expected_number_of_frames=expected_number_of_frames)

        shutil.rmtree(path=source_subfolder, ignore_errors=True)

        _check_for_pause(pause_file_path=pause_file_path)

        automatic_dandi_upload(dandiset_id="000728", nwb_folder_path=output_subfolder)
    except Exception as exception:
        if log:
            log_folder_path = base_folder_path / "logs"
            log_folder_path.mkdir(exist_ok=True)
            with open(file=log_folder_path / f"logs_{session_id}.txt", mode="w") as io:
                io.write(f"{type(exception)}: {str(exception)}\n{traceback.format_exc()}")
        else:
            raise exception
    finally:  # In the event of error, or when done, try to clean up for first time
        shutil.rmtree(path=session_subfolder, ignore_errors=True)


if __name__ == "__main__":
    # Deliberately no default session ID: this script ends in an upload to a published dandiset, and a
    # hardcoded test session (712919679) is how a stub file reached the archive in the first place.
    # See https://github.com/dandi/helpdesk/discussions/209
    if len(sys.argv) < 3:
        raise SystemExit(f"usage: python {pathlib.Path(sys.argv[0]).name} <session_id> <base_folder_path>")

    session_id = sys.argv[1]
    base_folder_path = pathlib.Path(sys.argv[2])

    safe_download_convert_and_upload_raw_session(
        session_id=session_id,
        base_folder_path=base_folder_path,
        log=False,
    )
