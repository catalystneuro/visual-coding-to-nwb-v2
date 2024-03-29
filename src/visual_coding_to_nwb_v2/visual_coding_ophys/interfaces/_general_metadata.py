"""Primary class for grabbing experiment-specific metadata."""

from datetime import datetime

import h5py
from dateutil import tz
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.utils import DeepDict
from pynwb.file import NWBFile

SESSION_TYPE_MAPPING = dict(three_session_A=3)


class VisualCodingMetadataInterface(BaseDataInterface):
    """General metadata interface for visual-coding-ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)

    def get_metadata(self) -> DeepDict:
        metadata = super().get_metadata()

        with h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r") as v1_nwbfile:
            session_start_time = datetime.strptime(
                v1_nwbfile["session_start_time"][()].decode("utf-8"), "%a %b %d %H:%M:%S %Y"
            )
            session_start_time = session_start_time.replace(tzinfo=tz.gettz("US/Pacific"))
            metadata["NWBFile"]["session_start_time"] = session_start_time

            experiment_id = v1_nwbfile["general"]["ophys_experiment_id"][()].decode("utf-8")
            session_type = v1_nwbfile["general"]["session_type"][()].decode("utf-8")
            reduced_session_type = session_type.split("_")[-1]
            session_id = f"{experiment_id}-Stim{reduced_session_type}"
            metadata["NWBFile"]["session_id"] = session_id

            session_description = v1_nwbfile["session_description"][()].decode("utf-8") + "."
            session_description += """

Monitor was positioned 15 cm from the mouse's eye, and spanned 120 degrees x 95 degrees of visual space without accounting for stimulus warping.

Each monitor was gamma corrected using a USB-650 Red Tide Spectrometer (Ocean Optics). Luminance was measured using a SpectroCAL MKII Spectroradiometer (Cambridge Research Systems). Monitors were used at a brightness setting of 30% and contrast at 50%, corresponding to mean luminance of 50 cd/m^2.
"""  # noqa: E501
            metadata["NWBFile"]["session_description"] = session_description

            metadata["NWBFile"]["experiment_description"] = v1_nwbfile["general"]["For more information"][()].decode(
                "utf-8"
            )
            metadata["NWBFile"]["protocol"] = v1_nwbfile["general"]["ophys_experiment_name"][()].decode("utf-8")
            metadata["NWBFile"]["data_collection"] = (
                "Generated by " + " ".join([x.decode("utf-8") for x in v1_nwbfile["general"]["generated_by"][:]]) + "."
            )
            metadata["NWBFile"]["institution"] = v1_nwbfile["general"]["institution"][()].decode("utf-8")

            # TODO: If desired, could make lab-metadata extension for items included in these notes
            container_id = v1_nwbfile["general"]["experiment_container_id"][()].decode("utf-8")
            mouse_id = v1_nwbfile["general"]["specimen_name"][()].decode("utf-8").split("-")[-1]
            notes = f"Container ID: {container_id}"
            notes += f"\nMouse ID (from genotype white paper): {mouse_id}"
            notes += f"\nSession type: {session_type}"
            metadata["NWBFile"]["notes"] = notes

            metadata["Subject"]["subject_id"] = v1_nwbfile["general"]["subject"]["subject_id"][()].decode("utf-8")
            metadata["Subject"]["description"] = (
                v1_nwbfile["general"]["subject"]["description"][()].decode("utf-8") + "."
            )
            age_string = v1_nwbfile["general"]["subject"]["age"][()].decode("utf-8")
            days_old = age_string.split(" ")[0]
            metadata["Subject"]["age"] = f"P{days_old}D"
            sex_string = v1_nwbfile["general"]["subject"]["sex"][()].decode("utf-8")
            metadata["Subject"]["sex"] = "M" if sex_string == "male" else "F"
            metadata["Subject"]["species"] = v1_nwbfile["general"]["subject"]["species"][()].decode("utf-8")
            metadata["Subject"]["strain"] = v1_nwbfile["general"]["specimen_name"][()].decode("utf-8")  # TODO: confirm
            metadata["Subject"]["genotype"] = v1_nwbfile["general"]["subject"]["genotype"][()].decode("utf-8")

        return metadata

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        pass
