"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter

from .interfaces import (
    # VisualCodingTwoPhotonSeriesInterface,
    VisualCodingMetadataInterface,
    EyeTrackingInterface,
    PupilInterface,
    RunningSpeedInterface,
    NaturalMovieStimulusInterface,
    NaturalSceneStimulusInterface,
    SpontaneousStimuliInterface,
    LocallySparseNoiseStimulusInterface,
    StaticGratingStimuliInterface,
    DriftingGratingStimuliInterface,
    VisualCodingProcessedOphysInterface,
)


class VisualCodingOphysNWBConverter(NWBConverter):
    """Primary conversion class for this dataset."""

    data_interface_classes = dict(
        # Raw=VisualCodingTwoPhotonSeriesInterface,
        Metadata=VisualCodingMetadataInterface,
        EyeTracking=EyeTrackingInterface,
        Pupil=PupilInterface,
        RunningSpeed=RunningSpeedInterface,
        NaturalMovies=NaturalMovieStimulusInterface,
        NaturalScenes=NaturalSceneStimulusInterface,
        SpontaneousStimuli=SpontaneousStimuliInterface,
        LocallySparseStimuli=LocallySparseNoiseStimulusInterface,
        StaticGratingStimuli=StaticGratingStimuliInterface,
        DriftingGratingStimuli=DriftingGratingStimuliInterface,
        ProcessedOphys=VisualCodingProcessedOphysInterface,
    )
