"""Primary class for eye tracking data."""

import h5py
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module
from pynwb.behavior import CompassDirection, EyeTracking, SpatialSeries
from pynwb.file import NWBFile

from .shared_methods import add_eye_tracking_device


class EyeTrackingInterface(BaseDataInterface):
    """Eye tracking interface for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        if "Camera" not in nwbfile.devices:
            add_eye_tracking_device(nwbfile=nwbfile)

        processing_source = self.v1_nwbfile["processing"]["brain_observatory_pipeline"]
        if "EyeTracking" not in processing_source:
            return
        eye_tracking_source_data = processing_source["EyeTracking"]

        # x, y grid
        pupil_location_data = eye_tracking_source_data["pupil_location"]["data"][:]
        pupil_location_timestamps = eye_tracking_source_data["pupil_location"]["timestamps"][:]

        eye_tracking_spatial_series = SpatialSeries(
            name="pupil_location",
            description="Location of pupil focus on the visual grid.",
            data=pupil_location_data,
            timestamps=pupil_location_timestamps,
            unit="m",
            reference_frame="(0,0) is the center of the monitor.",
        )
        eye_tracking = EyeTracking(spatial_series=[eye_tracking_spatial_series])

        behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="Processed behavioral data.")
        behavior_module.add_data_interface(eye_tracking)

        # Angular space
        pupil_location_data_spherical = eye_tracking_source_data["pupil_location_spherical"]["data"][:]
        pupil_location_timestamps_spherical = eye_tracking_source_data["pupil_location_spherical"]["timestamps"][:]

        eye_tracking_spatial_series_spherical = SpatialSeries(
            name="pupil_location_spherical",
            description="Angle of pupil focus on the visual grid.",
            data=pupil_location_data_spherical,
            timestamps=pupil_location_timestamps_spherical,
            unit="degrees",
            reference_frame=(
                "(0,0) is the center of the monitor; angle of incidence is calculated with respect to a "
                "right-facing vector."
            ),
        )
        eye_tracking_spherical = CompassDirection(spatial_series=[eye_tracking_spatial_series_spherical])

        behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="Processed behavioral data.")
        behavior_module.add_data_interface(eye_tracking_spherical)
