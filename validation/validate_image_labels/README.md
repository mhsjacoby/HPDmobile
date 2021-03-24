# Validate Image Labels

Code for validating the zone based image labels.

Helper files used: 
- gen_argparse.py
- my_functions.py

Author: Maggie Jacoby

---
# Repository Contents

- check_zone_labels.py

    This code randomly samples the zone labeled images (in CSV form), generating subsets that are supposed to be occupied or vacant. It copies the actual images into a new folder, so a human can confirm. It also generates CSVs specifying how the images were separated. 

- validate_img_labels.py

    This code takes folders of images that have been manually verified, and compares the contents of the folders against the CSV generated previously. It computes statistics on accuracy, false positive rate, etc. 

- verify_images.py

    This script looks at images predicted to be occupied, along with the ground truth files, and find times when the house is supposed to be empty, but a person was detected with the inference algorithm. The timestamps of these are printed to a CSV, so that a human can manually verify if someone is in the image, and figure out why it wasn't captured in the ground truth.


## Image_inference
This folder contains all the files that are used for generating inferences based on images. Image inferencing is done via YOLO (You Only Look Once) object detection algorithm. Additional documentation is in `/yolov5/Source-Documentation`. The trained models and weights may not be updated online because of their size. 

- confidence.py

    This is the main inferencing code, which looks at images, and generates a probability of occupied using the [YOLOv5](https://github.com/ultralytics/yolov5). The code outputs the highest confidence level, above some threshold (`default = 0.1`) from the yolov5 algorithm, as well as a binary prediciton based on a different threshold (`default = 0.5`) for every second. Input to these files is path location to stored images (eg `/Volumes/TOSHIBA-18/H6-black/`) with optional additional arguments, and output is predictions and/or confidence on a 1-second frequency in day-wise CSVs (86,400 entries per day) stored in `.../H6-black/Inference_DB/BS3/img_1sec/`. These files take a long time to run (about 20-30 minutes per day of data for a single hub, or upto 45-60 minutes if running multiple hubs simultaneously). Uses the options specified in `yolov5/detection_options.py`. Input files need to be unpickled and 112x112 pixels. Use processing files for this. Images should be stored in `.../H1-red/RS1/img-unpickled/`, then by day and by minute. 

- post_img.py
    
This takes in the daywise 1-second image csvs and averages to get a 10-second frequency. Uses maximum over the 10 seconds for both occupancy and probability. Output is stored in `.../H6-black/Inference_DB/BS3/img_inf/` in day-wise CSVs (8,640 long). Missing values are nan in pthon, blanks in the csv. Dark images below a certain threshold are shown as missing.

*yolov5*
    This folder contains all the code for the yolov5 algorithm, and was downloaded from the Ultralytics github. 