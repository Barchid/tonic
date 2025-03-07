import pytest
import numpy as np
import tonic.transforms as transforms
from utils import create_random_input


class TestRepresentations:
    @pytest.mark.parametrize(
        "time_window, event_count, n_time_bins, n_event_bins, overlap,"
        " include_incomplete, sensor_size",
        [
            (2000, None, None, None, 0, False, (40, 20, 2)),
            (2000, None, None, None, 200, True, (40, 20, 1)),
            (1000, None, None, None, 100, True, (40, 20, 3)),
            (None, 2000, None, None, 0, False, (40, 20, 2)),
            (None, 2000, None, None, 200, True, (20, 20, 1)),
            (None, 2000, None, None, 100, True, (10, 20, 2)),
            (None, None, 5, None, 0, False, (40, 20, 2)),
            (None, None, 5, None, 0.1, False, (10, 20, 2)),
            (None, None, 5, None, 0.25, True, (40, 20, 2)),
            (None, None, None, 5, 0, True, (40, 20, 2)),
            (None, None, None, 5, 0.1, False, (40, 20, 2)),
            (None, None, None, 5, 0.25, False, (10, 20, 1)),
        ],
    )
    def test_representation_frame(
        self,
        time_window,
        event_count,
        n_time_bins,
        n_event_bins,
        overlap,
        include_incomplete,
        sensor_size,
    ):
        n_events = 10000
        orig_events, _ = create_random_input(sensor_size=sensor_size, n_events=n_events)

        transform = transforms.ToFrame(
            sensor_size=sensor_size,
            time_window=time_window,
            event_count=event_count,
            n_time_bins=n_time_bins,
            n_event_bins=n_event_bins,
            overlap=overlap,
            include_incomplete=include_incomplete,
        )

        frames = transform(orig_events)

        assert frames.shape[1:] == sensor_size[::-1]
        if time_window is not None:
            stride = time_window - overlap
            times = orig_events["t"]
            if include_incomplete:
                assert frames.shape[0] == int(
                    np.ceil(((times[-1] - times[0]) - time_window) / stride) + 1
                )
            else:
                assert frames.shape[0] == int(
                    np.floor(((times[-1] - times[0]) - time_window) / stride) + 1
                )

        if event_count is not None:
            assert event_count == frames[0].sum()
            stride = event_count - overlap
            if include_incomplete:
                assert frames.shape[0] == int(
                    np.ceil((n_events - event_count) / stride) + 1
                )
            else:
                assert frames.shape[0] == int(
                    np.floor((n_events - event_count) / stride) + 1
                )

        if n_time_bins is not None:
            assert frames.shape[0] == n_time_bins

        if n_event_bins is not None:
            assert frames.shape[0] == n_event_bins
            assert frames[0].sum() == (1 + overlap) * (n_events // n_event_bins)

        assert frames is not orig_events


    @pytest.mark.parametrize(
        "time_window, event_count, n_time_bins, n_event_bins, overlap,"
        " include_incomplete, sensor_size",
        [
            (2000, None, None, None, 0, False, (40, 20, 2)),
            (2000, None, None, None, 200, True, (40, 20, 1)),
            (1000, None, None, None, 100, True, (40, 20, 3)),
            (None, 2000, None, None, 0, False, (40, 20, 2)),
            (None, 2000, None, None, 200, True, (20, 20, 1)),
            (None, 2000, None, None, 100, True, (10, 20, 2)),
            (None, None, 5, None, 0, False, (40, 20, 2)),
            (None, None, 5, None, 0.1, False, (10, 20, 2)),
            (None, None, 5, None, 0.25, True, (40, 20, 2)),
            (None, None, None, 5, 0, True, (40, 20, 2)),
            (None, None, None, 5, 0.1, False, (40, 20, 2)),
            (None, None, None, 5, 0.25, False, (10, 20, 1)),
        ],
    )
    def test_representation_sparse_tensor(
        self,
        time_window,
        event_count,
        n_time_bins,
        n_event_bins,
        overlap,
        include_incomplete,
        sensor_size,
    ):
        n_events = 10000
        orig_events, sensor_size = create_random_input(sensor_size=sensor_size, n_events=n_events)

        transform = transforms.ToSparseTensor(
            sensor_size=sensor_size,
            time_window=time_window,
            event_count=event_count,
            n_time_bins=n_time_bins,
            n_event_bins=n_event_bins,
            overlap=overlap,
            include_incomplete=include_incomplete,
        )

        sparse_tensor = transform(orig_events)

        assert sparse_tensor.is_sparse
        assert sparse_tensor.shape[1:] == sensor_size[::-1]

        if time_window is not None:
            stride = time_window - overlap
            times = orig_events["t"]
            if include_incomplete:
                assert sparse_tensor.shape[0] == int(
                    np.ceil(((times[-1] - times[0]) - time_window) / stride) + 1
                )
            else:
                assert sparse_tensor.shape[0] == int(
                    np.floor(((times[-1] - times[0]) - time_window) / stride) + 1
                )

        if event_count is not None:
            assert event_count == sparse_tensor[0].to_dense().sum()
            stride = event_count - overlap
            if include_incomplete:
                assert sparse_tensor.shape[0] == int(
                    np.ceil((n_events - event_count) / stride) + 1
                )
            else:
                assert sparse_tensor.shape[0] == int(
                    np.floor((n_events - event_count) / stride) + 1
                )

        if n_time_bins is not None:
            assert sparse_tensor.shape[0] == n_time_bins

        if n_event_bins is not None:
            assert sparse_tensor.shape[0] == n_event_bins
            assert sparse_tensor[0].to_dense().sum() == (1 + overlap) * (n_events // n_event_bins)

        assert sparse_tensor is not orig_events

        
    def test_representation_frame_inferred(self):
        sensor_size = (20, 10, 2)
        orig_events, _ = create_random_input(n_events=30000, sensor_size=sensor_size)
        transform = transforms.ToFrame(sensor_size=None, time_window=25000)
        frames = transform(orig_events)
        assert frames.shape[1:] == sensor_size[::-1]

    def test_representation_frame_audio(self):
        sensor_size = (200, 1, 2)
        orig_events, _ = create_random_input(
            sensor_size=sensor_size,
            dtype=np.dtype([("x", int), ("t", int), ("p", int)]),
        )
        transform = transforms.ToFrame(sensor_size=sensor_size, time_window=25000)
        frames = transform(orig_events)
        assert frames.shape[1:] == (sensor_size[2], sensor_size[0])

    def test_representation_image(self):
        sensor_size = (100, 100, 2)
        orig_events, _ = create_random_input(n_events=10000, sensor_size=sensor_size)
        transform = transforms.ToImage(sensor_size=sensor_size)
        image = transform(orig_events)
        assert image.shape == sensor_size[::-1]

    @pytest.mark.parametrize(
        "surface_dimensions, tau,", [((15, 15), 100), ((3, 3), 10), (None, 1e4)]
    )
    def test_representation_time_surface(self, surface_dimensions, tau):
        orig_events, sensor_size = create_random_input()

        transform = transforms.ToTimesurface(
            sensor_size=sensor_size, surface_dimensions=surface_dimensions, tau=tau
        )

        surfaces = transform(orig_events)

        assert surfaces.shape[0] == len(orig_events)
        assert surfaces.shape[1] == 2
        if surface_dimensions:
            assert surfaces.shape[2:] == surface_dimensions
        else:
            assert surfaces.shape[2] == sensor_size[1]
            assert surfaces.shape[3] == sensor_size[0]
        assert surfaces is not orig_events

    @pytest.mark.parametrize("surface_size, cell_size, tau, num_workers, decay", [(7, 9, 100, 1, "lin"), (3, 4, 1000, 1, "exp")])
    def test_representation_avg_time_surface(self, surface_size, cell_size, tau, num_workers, decay):
        orig_events, sensor_size = create_random_input(n_events=1000)

        transform = transforms.ToAveragedTimesurface(
            sensor_size=sensor_size, surface_size=surface_size, cell_size=cell_size, tau=tau, num_workers=num_workers, decay=decay
        )

        surfaces = transform(orig_events)
        import math 
        assert len(surfaces.shape) == 4
        assert surfaces.shape[0] == math.ceil(sensor_size[0]/cell_size)*math.ceil(sensor_size[1]/cell_size)
        assert surfaces.shape[1] == sensor_size[2]
        assert surfaces.shape[2] == surface_size
        assert surfaces.shape[3] == surface_size
        assert surfaces is not orig_events

    @pytest.mark.parametrize("n_time_bins", [10, 1])
    def test_representation_voxel_grid(self, n_time_bins):
        orig_events, sensor_size = create_random_input()

        transform = transforms.ToVoxelGrid(
            sensor_size=sensor_size, n_time_bins=n_time_bins
        )

        volume = transform(orig_events)
        assert volume.shape == (n_time_bins, *sensor_size[1::-1])
        assert volume is not orig_events
