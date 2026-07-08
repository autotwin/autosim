import csv
from pathlib import Path

def write_frame_times_csv(csv_output_path: Path, comp_frames):
    
    """
    Creates the CSV file which contains info about frame time, 
    which will be used later in the post-processing scripts

    Args:
        csv_output_path: Path where csv will be saved
        comp_frames : A list of dicts containing the time of each frame in s

    """
    
    csv_path = csv_output_path / "frame_times.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=comp_frames[0].keys())
        writer.writeheader()
        writer.writerows(comp_frames)


def write_translation_metadata_csv(csv_output_path: Path, voxel_size, tx, ty, tz):

    """
    Creates the CSV file which contains info about geometry translation, 
    which will be used later in the post-processing scripts

    Args:
        csv_output_path: Path where csv will be saved
        voxel_size : Desired element size
        tx, ty, tz : Translations in the x,y,z axis for the CoG to match the 0,0,0

    """

    csv_path = csv_output_path / "translation_metadata.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["xtranslate_mm", "ytranslate_mm", "ztranslate_mm",
                         "voxel_size_mm"])
        writer.writerow([tx, ty, tz, voxel_size])
    print(f"Translation saved to: {csv_output_path}")