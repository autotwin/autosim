import numpy as np


def extract_window(time_ms, velocity, t_start_ms, t_end_ms) -> tuple:

    """
    Extracts the time and velocity window from first frame to last frame
    
    Args:
        time_ms : Time array in ms
        velocity : Velocity array in rad/s
        t_start_ms : First time array component in ms
        t_end_ms : Last time array component in ms

    Returns:
        The filtered time and velocity arrays as a tuple

    Raises:
      ValueError: If no data points found in the window.
    """

    ### Add assert t_start_ms < t_end_ms check if t_start > t_end -> throw an error
    ### assert t_min < t_max, "t_min must be less than t_max"
 
    mask = (time_ms >= t_start_ms) & (time_ms <= t_end_ms)
    t_win_ms = time_ms[mask]
    v_win = velocity[mask]

    if len(t_win_ms) == 0:
        raise ValueError(
            "No data points found in window [{}, {}] ms. "
            "Check .mat time axis.".format(t_start_ms, t_end_ms))

    return (t_win_ms, v_win)


def to_abaqus_time(t_win_ms: float, t_start_ms: float, t_end_ms: float) -> tuple:

    """
    Converts filtered time array from milliseconds to Abaqus  
    seconds, pinning first point to 0.0 and last to
    sim_duration. 

    Args:
        t_win_ms : Time window in ms
        t_start_ms : First time component in ms
        t_end_ms : Last time component in ms

    Returns:
        t_abq_s : An array which contains the time period used by solver in s
    """
    
    sim_duration = (t_end_ms - t_start_ms) / 1000.0
    
    t_abq_s = (t_win_ms - t_start_ms) / 1000.0
    
    # Ensure first point is exactly t=0 and last is exactly sim_duration
    t_abq_s[0] = 0.0
    t_abq_s[-1] = sim_duration

    return t_abq_s


def compute_frame_times(frame_center_ms, frame_start_ms, frame_end_ms, t_sim_start_ms) -> dict:

    """
    Computes the Experimental and Simulation time frames that will be used for result comparison

    Args:
        frame_center_ms : Each frame center in ms
        frame_start_ms : Each frame start in ms
        frame_end_ms : Each frame end in ms
        t_sim_start_ms : First time component of Abaqus time window in ms

    Returns:
        A list of dicts containing the time of each frame in s
    """

    comp_frames = []
    for i in range(len(frame_center_ms)):
        fc_ms = frame_center_ms[i]
        fs_ms = frame_start_ms[i]
        fe_ms = frame_end_ms[i]
        t_abq = (fc_ms - t_sim_start_ms) / 1000.0
        comp_frames.append({
            "frame_index": i,
            "frameCenter_ms": fc_ms,
            "frameStart_ms": fs_ms,
            "frameEnd_ms": fe_ms,
            "abaqus_time_s": round(t_abq, 6),
        })
    
    return comp_frames


def find_last_active_frame(frame_start_ms, frame_end_ms, time_ms, velocity, v_cutoff: float) -> int:

    """
    Returns the index of the last comparison frame where the peak |velocity|
    within [frame_start_ms[i], frame_end_ms[i]] exceeds v_cutoff.

    If v_cutoff <= 0, or no frame exceeds the threshold, returns the last frame
    index so the simulation is never trimmed below one frame.

    Args:
        frame_start_ms : Frame start times (ms)
        frame_end_ms : Frame end times (ms)
        time_ms : Full experimental time array (ms)
        velocity : Full experimental velocity array (rad/s)
        v_cutoff : Velocity threshold (rad/s); set to 0 to disable trimming

    Returns:
        Index of the last active frame (0-based)
    """

    if v_cutoff <= 0:
        return len(frame_start_ms) - 1

    last_active = -1
    for i in range(len(frame_start_ms)):
        mask = (time_ms >= frame_start_ms[i]) & (time_ms <= frame_end_ms[i])
        if mask.sum() == 0:
            continue
        if np.max(np.abs(velocity[mask])) > v_cutoff:
            last_active = i

    if last_active == -1:
        return len(frame_start_ms) - 1

    return last_active


def format_amplitude_lines(t_abq_s, v_win) -> list[str]:

    """
    Converts the time window array components (floats) to strings so they can used in the .inp file

    Args:
        t_abq_s : An array which contains the time period used by solver in s
        v_win : An array which contains the velocity used by solver in rad/s

    Returns: 
        A list containing the data ready to be printed in the loads.inp file
    """
    
    file = []
    file.append("*Amplitude, name=AMP-1, definition=TABULAR")
    for t, v in zip(t_abq_s, v_win):
        file.append("  {:.8f},  {:.8f},".format(t, v))

    return file