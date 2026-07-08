import numpy as np
import pytest

from pipeline.preprocessing.loads import extract_window, to_abaqus_time, compute_frame_times, format_amplitude_lines, find_last_active_frame

def test_extract_window_no_data():
    time_ms = np.array([0, 50, 100])
    velocity = np.array([10, 20, 300])
   
    with pytest.raises(ValueError):
        results = extract_window(time_ms, velocity, 200, 300)  

def test_extract_window_with_data():
    time_ms = np.array([0, 50, 100])
    velocity = np.array([10, 20, 300])

    t_win, v_win = extract_window(time_ms, velocity, 25, 75)

    assert np.array_equal(t_win, np.array([50]))
    assert np.array_equal(v_win, np.array([20]))

def test_extract_window_boundary_values():
    time_ms = np.array([0, 50, 100])
    velocity = np.array([10, 20, 300])

    t_win, v_win = extract_window(time_ms, velocity, time_ms[0], time_ms[-1])

    assert np.array_equal(t_win, np.array([0, 50, 100]))
    assert np.array_equal(v_win, np.array([10, 20, 300]))

def test_to_abaqus_time():

    t_win_ms = np.array([0, 50, 100])
    t_start_ms = 0
    t_end_ms = 100

    t_abq_s = to_abaqus_time(t_win_ms, t_start_ms, t_end_ms)

    assert np.array_equal(t_abq_s, np.array([0, 0.05, 0.1]))

def test_compute_frame_times():

    frame_center_ms = np.array([0.0, 18.0, 36.0, 54.0])
    frame_start_ms = np.array([-9.0, 9.0, 27.0, 45.0])
    frame_end_ms = np.array([9.0, 27.0, 45.0, 63.0])
    t_sim_start_ms = -9.0

    results = compute_frame_times(frame_center_ms, frame_start_ms, frame_end_ms, t_sim_start_ms)

    assert results[0]["abaqus_time_s"] == 0.009
    assert results[1]["abaqus_time_s"] == 0.027
    assert results[2]["abaqus_time_s"] == 0.045
    assert results[3]["abaqus_time_s"] == 0.063
    assert len(results) == 4


def test_find_last_active_frame_no_cutoff():
    # v_cutoff=0 → never trim regardless of velocity
    frame_start = np.array([0.0, 18.0, 36.0, 54.0])
    frame_end = np.array([9.0, 27.0, 45.0, 63.0])
    time_ms = np.linspace(0, 63, 100)
    velocity = np.zeros(100)

    idx = find_last_active_frame(frame_start, frame_end, time_ms, velocity, v_cutoff=0.0)
    assert idx == 3


def test_find_last_active_frame_all_active():
    # All frames above threshold → last index returned
    frame_start = np.array([0.0, 18.0, 36.0, 54.0])
    frame_end = np.array([9.0, 27.0, 45.0, 63.0])
    time_ms = np.linspace(0, 63, 200)
    velocity = np.ones(200) * 2.0

    idx = find_last_active_frame(frame_start, frame_end, time_ms, velocity, v_cutoff=0.1)
    assert idx == 3


def test_find_last_active_frame_trailing_dead():
    # First 2 frames active, last 2 dead → index 1
    frame_start = np.array([0.0, 18.0, 36.0, 54.0])
    frame_end = np.array([9.0, 27.0, 45.0, 63.0])
    time_ms = np.linspace(0, 63, 200)
    velocity = np.where(time_ms <= 27.0, 2.0, 0.0)

    idx = find_last_active_frame(frame_start, frame_end, time_ms, velocity, v_cutoff=0.1)
    assert idx == 1


def test_find_last_active_frame_only_first_active():
    # Only first frame active
    frame_start = np.array([0.0, 18.0, 36.0])
    frame_end = np.array([9.0, 27.0, 45.0])
    time_ms = np.linspace(0, 45, 100)
    velocity = np.where(time_ms <= 9.0, 2.0, 0.0)

    idx = find_last_active_frame(frame_start, frame_end, time_ms, velocity, v_cutoff=0.1)
    assert idx == 0


def test_find_last_active_frame_none_active_returns_safe_default():
    # All frames below threshold → safe default: last index (never trim to zero)
    frame_start = np.array([0.0, 18.0, 36.0])
    frame_end = np.array([9.0, 27.0, 45.0])
    time_ms = np.linspace(0, 45, 100)
    velocity = np.ones(100) * 0.01

    idx = find_last_active_frame(frame_start, frame_end, time_ms, velocity, v_cutoff=0.1)
    assert idx == 2


def test_format_amplitude_lines():

    t_abq_s = np.array([0.0, 0.05, 0.1])
    v_win = np.array([3.4, 2.1, 1.0])

    lines = format_amplitude_lines(t_abq_s, v_win)

    assert len(lines) == 4
    assert "AMP-1" in lines[0]
    assert "  0.00000000,  3.40000000," in lines[1] 

