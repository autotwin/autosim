import scipy.io as sio
from pathlib import Path

def load_pva_mat(mat_path: Path) -> tuple:

    """
    Loads the .mat file to extract the time vector, velocity vector and frames

    Args:
        mat_path: Path to the .mat file

    Returns:
        Time vector in ms, velocity vector in rad/s
        frame center in ms, frame start in ms, and frame end in ms
    """

    mat = sio.loadmat(mat_path)
    pva = mat["PVA"][0, 0]

    time_ms = pva["time"].flatten()          
    velocity = pva["velocity"].flatten()     
    frame_center = pva["frameCenter_ms"].flatten().astype(float) 
    frame_start = pva["frameStart_ms"].flatten().astype(float)  
    frame_end = pva["frameEnd_ms"].flatten().astype(float)    

    return time_ms, velocity, frame_center, frame_start, frame_end