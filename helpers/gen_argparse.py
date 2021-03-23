"""
gen_argparse.py
general argument parsers that are used in a variety of detection, inference and file reading codes. 
usage: python3 arg_test.py -path /Volumes/TOSHIBA-21/H1-red/ -hub RS1 RS2

employed in:
	- copy_img.py
	- copy_audio.py

not yet in:
	- detect.py and confidence.py (image detection using yolov5)
	- audio classification
	- grouping files
"""


# ==== Usage ====
import os
import argparse
from my_functions import *

parser = argparse.ArgumentParser(description="Description")

parser.add_argument('-path','--path', default='', type=str, help='path of stored data') # Stop at house level, example G:\H6-black\
parser.add_argument('-save_location', '--save', default='', type=str, help='location to store files (if different from path')
parser.add_argument('-hub', '--hub', default="", nargs="+", type=str, help='if only one hub... ') # Example: python time_window.py -hub BS2 BS3
parser.add_argument('-start_date', '--start', default='', type=str, help='type day to start')
parser.add_argument('-end_date', '--end', default='', type=str, help='type day to end')

# used only for image copying
parser.add_argument('-img_name', '--img_name', default='img-unpickled', type=str, help='name of files containing raw images')

args = parser.parse_args()
path = args.path

home_system = os.path.basename(path.strip('/'))
H = home_system.split('-')
H_num, color = H[0], H[1][0].upper()

save_root = os.path.join(args.save, home_system) if len(args.save) > 0 else path

hubs = args.hub if len(args.hub) > 0 else sorted(mylistdir(path, bit=f'{color}S', end=False))

start_date = args.start
end_date = args.end


img_name = args.img_name

__all__ = [
	"path",
	"save_root",
	"home_system",
	"H",
	"H_num",
	"color",
	"hubs",
	"start_date",
	"end_date",
	"img_name"
]