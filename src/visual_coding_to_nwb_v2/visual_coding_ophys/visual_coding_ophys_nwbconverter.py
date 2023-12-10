"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter

from .interfaces import (  # VisualCodingTwoPhotonSeriesInterface,
    DriftingGratingStimuliInterface,
    EyeTrackingInterface,
    LocallySparseNoiseStimulusInterface,
    NaturalMovieStimulusInterface,
    NaturalSceneStimulusInterface,
    PupilInterface,
    RunningSpeedInterface,
    SpontaneousStimulusInterface,
    StaticGratingStimuliInterface,
    VisualCodingMetadataInterface,
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
        SpontaneousStimulus=SpontaneousStimulusInterface,
        LocallySparseStimuli=LocallySparseNoiseStimulusInterface,
        StaticGratingStimuli=StaticGratingStimuliInterface,
        DriftingGratingStimuli=DriftingGratingStimuliInterface,
        ProcessedOphys=VisualCodingProcessedOphysInterface,
    )
