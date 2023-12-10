"""Primary script to run to convert an entire session for of data using the NWBConverter."""
from pathlib import Path
from typing import Union

from neuroconv.tools.nwb_helpers import (
    configure_backend,
    get_default_backend_configuration,
    make_or_load_nwbfile,
)

from visual_coding_to_nwb_v2.visual_coding_ophys import VisualCodingOphysNWBConverter


def convert_session(
    session_id: str, data_folder_path: Union[str, Path], output_folder_path: Union[str, Path], stub_test: bool = False
):
    """Convert a single session of the visual coding ophys dataset."""
    data_folder_path = Path(data_folder_path)
    output_folder_path = Path(output_folder_path)

    if stub_test:
        output_folder_path = output_folder_path / "nwb_stub"
    output_folder_path.mkdir(parents=True, exist_ok=True)

    v1_nwbfile_path = data_folder_path / f"{session_id}.nwb"
    v2_nwbfile_path = output_folder_path / f"ses-{session_id}.nwb"

    # All interfaces take the same input for this conversion
    source_data = {
        key: dict(v1_nwbfile_path=str(v1_nwbfile_path)) for key in VisualCodingOphysNWBConverter.data_interface_classes
    }

    converter = VisualCodingOphysNWBConverter(source_data=source_data)
    metadata = converter.get_metadata()

    with make_or_load_nwbfile(
        nwbfile_path=v2_nwbfile_path,
        metadata=metadata,
        overwrite=True,
        verbose=True,
    ) as nwbfile:
        converter.add_to_nwbfile(nwbfile=nwbfile, metadata=metadata)
        default_backend_configuration = get_default_backend_configuration(nwbfile=nwbfile, backend="hdf5")

        with open(file=f"C:/Users/Raven/Downloads/backend_configuration_{session_id}.txt", mode="w") as io:
            io.writelines(str(default_backend_configuration))

        configure_backend(nwbfile=nwbfile, backend_configuration=default_backend_configuration)


if __name__ == "__main__":
    data_folder_path = Path("F:/visual-coding/ophys_experiment_data")
    output_folder_path = Path("F:/visual-coding/v2_nwbfiles")
    stub_test = False

    # session_id = "496908818"  # Example of natural scenes
    # session_id = "679697901"  # Example of locally sparse
    session_id = "682051855"  # Example of drifting grating and spontaneous

    convert_session(
        session_id=session_id,
        data_folder_path=data_folder_path,
        output_folder_path=output_folder_path,
        stub_test=stub_test,
    )
