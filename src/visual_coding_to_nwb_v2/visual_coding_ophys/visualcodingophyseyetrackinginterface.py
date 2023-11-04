"""Primary class for eye tracking data."""
from pathlib import Path

import h5py
from pynwb import H5DataIO
from pynwb.file import NWBFile
from pynwb.behavior import EyeTracking, SpatialSeries, CompassDirection
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module


class VisualCodingEyeTrackingInterface(BaseDataInterface):
    """Eye tracking interface for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: Path):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        with h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r") as v1_nwbfile:
            eye_tracking_source_data = v1_nwbfile["processing"]["brain_observatory_pipeline"]["EyeTracking"]

            # x, y grid
            pupil_location_data = eye_tracking_source_data["pupil_location"]["data"]
            number_of_columns = 2
            max_frames_per_chunk = int(10e6 / (pupil_location_data.dtype.itemsize * number_of_columns))
            data_chunks = (min(pupil_location_data.shape[0], max_frames_per_chunk), number_of_columns)

            pupil_location_timestamps = eye_tracking_source_data["pupil_location"]["timestamps"]
            timestamp_chunks = min(
                pupil_location_timestamps.shape[0], int(10e6 / pupil_location_timestamps.dtype.itemsize)
            )

            eye_tracking_spatial_series = list(
                SpatialSeries(
                    name="pupil_location",
                    description="Location of pupil focus on the visual grid.",
                    data=H5DataIO(data=pupil_location_data, compression=True, chunks=data_chunks),
                    timestamps=H5DataIO(data=pupil_location_timestamps, compression=True, chunks=timestamp_chunks),
                    unit="m",
                    reference_frame="(0,0) is the center of the monitor.",
                )
            )
            eye_tracking = EyeTracking(spatial_series=eye_tracking_spatial_series)

            behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="Processed behavioral data.")
            behavior_module.add(eye_tracking)

            # Angular space
            pupil_location_data_spherical = eye_tracking_source_data["pupil_location_spherical"]["data"]
            number_of_columns_spherical = 2
            max_frames_per_chunk_spherical = int(
                10e6 / (pupil_location_data_spherical.dtype.itemsize * number_of_columns_spherical)
            )
            data_chunks_spherical = (
                min(pupil_location_data_spherical.shape[0], max_frames_per_chunk_spherical),
                number_of_columns_spherical,
            )

            pupil_location_timestamps_spherical = eye_tracking_source_data["pupil_location_spherical"]["timestamps"]
            timestamp_chunks_spherical = min(
                pupil_location_timestamps_spherical.shape[0],
                int(10e6 / pupil_location_timestamps_spherical.dtype.itemsize),
            )

            eye_tracking_spatial_series_spherical = list(
                SpatialSeries(
                    name="pupil_location_spherical",
                    description="Angle of pupil focus on the visual grid.",
                    data=H5DataIO(data=pupil_location_data_spherical, compression=True, chunks=data_chunks_spherical),
                    timestamps=H5DataIO(
                        data=pupil_location_timestamps_spherical, compression=True, chunks=timestamp_chunks_spherical
                    ),
                    unit="degrees",
                    reference_frame=(
                        "(0,0) is the center of the monitor; angle of incidence is calculated with respect to a "
                        "right-facing vector."
                    ),
                )
            )
            eye_tracking_spherical = CompassDirection(spatial_series=eye_tracking_spatial_series_spherical)

            behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="Processed behavioral data.")
            behavior_module.add(eye_tracking_spherical)
