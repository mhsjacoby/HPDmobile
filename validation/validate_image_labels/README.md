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
    This folder contains all the files that are used for generating inferences based on images. 

    - confidence.py

        This is the main inferencing code, which looks at images, and generates a probability of occupied using the [YOLOv5](https://github.com/ultralytics/yolov5) object detection algorithm. 

    - post_img.py
        
        This code takes the inferences generated on a one-second basis, and aggegates them to a ten-second basis.

    *yolov5*
        This folder contains all the code for the yolov5 algorithm, and was forked from them. 
