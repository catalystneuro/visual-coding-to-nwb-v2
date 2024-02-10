"""Primary NWBConverter class for the Visual Coding - Optical Physiology dataset."""

from neuroconv import NWBConverter

from .interfaces import (  # VisualCodingTwoPhotonSeriesInterface,
    DriftingGratingStimulusInterface,
    EpochsInterface,
    EyeTrackingInterface,
    LocallySparseNoiseStimulusInterface,
    NaturalMovieStimulusInterface,
    NaturalSceneStimulusInterface,
    PupilTrackingInterface,
    RunningSpeedInterface,
    SpontaneousStimulusInterface,
    StaticGratingStimulusInterface,
    VisualCodingMetadataInterface,
    VisualCodingProcessedOphysInterface,
)


class VisualCodingOphysNWBConverter(NWBConverter):
    """Primary conversion class for this dataset."""

    data_interface_classes = dict(
        # Raw=VisualCodingTwoPhotonSeriesInterface,
        Metadata=VisualCodingMetadataInterface,
        EyeTracking=EyeTrackingInterface,
        PupilTracking=PupilTrackingInterface,
        RunningSpeed=RunningSpeedInterface,
        NaturalMovies=NaturalMovieStimulusInterface,
        NaturalScenes=NaturalSceneStimulusInterface,
        SpontaneousStimulus=SpontaneousStimulusInterface,
        LocallySparseStimuli=LocallySparseNoiseStimulusInterface,
        StaticGratingStimulus=StaticGratingStimulusInterface,
        DriftingGratingStimulus=DriftingGratingStimulusInterface,
        ProcessedOphys=VisualCodingProcessedOphysInterface,
        Epochs=EpochsInterface,
    )
