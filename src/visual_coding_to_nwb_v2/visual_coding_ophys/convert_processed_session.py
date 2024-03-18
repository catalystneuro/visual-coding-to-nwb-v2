"""Primary script for converting a single processed-only session of the Visual Coding - Optical Physiology dataset."""

import pathlib
import typing

import neuroconv

from visual_coding_to_nwb_v2.visual_coding_ophys import VisualCodingOphysNWBConverter


def convert_processed_session(
    session_id: str,
    data_folder_path: typing.Union[str, pathlib.Path],
    output_folder_path: typing.Union[str, pathlib.Path],
    stub_test: bool = False,
) -> None:
    """Convert a single session of the visual coding ophys dataset."""
    data_folder_path = pathlib.Path(data_folder_path)
    output_folder_path = pathlib.Path(output_folder_path)

    if stub_test:
        output_folder_path = output_folder_path / "nwb_stub"
    output_folder_path.mkdir(parents=True, exist_ok=True)

    v1_nwbfile_path = data_folder_path / f"{session_id}.nwb"
    v2_nwbfile_path = output_folder_path / f"ses-{session_id}.nwb"

    # Temporary: skip
    if v2_nwbfile_path.exists():
        return

    # All interfaces take the same common input for this conversion
    source_data = {
        key: dict(v1_nwbfile_path=str(v1_nwbfile_path)) for key in VisualCodingOphysNWBConverter.data_interface_classes
    }

    epoch_table_file_path = data_folder_path.parent / "epoch_tables" / f"{session_id}.json"
    if epoch_table_file_path.exists():
        source_data["Epochs"].update(epoch_table_file_path=str(epoch_table_file_path))
    else:
        del source_data["Epochs"]

    converter = VisualCodingOphysNWBConverter(source_data=source_data)
    metadata = converter.get_metadata()

    with neuroconv.tools.nwb_helpers.make_or_load_nwbfile(
        nwbfile_path=v2_nwbfile_path,
        metadata=metadata,
        overwrite=True,
        verbose=True,
    ) as nwbfile:
        converter.add_to_nwbfile(nwbfile=nwbfile, metadata=metadata)
        default_backend_configuration = neuroconv.tools.nwb_helpers.get_default_backend_configuration(
            nwbfile=nwbfile, backend="hdf5"
        )

        neuroconv.tools.nwb_helpers.configure_backend(
            nwbfile=nwbfile, backend_configuration=default_backend_configuration
        )


if __name__ == "__main__":
    data_folder_path = pathlib.Path("F:/visual-coding/cache/ophys_experiment_data")
    output_folder_path = pathlib.Path("F:/visual-coding/v2_nwbfiles")
    stub_test = False

    # session_id = "496908818"  # Example of natural scenes
    # session_id = "679697901"  # Example of locally sparse
    # session_id = "682051855"  # Example of drifting grating and spontaneous
    # session_id = "501004031"  # With EyeTracking
    session_id = "507691476"  # Investigate missing demixed source

    convert_processed_session(
        session_id=session_id,
        data_folder_path=data_folder_path,
        output_folder_path=output_folder_path,
        stub_test=stub_test,
    )
