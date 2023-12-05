"""Common functions for adding device/imaging plane used by both the 2P and processed ophys interfaces."""
from typing import Literal

import numpy
from pynwb import NWBFile
from pynwb.file import Device
from pynwb.ophys import ImagingPlane, OpticalChannel


def add_stimulus_device(nwbfile: NWBFile):
    """Custom device for the stimulus display data from the Visual Coding Ophys conversion."""
    nwbfile.add_device(
        devices=Device(
            name="StimulusDisplay",
            description="An ASUS PA248Q monitor used to display visual stimuli.",
            manufacturer="ASUS",
        )
    )


def add_eye_tracking_device(nwbfile: NWBFile):
    """Custom device for the eye tracking and pupil data from the Visual Coding Ophys conversion."""
    nwbfile.add_device(
        devices=Device(
            name="Camera",
            description="An AVT Mako-G032B camera used to track eye movement and pupil dilation.",
            manufacturer="Allied Vision",
        )
    )


def add_imaging_device(nwbfile: NWBFile):
    """Custom Device for the calcium imaging data from the Visual Coding Ophys conversion."""
    nwbfile.add_device(
        devices=Device(
            name="Microscope",
            description=(
                "A Nikon A1R-MP multiphoton microscope. "
                "This system was adapted to provide space to accommodate the behavior apparatus."
            ),
            manufacturer="Nikon",
        )
    )


def add_imaging_plane(
    nwbfile: NWBFile, depth: str, location: Literal["VISl", "VISal", "VISp", "VISpm", "VISrl", "VISam"]
):
    """Custom ImagingPlane for Visual Coding Ophys conversion."""
    device = nwbfile.devices["Microscope"]

    optical_channel = OpticalChannel(
        name="OpticalChannel",
        description="An optical channel used to collection light emission during two-photon calcium imaging.",
        emission_lambda=numpy.nan,
    )

    imaging_plane = ImagingPlane(
        name="ImagingPlane",
        description="The imaging plane sampled by the two-photon calcium imaging at a depth of {depth} µm.",
        excitation_lambda=910.0,
        indicator="GCaMP6f",
        grid_spacing=[0.78, 0.78],
        grid_spacing_unit="micrometers",
        location=location,
        device=device,
        optical_channel=optical_channel,
    )

    nwbfile.add_imaging_plane(imaging_planes=imaging_plane)
