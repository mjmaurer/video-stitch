# import subprocess in case this cell is run without the above cells
import subprocess
import torch
import sys
import os
import re
from tqdm import tqdm
from PIL import Image

# Try to avoid OOM errors
torch.cuda.empty_cache()

init_frame = int(sys.argv[1])
last_frame = int(sys.argv[2])
fps = int(sys.argv[3])
cwd = os.getcwd()
output = "output.mp4"

filepath = f'{cwd}/{output}'

frames = []
# tqdm.write('Generating video...')
image_path = f'{cwd}/VQGAN-CLIP/steps/zoomed_*.png'

# cmd = [
#     'ffmpeg',
#     '-y',
#     '-vcodec',
#     'png',
#     '-r',
#     str(fps),
#     '-start_number',
#     str(init_frame),
#     '-pattern_type '
#     'glob',
#     '-i',
#     image_path,
#     '-c:v',
#     'libx264',
#     '-frames:v',
#     str(last_frame-init_frame),
#     '-vf',
#     f'fps={fps}',
#     '-pix_fmt',
#     'yuv420p',
#     '-crf',
#     '17',
#     '-preset',
#     'veryslow',
#     filepath
# ]

# process = subprocess.Popen(cmd, cwd=f'{cwd}/VQGAN-CLIP/steps/', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# stdout, stderr = process.communicate()
# if process.returncode != 0:
#     print(stderr)
#     print(
#         "You may be able to avoid this error by backing up the frames,"
#         "restarting the notebook, and running only the google drive/local connection and video synthesis cells,"
#         "or by decreasing the resolution of the image generation steps. "
#         "If these steps do not work, please post the traceback in the github."
#     )
#     raise RuntimeError(stderr)
# else:
#     print("The video is ready")
frames = []
tqdm.write('Generating video...')
for i in range(init_frame,last_frame):
    temp = Image.open(f'{cwd}/VQGAN-CLIP/steps/{str(i)}.png')
    keep = temp.copy()
    frames.append(keep)
    temp.close()
ffmpeg_filter = f"minterpolate='mi_mode=mci:me=hexbs:me_mode=bidir:mc_mode=aobmc:vsbmc=1:mb_size=8:search_param=32:fps={fps}'"
output_file = re.compile('\.png$').sub('.mp4', "output.mp4")
try:
    p = subprocess.Popen(['ffmpeg',
            '-y',
            '-f', 'image2pipe',
            '-vcodec', 'png',
            '-r', str(fps),               
            '-i',
            '-',
            # '-b:v', '10M',
            '-vcodec', 'libx264',
            # '-vcodec', 'h264_nvenc',
            '-pix_fmt', 'yuv420p',
            '-crf', '17',
            '-preset', 'veryslow',
            # '-strict', 'experimental',
            # '-filter:v', f'{ffmpeg_filter}',
        output_file], stdin=subprocess.PIPE)
except FileNotFoundError:
    print("ffmpeg command failed - check your installation")
for im in tqdm(frames):
    im.save(p.stdin, 'PNG')
p.stdin.close()
p.wait()