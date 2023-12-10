"""Primary script to run to convert an entire session for of data using the NWBConverter."""
from pathlib import Path
from typing import Union

from visual_coding_to_nwb_v2.visual_coding_ophys import VisualCodingOphysNWBConverter

# from neuroconv.tools.nwb_helpers import


def convert_session(
    session_id: str, data_folder_path: Union[str, Path], output_folder_path: Union[str, Path], stub_test: bool = False
):
    data_folder_path = Path(data_folder_path)
    output_folder_path = Path(output_folder_path)

    if stub_test:
        output_folder_path = output_folder_path / "nwb_stub"
    output_folder_path.mkdir(parents=True, exist_ok=True)

    v1_nwbfile_path = data_folder_path / f"{session_id}.nwb"
    v2_nwbfile_path = output_folder_path / f"ses-{session_id}.nwb"

    source_data = {
        key: dict(v1_nwbfile_path=str(v1_nwbfile_path)) for key in VisualCodingOphysNWBConverter.data_interface_classes
    }

    converter = VisualCodingOphysNWBConverter(source_data=source_data)
    converter.run_conversion(nwbfile_path=str(v2_nwbfile_path), overwrite=True)


if __name__ == "__main__":
    # Parameters for conversion
    data_folder_path = Path("F:/visual-coding/ophys_experiment_data")
    output_folder_path = Path("F:/visual-coding/v2_nwbfiles")
    stub_test = False

    # session_id = "496908818"
    session_id = "679697901"  # Example of locally sparse

    convert_session(
        session_id=session_id,
        data_folder_path=data_folder_path,
        output_folder_path=output_folder_path,
        stub_test=stub_test,
    )
