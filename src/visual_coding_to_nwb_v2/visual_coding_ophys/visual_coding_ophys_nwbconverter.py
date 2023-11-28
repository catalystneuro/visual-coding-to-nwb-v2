"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter

from .interfaces import (
    VisualCodingMetadataInterface,
    EyeTrackingInterface,
    PupilInterface,
    RunningSpeedInterface,
    NaturalMovieStimulusInterface,
    NaturalSceneStimulusInterface,
    # VisualCodingTwoPhotonSeriesInterface,
)


class VisualCodingOphysNWBConverter(NWBConverter):
    """Primary conversion class for this dataset."""

    data_interface_classes = dict(
        Metadata=VisualCodingMetadataInterface,
        EyeTracking=EyeTrackingInterface,
        Pupil=PupilInterface,
        RunningSpeed=RunningSpeedInterface,
        NaturalMovieOne=NaturalMovieStimulusInterface,
        # NaturalScene=NaturalSceneStimulusInterface,
        # Raw=VisualCodingTwoPhotonSeriesInterface,
    )
