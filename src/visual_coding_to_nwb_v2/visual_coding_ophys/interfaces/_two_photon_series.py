"""Primary class for two photon series."""

import h5py
import numpy
import pynwb
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.hdmf import SliceableDataChunkIterator
from pynwb.ophys import TwoPhotonSeries

from .shared_methods import add_imaging_device, add_imaging_plane


class VisualCodingTwoPhotonSeriesInterface(BaseDataInterface):
    """Two photon calcium imaging interface for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: str, ophys_movie_file_path: str):
        self.v1_nwbfile = h5py.File(name=v1_nwbfile_path, mode="r")
        self.ophys_movie = h5py.File(name=ophys_movie_file_path, mode="r")
        super().__init__(v1_nwbfile_path=v1_nwbfile_path, ophys_movie_file_path=ophys_movie_file_path)

    def __del__(self):
        """
        The HDF5 files must remain open for buffered writing (they are not read all at once into RAM).

        Garbage collection should close the I/O no matter what, but doesn't hurt to additionally specify here.
        """
        if hasattr(self, "v1_nwbfile"):
            self.v1_nwbfile.close()
        if hasattr(self, "ophys_movie"):
            self.ophys_movie.close()

    def add_to_nwbfile(self, nwbfile: pynwb.NWBFile, metadata: dict, stub_test: bool = False):
        ophys_data = self.ophys_movie["data"]
        timestamps = self.v1_nwbfile["acquisition"]["timeseries"]["2p_image_series"]["timestamps"]

        add_imaging_device(nwbfile=nwbfile)

        source_imaging_plane = self.v1_nwbfile["general"]["optophysiology"]["imaging_plane_1"]
        add_imaging_plane(
            nwbfile=nwbfile,
            depth=source_imaging_plane["imaging depth"][()].decode("utf-8").strip(" microns"),
            location=source_imaging_plane["location"][()].decode("utf-8"),
        )
        imaging_plane = nwbfile.imaging_planes["ImagingPlane"]

        two_photon_series = TwoPhotonSeries(
            name="MotionCorrectedTwoPhotonSeries",
            description=(
                "Motion corrected flourescence from calcium imaging recording. "
                "Refer to the 'MotionCorrectionShiftsPerFrame' series to see how each frame was shifted."
            ),
            data=SliceableDataChunkIterator(
                data=ophys_data[:10, ...] if stub_test else ophys_data,
                display_progress=True,
                progress_bar_options=dict(position=1),
            ),
            imaging_plane=imaging_plane,
            unit="n.a.",
            timestamps=SliceableDataChunkIterator(
                numpy.array(timestamps)[:10] if stub_test else numpy.array(timestamps),
            ),
        )
        nwbfile.add_acquisition(two_photon_series)

        motion_correction = self.v1_nwbfile["processing"]["brain_observatory_pipeline"]["MotionCorrection"]
        # Either 'x' is 'height' and 'y' is 'width', or the imaging data is saved as height x width (hard to tell)
        # Either way, flipping this here so it makes more sense one-to-one with axis indices
        xy_translation_data = numpy.flip(motion_correction["2p_image_series"]["xy_translation"]["data"][:, :], axis=1)
        xy_translation = pynwb.TimeSeries(
            name="MotionCorrectionShiftsPerFrame",
            description=(
                "The continuous column (first value of the second axis) and row (second value of second axis) shifts"
                "estimated by motion correction. Actual pixel shifts per axis are the nearest integer to these values."
            ),
            data=xy_translation_data[:10, ...] if stub_test else xy_translation_data,
            unit="n.a.",
            timestamps=two_photon_series,
        )
        nwbfile.add_acquisition(xy_translation)
