"""
copy_img.py
Author: Sin Yong Tan 2020-09-10
Updates by Maggie Jacoby
	2020-09-15: move argument parser to separate file

This code takes in image occupancy prediction files and copies images to another folder, specifed by condifdence level
	
==== Input ====
mode == img:
input is 1S predictions. Copy into image files depending on probability (10%, 20%,... etc)
"""


import os
import sys
import argparse
import pandas as pd

from glob import glob
from natsort import natsorted

import shutil

from gen_argparse import *
from my_functions import *


if __name__ == '__main__':
	# uses arguments specifed by gen_argparse.py

	print(f'List of Hubs: {hubs}')

	mode = 'img'

	for hub in hubs:
		infer_csv_path = os.path.join(path, 'Inference_DB', hub, 'img_1sec', '*.csv')

		save_path = make_storage_directory(os.path.join(save_root, 'Auto_Labled', f'{mode}_{hub}'))
		days = [day for day in sorted(glob(infer_csv_path))]

		if len(days) == 0:
			print(f'No days in folder: {infer_csv_path}. Exiting program.')
			sys.exit()

		end_date =  os.path.basename(days[-1]).strip('.csv') if not end_date else end_date
		days = [day for day in days if os.path.basename(day).strip('.csv') <= end_date]

		print(f'Number of days: {len(days)}')

		for day in days:
			day_name = os.path.basename(day).strip('.csv')

			all_data = pd.read_csv(day,index_col=0)
			all_data.index = pd.to_datetime(all_data.index)
			all_data["day"] = all_data.index.date
			all_data["time"] = all_data.index.time

			print(f'{day}: {max(all_data["probability"])}, {min(all_data["probability"])}')
			for x in range(0,100,10):

				data = all_data[(all_data['probability']*100 >= x) & (all_data['probability']*100 <= x+10)] # select "occupied" timestamp
				save_folder = make_storage_directory(os.path.join(save_path, f'greater_than_{x}') )
	
				copy_paths_root = os.path.join(path, hub, img_name)
				copy_paths = [os.path.join(copy_paths_root,f"{data['day'][i]}",f"{data['time'][i]}".replace(":","")[:4],"*"+f"{data['time'][i]}".replace(":","")+"*") for i in range(len(data['time']))]
				for copy_path in copy_paths:
					print(copy_path)
					src = natsorted(glob(copy_path))

					if len(src) == 0:
						print(f'No file in: {copy_path}')

					else:
						if len(src) >= 2:
							print(f"{copy_path} has {len(src)} {mode} with the same 'time'!")
						src = src[0]
						fname = os.path.basename(src)
						dest = os.path.join(save_folder, fname)
						shutil.copy(src, dest)