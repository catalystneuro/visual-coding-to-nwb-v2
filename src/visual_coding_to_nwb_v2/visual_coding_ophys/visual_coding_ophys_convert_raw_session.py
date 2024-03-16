"""Primary script for converting a single processed-only session of the Visual Coding - Optical Physiology dataset."""

import pathlib
import typing

import neuroconv

from visual_coding_to_nwb_v2.visual_coding_ophys import VisualCodingOphysNWBConverter


def convert_processed_session(
    session_id: str,
    processed_data_folder_path: typing.Union[str, pathlib.Path],
    raw_data_folder_path: typing.Union[str, pathlib.Path],
    output_folder_path: typing.Union[str, pathlib.Path],
    stub_test: bool = False,
) -> None:
    """Convert a single session of the visual coding ophys dataset."""
    processed_data_folder_path = pathlib.Path(processed_data_folder_path)
    raw_data_folder_path = pathlib.Path(raw_data_folder_path)
    output_folder_path = pathlib.Path(output_folder_path)

    if stub_test:
        output_folder_path = output_folder_path / "nwb_stub"
    output_folder_path.mkdir(parents=True, exist_ok=True)

    v1_nwbfile_path = processed_data_folder_path / f"{session_id}.nwb"
    ophys_movie_file_path = raw_data_folder_path / f"ophys_experiment_{session_id}.h5"

    v2_nwbfile_path = output_folder_path / f"ses-{session_id}_desc-raw.nwb"

    source_data = dict(
        TwoPhotonSeries=dict(v1_nwbfile_path=str(v1_nwbfile_path), ophys_movie_file_path=str(ophys_movie_file_path)),
        Metadata=dict(v1_nwbfile_path=str(v1_nwbfile_path)),
    )

    converter = VisualCodingOphysNWBConverter(source_data=source_data)
    metadata = converter.get_metadata()

    conversion_options = dict(TwoPhotonSeries=dict(stub_test=stub_test))
    with neuroconv.tools.nwb_helpers.make_or_load_nwbfile(
        nwbfile_path=v2_nwbfile_path,
        metadata=metadata,
        overwrite=True,
        verbose=False,
    ) as nwbfile:
        converter.add_to_nwbfile(nwbfile=nwbfile, metadata=metadata, conversion_options=conversion_options)
        default_backend_configuration = neuroconv.tools.nwb_helpers.get_default_backend_configuration(
            nwbfile=nwbfile, backend="hdf5"
        )

        neuroconv.tools.nwb_helpers.configure_backend(
            nwbfile=nwbfile, backend_configuration=default_backend_configuration
        )


if __name__ == "__main__":
    processed_data_folder_path = pathlib.Path("F:/visual_coding/cache/ophys_experiment_data")
    raw_data_folder_path = pathlib.Path("F:/visual_coding/ophys_movies")
    output_folder_path = pathlib.Path("F:/visual_coding/v2_nwbfiles")
    stub_test = False

    session_id = "571099190"

    convert_processed_session(
        session_id=session_id,
        processed_data_folder_path=processed_data_folder_path,
        raw_data_folder_path=raw_data_folder_path,
        output_folder_path=output_folder_path,
        stub_test=stub_test,
    )
