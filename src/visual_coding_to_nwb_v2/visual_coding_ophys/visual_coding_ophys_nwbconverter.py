"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter

from .visualcodingmetadatainterface import VisualCodingMetadataInterface
from .visualcodingpupilinterface import VisualCodingPupilInterface


class VisualCodingOphysNWBConverter(NWBConverter):
    """Primary conversion class for this dataset."""

    data_interface_classes = dict(
        Metadata=VisualCodingMetadataInterface,
        Pupil=VisualCodingPupilInterface,
    )
