"""Primary class for two photon series."""
from pathlib import Path

import numpy
import h5py
from pynwb import H5DataIO
from pynwb.file import NWBFile
from pynwb.ophys import TwoPhotonSeries, ImagingPlane
from pynwb.testing.mock.ophys import mock_ImagingPlane, mock_Device  # TODO: temporary
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.hdmf import SliceableDataChunkIterator


class TwoPhotonSeriesInterface(BaseDataInterface):
    """Two photon calcium imaging interface for visual coding ophys conversion."""

    def __init__(self, v1_nwbfile_path: Path, ophys_movie_path: Path):
        self.v1_nwbfile = h5py.File(name=v1_nwbfile_path, mode="r")
        self.ophys_movie = h5py.File(name=ophys_movie_path, mode="r")
        super().__init__(v1_nwbfile_path=v1_nwbfile_path, ophys_movie_path=ophys_movie_path)

    def __del__(self):
        """
        The HDF5 files must remain open for buffered writing (they are not read all at once into RAM).

        Garbage collection should close the I/O no matter what, but doesn't hurt to additionally specify here.
        """
        self.v1_nwbfile.close()
        self.ophys_movie.close()

    def add_to_nwbfile(self, nwbfile: NWBFile, metadata: dict, stub_test: bool = False):
        ophys_data = self.ophys_movie["data"]
        timestamps = self.v1_nwbfile["acquisition"]["timeseries"]["2p_image_series"]["timestamps"]

        max_frames_per_chunk = int(10e6 / (ophys_data.dtype.itemsize * ophys_data.shape[1] * ophys_data.shape[2]))
        data_buffer_shape = (  # TODO: fix neuroconv bug with numpy.prod
            min(ophys_data.shape[0], max_frames_per_chunk * 100),
            ophys_data.shape[1],
            ophys_data.shape[2],
        )
        data_chunk_shape = (
            min(ophys_data.shape[0], max_frames_per_chunk),
            ophys_data.shape[1],
            ophys_data.shape[2],
        )

        timestamps_chunk_shape = (min(timestamps.shape[0], int(10e6 / timestamps.dtype.itemsize)),)

        device = mock_Device()  # TODO: replace with actual
        nwbfile.add_device(devices=device)

        imaging_plane = mock_ImagingPlane(device=device)  # TODO: replace with actual
        nwbfile.add_imaging_plane(imaging_planes=imaging_plane)

        two_photon_series = TwoPhotonSeries(
            name="TwoPhotonSeries",
            description="Raw flourescence from calcium imaging recording.",
            data=H5DataIO(
                data=SliceableDataChunkIterator(
                    data=ophys_data[: data_chunk_shape[0], ...] if stub_test else ophys_data,
                    chunk_shape=data_chunk_shape,
                    buffer_shape=data_buffer_shape,
                ),
                compression=True,
            ),
            imaging_plane=imaging_plane,
            unit="n.a.",
            timestamps=H5DataIO(
                data=SliceableDataChunkIterator(
                    numpy.array(timestamps)[: data_chunk_shape[0]] if stub_test else numpy.array(timestamps),
                    chunk_shape=(data_chunk_shape[0],) if stub_test else timestamps_chunk_shape,
                ),
                compression=True,
            ),
        )
        nwbfile.add_acquisition(two_photon_series)
