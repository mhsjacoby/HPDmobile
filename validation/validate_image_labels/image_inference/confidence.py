"""
detect.py
Author: Sin Yong Tan 2020-08-04
Based on code from: https://github.com/ultralytics/yolov5
Updates by Maggie Jacoby 
    2020-08-24: new branch for my edits, change input format

This is the first step of inferencing code for images in the HPDmobile
Inputs: path the folder (home, system, hub specific), which contain 112x112 png images
Outputs: csv with 0/1  occupancy by day

A median filter is first applied to the images (default filter size = 3)

Run this:
python detect.py -path /Users/maggie/Desktop/ -H 1 -sta_num 1 -sta_col G
    optional arguments: 
                        -hub (if only one hub is to be run, default is to run all in the folder)
                        -save_location (if different from read path)
                        -start_index (file number, default is 0)
                        -number_files (previously end index. Default is 4)
                        -img_file_name (default is whatever starts with "img" eg, "img-downsized" or "img-unpickled")

==== SY Notes ====
Keep save_img and save_txt, update them to save_occ and save_csv(or save_json) later, depending on need

How to save the labeled data with >1 bounding box?

Check chronological order of the saving in csv (should be sorted ady) 

runs around 14~16 FPS
"""

import argparse
import torch.backends.cudnn as cudnn
# from yolov5 import *
from yolov5.utils.datasets import *
from yolov5.utils.utils import *
# from utils.datasets import *
# from utils.utils import *
import cv2
import datetime
import time
import sys
import pandas as pd
import numpy as np


import warnings
warnings.filterwarnings("ignore")

from my_functions import *



def detect():

    minute_fname, minute_occupancy, minute_conf = [], [], []
    source, save_txt, imgsz = args.source, args.save_txt, args.img_size

    dataset = LoadImages(source, img_size=imgsz)

    # Run inference
    for path, img, _, _ in dataset:
        fname = os.path.basename(path).split("_")
        fname = fname[0] + " " + fname[1]
        minute_fname.append(fname)

        # ==== Added Median Filtering Here ====
        # img = cv2.medianBlur(img, args.filter_size)

        img = torch.from_numpy(img).to(device)        
        img = img.float()  # uint8 to fp32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        pred = model(img, augment=args.augment)[0]
        # Apply NMS
        pred = non_max_suppression(pred, args.conf_thres, args.iou_thres, classes=[0], agnostic=args.agnostic_nms)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            M = 0
            if det is not None:
                M = max([float(x[4]) for x in det])
            minute_conf.append(M)
            minute_occupancy.append(0 if det is None or M < args.occ_threshold else 1)                
    return minute_fname, minute_occupancy, minute_conf






if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Model arg: No changes needed
    parser.add_argument('--weights', type=str, default='yolov5/weights/yolov5s.pt', help='model.pt path')
    # parser.add_argument('--weights', type=str, default='yolov5/weights/yolov5x.pt', help='model.pt path')
    parser.add_argument('--source', type=str, default='inference/images', help='source')  # file/folder to read the img (constantly loops in the code)
    parser.add_argument('--img-size', type=int, default=128, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.1, help='object confidence threshold for writing data')
    parser.add_argument('--occ_threshold', type=float, default=0.5, help='object confidence threshold for saving data')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--fourcc', type=str, default='mp4v', help='output video codec (verify ffmpeg support)')
    parser.add_argument('--device', default='cpu', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')


    parser.add_argument('-f_sz', '--filter_size', type=int, default=3, help='Apply median filter to input img') # Added median filtering option
    parser.add_argument('-img_file_name', '--img_fname', default='', type=str, help='Name of subfolder containing images')

    # Standard arguments
    parser.add_argument('-path','--path', default="AA", type=str, help='path of stored data')
    parser.add_argument('-hub', '--hub', default="", nargs="+", type=str, help='if only one hub... ') # Example: python time_window.py -hub BS2 BS3
    parser.add_argument('-save_location', '--save', default='', type=str, help='location to store files (if different from path')
    parser.add_argument('-start_date','--start', default='', type=str, help='Processing START Date index')
    parser.add_argument('-end_date','--end', default='', type=str, help='Processing END Date index')
    # parser.add_argument('-number_files', '--end_date_index', default=10, type=int, help='Number of files to read')

    args = parser.parse_args()
    args.img_size = check_img_size(args.img_size)

    path = args.path
    home_system = path.strip('/').split('/')[-1]
    H = home_system.split('-')
    H_num, color = H[0], H[1][0].upper()

    save_path = os.path.join(args.save, home_system) if len(args.save) > 0 else path

    hubs = args.hub if len(args.hub) > 0 else sorted(mylistdir(path, bit=f'{color}S', end=False))
    print(f'List of Hubs: {hubs}')

    start_date = args.start
    end_date = args.end
    

    for hub in hubs:

        img_fnames = [args.img_fname] if len(args.img_fname) > 0 else mylistdir(os.path.join(path, hub), bit='img', end=False)

        if len(img_fnames) > 1:
            print(f'Multiple images files found in hub {hub}: {img_fnames}. \n System Exiting.')
            sys.exit()
        
        print(f'Reading images from file: {img_fnames[0]}')

        read_root_path = os.path.join(path,hub,img_fnames[0],"*")
        dates = sorted(glob.glob(read_root_path))
        print(dates)

        if len(dates) == 0:
            print(f'No dates in file: {read_root_path}. Exiting Program.')
            sys.exit()


        end_date =  os.path.basename(dates[-1]).strip('.csv') if not end_date else end_date
        dates = [x for x in dates if os.path.basename(x) >= start_date and os.path.basename(x) <= end_date]
		# dates = [x for x in dates if os.path.basename(x) >= start_date]
        print('Dates:', len(dates))

        save_root_path = make_storage_directory(os.path.join(save_path,'Inference_DB', hub, 'imgX_1sec'))
        print("save_root_path: ", save_root_path)
		

        # ================ Move Model loading etc here ================
        # Initialize
        device = torch_utils.select_device(args.device) # Prints "Using CPU"

        # Load model
        model = torch.load(args.weights, map_location=device)['model'].float()  # load to FP32
        model.to(device).eval()

        start = time.time()

        D = 0    # Keep track of days analysed this session
        for date_folder_path in dates:
            date = os.path.basename(date_folder_path)
            if not date.startswith('20'):
                print(f'passing folder: {date}')
                continue

            prev_file = os.path.join(save_path,'Inference_DB', hub, 'img_1sec', f'{date}.csv')
            prev_infs = pd.read_csv(prev_file, index_col = 'timestamp')
            idx = pd.DatetimeIndex(prev_infs.index)
            prev_infs.index = idx


            print(f"Loading date folder: {date} ...")


            ''' Check if Directory is empty '''
            times = os.listdir(date_folder_path)

            if len(times) == 0: 
                print(f"Date folder {os.path.basename(date_folder_path)} is empty")
            else:
                day_start = datetime.datetime.now()
                # Created day-content placeholder
                day_fname, day_occupancy, day_conf = [], [], []            
                date_folder_path = os.path.join(date_folder_path,"*")
                
                for time_folder_path in sorted(glob.glob(date_folder_path)):
                    time_f = os.path.basename(time_folder_path)
                    if int(time_f)%100 == 0:
                        print(f"Checking time folder: {time_f} ...")

                    imgs = os.listdir(time_folder_path)

                    if len(imgs) == 0:
                        print(f"Time folder {os.path.basename(time_folder_path)} is empty")

                    else:
                        # Update source folder
                        args.source = time_folder_path # 1 min folder ~ 60 img

                        with torch.no_grad():
                            min_fname, min_occ, min_conf = detect() # detect this time folder
                            day_fname.extend(min_fname)
                            day_occupancy.extend(min_occ)
                            day_conf.extend(min_conf)

                D += 1 # Keep track of days analysed this session

                day_fname = [date_[:11]+date_[11:13]+":"+date_[13:15]+":"+date_[15:17] for date_ in day_fname] # date formatting
                day_fname = [datetime.datetime.strptime(date_, '%Y-%m-%d %H:%M:%S') for date_ in day_fname] # date formatting

                save_data = np.vstack((day_fname, day_occupancy, day_conf))
                save_data = np.transpose(save_data)
                np.savetxt(os.path.join(save_root_path,f'{date}_x.csv'), save_data,
                            delimiter=',',fmt='%s',header="timestamp,occupied,probability",comments='')
                # print(day_fname)

                

                new_df = pd.DataFrame(save_data, columns=['timestamp', 'occupied', 'probability'])
                new_df.index = new_df['timestamp']
                new_df.drop(columns=['timestamp'], inplace=True)

                combined_df = pd.concat([new_df['occupied'], prev_infs['occupied'], new_df['probability'], prev_infs['probability']], axis=1)
                combined_df.columns = ['modelX occ', 'modelS occ', 'modelX prob', 'modelS prob']
                # combined_df['diff'] = combined_df['modelX'] - combined_df['modelS']
                # print(combined_df)
                # print(combined_df.isna().sum())
                
                # diffs = combined_df[combined_df.columns.difference(['', 'D'])]
                small_df = combined_df.dropna()
                small_df['diff'] = small_df['modelX occ'] - small_df['modelS occ']
                small_df['prob diff'] = small_df['modelX prob'] - small_df['modelS prob']

                diff_df = small_df.loc[small_df['diff'] != 0]
                # print(diff_df)
                diff_save_loc = make_storage_directory(f'/Users/maggie/Desktop/DF_differences/{H_num}/{hub}')
                diff_df.to_csv(os.path.join(diff_save_loc, f'{date}_diff.csv'), index_label='timestamp')

                print('diff', small_df['diff'].sum())
                
                print('prob diff', small_df['prob diff'].sum())
                
                

                # sys.exit()

                day_end = datetime.datetime.now()
                print(f"Time to process day {date} on hub {hub}: {str(day_end-day_start).split('.')[0]}")
                print(f'Current time is: {datetime.datetime.now().strftime("%m-%d %H:%M")}')

        end = time.time()
        total_time = (end-start)/3600
        print(f'Total time taken to process {D} days on {hub}: {total_time:.2} hours')
        
