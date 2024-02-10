"""Primary class for stimulus data specific to static gratings."""

import h5py
import numpy
from neuroconv.basedatainterface import BaseDataInterface
from pynwb.file import NWBFile, TimeIntervals


class StaticGratingStimuliInterface(BaseDataInterface):
    """Stimulus interface specific to the natural scenes for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str):
        super().__init__(v1_nwbfile_path=v1_nwbfile_path)
        self.v1_nwbfile = h5py.File(name=self.source_data["v1_nwbfile_path"], mode="r")

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict):
        if "static_gratings_stimulus" not in self.v1_nwbfile["stimulus"]["presentation"]:
            return

        static_gratings_source = self.v1_nwbfile["stimulus"]["presentation"]["static_gratings_stimulus"]

        static_gratings = TimeIntervals(
            name="static_gratings", description="Parameterizations of visual non-moving gratings shown to the subject."
        )
        static_gratings.add_column(
            name="orientation_in_degrees",
            description="Angle of the grating in degrees. NaN values correspond to a blank sweep.",
        )
        static_gratings.add_column(
            name="spatial_frequency_in_cycles_per_degree",
            description="Period of the grating in cycles/degree. NaN values correspond to a blank sweep.",
        )
        static_gratings.add_column(
            name="phase",
            description=(
                "Relative position of the grating. Phase 0 and Phase 0.5 are 180° apart so that the peak of "
                "the grating of phase 0 lines up with the trough of phase 0.5. NaN values correspond to a blank sweep."
            ),
        )
        static_gratings.add_column(name="is_blank_sweep ", description="Mean luminance gray image.")

        duration = 0.25  # Duration of presentation was hard coded and not explicitly synchronized
        # The 'frame_start, frame_stop' are nearest interpolations of ophys frames, not to the source sampling frequency
        static_gratings_data = static_gratings_source["data"][:]
        static_gratings_nan = numpy.isnan(static_gratings_data)
        blank_sweeps = static_gratings_nan[0] & static_gratings_nan[1] & static_gratings_nan[2]
        for (
            timestamp,
            (frame_start, frame_stop),
            (orientation_in_degrees, spatial_frequency_in_cycles_per_degree, phase),
            is_blank_sweep,
        ) in zip(
            static_gratings_source["timestamps"][:],
            static_gratings_source["frame_duration"][:],
            static_gratings_data,
            blank_sweeps,
        ):
            static_gratings.add_interval(
                start_time=timestamp,
                stop_time=timestamp + duration,
                orientation_in_degrees=orientation_in_degrees,
                spatial_frequency_in_cycles_per_degree=spatial_frequency_in_cycles_per_degree,
                phase=phase,
                is_blank_sweep=is_blank_sweep,
            )

        nwbfile.add_stimulus(static_gratings)
