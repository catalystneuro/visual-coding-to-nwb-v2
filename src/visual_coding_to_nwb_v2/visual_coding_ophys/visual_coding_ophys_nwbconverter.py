"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter

from .visual_coding_ophys_metadata_interface import VisualCodingMetadataInterface
from .visual_coding_ophys_pupil_interface import VisualCodingPupilInterface


class VisualCodingOphysNWBConverter(NWBConverter):
    """Primary conversion class for this dataset."""

    data_interface_classes = dict(
        Metadata=VisualCodingMetadataInterface,
        Pupil=VisualCodingPupilInterface,
    )
