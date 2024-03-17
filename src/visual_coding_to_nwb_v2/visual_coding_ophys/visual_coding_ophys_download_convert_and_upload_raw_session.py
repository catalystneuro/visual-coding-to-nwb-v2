"""Primary script for converting a single processed-only session of the Visual Coding - Optical Physiology dataset."""

import os
import pathlib
import shutil
import subprocess
import sys
import traceback
import typing

import neuroconv
from neuroconv.tools.data_transfers import automatic_dandi_upload

from visual_coding_to_nwb_v2.visual_coding_ophys import VisualCodingOphysNWBConverter


def download_convert_and_upload_processed_session(
    session_id: str, base_folder_path: typing.Union[str, pathlib.Path]
) -> None:
    """Convert a single session of the visual coding ophys dataset."""
    assert "DANDI_API_KEY" in os.environ
    import dandi  # noqa: To ensure installation before upload attempt

    try:
        base_folder_path = pathlib.Path(base_folder_path)

        session_subfolder = base_folder_path / session_id
        completed_subfolder = base_folder_path / "completed"
        completed_subfolder.mkdir(exist_ok=True)
        completed_file = completed_subfolder / f"completed_{session_id}.txt"

        source_subfolder = session_subfolder / "source_data"
        source_subfolder.mkdir(exist_ok=True, parents=True)
        v1_nwbfile_path = source_subfolder / f"{session_id}.nwb"
        ophys_movie_file_path = source_subfolder / f"ophys_experiment_{session_id}.h5"

        output_subfolder = session_subfolder / "v2_nwbfile"
        output_subfolder.mkdir(exist_ok=True, parents=True)
        v2_nwbfile_path = output_subfolder / f"ses-{session_id}_desc-raw.nwb"

        if not v1_nwbfile_path.exists():
            subprocess.run(
                [
                    "aws",
                    "s3",
                    "cp",
                    f"s3://allen-brain-observatory/visual-coding-2p/ophys_experiment_data/{v1_nwbfile_path.name}",
                    source_subfolder.absolute(),
                    "--quiet",
                ]
            )
        if not ophys_movie_file_path.exists():
            subprocess.run(
                [
                    "aws",
                    "s3",
                    "cp",
                    f"s3://allen-brain-observatory/visual-coding-2p/ophys_movies/{ophys_movie_file_path.name}",
                    source_subfolder.absolute(),
                    "--quiet",
                ]
            )

        source_data = dict(
            TwoPhotonSeries=dict(
                v1_nwbfile_path=str(v1_nwbfile_path), ophys_movie_file_path=str(ophys_movie_file_path)
            ),
            Metadata=dict(v1_nwbfile_path=str(v1_nwbfile_path)),
        )

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

        shutil.rmtree(path=source_subfolder)

        automatic_dandi_upload(dandiset_id="000728", nwb_folder_path=output_subfolder)

        with open(file=completed_file, mode="w") as io:
            io.write("")
    except Exception as exception:
        log_folder_path = base_folder_path / "logs"
        log_folder_path.mkdir(exist_ok=True)
        with open(file=log_folder_path / f"logs_{session_id}.txt", mode="w") as io:
            io.write(f"{type(exception)}: {str(exception)}\n{traceback.format_exc()}")
    finally:  # In the event of error, or when done, try to clean up for first time
        shutil.rmtree(path=session_subfolder)


if __name__ == "__main__":
    session_id = "712919679"
    # base_folder_path = pathlib.Path("F:/visual_coding/test")
    base_folder_path = pathlib.Path("/home/jovyan/visual_coding/")

    if len(sys.argv) > 1:  # CLI usage
        session_id = sys.argv[1]
        base_folder_path = sys.argv[2]

    download_convert_and_upload_processed_session(
        session_id=session_id,
        base_folder_path=base_folder_path,
    )
