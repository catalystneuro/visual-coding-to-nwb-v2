"""Primary class for stimulus data specific to drifting gratings."""

import h5py
from neuroconv.basedatainterface import BaseDataInterface
from pynwb.file import NWBFile, TimeIntervals


class DriftingGratingStimulusInterface(BaseDataInterface):
    """Stimulus interface specific to the natural scenes for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        if "drifting_gratings_stimulus" not in self.v1_nwbfile["stimulus"]["presentation"]:
            return

        drifting_gratings_source = self.v1_nwbfile["stimulus"]["presentation"]["drifting_gratings_stimulus"]

        drifting_gratings = TimeIntervals(
            name="drifting_gratings",
            description=(
                "Parameterizations of full field drifting sinusoidal grating at a single spatial contrast (80%). "
                "Direction of motion is to the orientation of the grating."
            ),
        )
        drifting_gratings.add_column(
            name="orientation_in_degrees",
            description="Angle of the grating in degrees. NaN values correspond to a blank sweep.",
        )
        drifting_gratings.add_column(
            name="spatial_frequency_in_cycles_per_degree",
            description="Period of the grating in cycles/degree. NaN values correspond to a blank sweep.",
        )
        drifting_gratings.add_column(
            name="temporal_frequency_in_hz",
            description="The speed at which the grating moves in Hz. NaN values correspond to a blank sweep.",
        )
        drifting_gratings.add_column(name="is_blank_sweep", description="Mean luminance gray image.")

        duration = 2.0  # Duration of presentation was hard coded and not explicitly synchronized
        # The 'frame_start, frame_stop' are nearest interpolations of ophys frames, not the to source sampling frequency
        for (
            timestamp,
            (frame_start, frame_stop),
            (temporal_frequency_in_hz, orientation_in_degrees, is_blank_sweep),
        ) in zip(
            drifting_gratings_source["timestamps"][:],
            drifting_gratings_source["frame_duration"][:],
            drifting_gratings_source["data"][:],
        ):
            drifting_gratings.add_interval(
                start_time=timestamp,
                stop_time=timestamp + duration,
                orientation_in_degrees=orientation_in_degrees,
                # spatial_frequency_in_cycles_per_degree was a fixed value.
                # Attached for consistency, description, and to show that it could have in principle varied.
                spatial_frequency_in_cycles_per_degree=0.04,
                temporal_frequency_in_hz=temporal_frequency_in_hz,
                is_blank_sweep=bool(is_blank_sweep),
            )

        nwbfile.add_stimulus(stimulus=drifting_gratings)
