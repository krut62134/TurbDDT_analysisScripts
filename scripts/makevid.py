import yt
import subprocess

# Define the ffmpeg command as a list of arguments
command = [
    "ffmpeg",
    "-start_number", "000001",
    "-i", "tDDT_hdf5_plt_cnt_%06d_combined_slice.png",
    "-c:v", "libx264",
    "-r", "30",
    "-pix_fmt", "yuv420p",
    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
    "video.mp4"
]

# Run the command
subprocess.run(command, check=True)

