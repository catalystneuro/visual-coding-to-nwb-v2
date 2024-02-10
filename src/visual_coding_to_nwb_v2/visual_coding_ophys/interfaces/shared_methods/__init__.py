"""Common methods to use across interfaces."""

from ._shared_methods import (
    add_eye_tracking_device,
    add_imaging_device,
    add_imaging_plane,
    add_stimulus_device,
)

__all__ = ["add_imaging_device", "add_imaging_plane", "add_eye_tracking_device", "add_stimulus_device"]
