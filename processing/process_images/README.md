# HPDmobile-Processing-Audio

This repository contains the processing code for audio files used in the HPDmobile project. 

Helper files used: 
- gen_argparse.py
- my_functions.py

Author: Maggie Jacoby

---
# Repository Contents

After images were collected by the HPDmobile system, they were either pickled and then transferred (most of the homes), or transferred directly (first few homes).

Images were captured in grey-scale, every second, at 336x336 pixels.

- Image_Resize.py / Image_Resize_unpickled.py

    This code takes images that were exported at 336x336 (without pickling), and resizes them to 112x112 pixels. This is only needed in the homes where the images were not pickled. 

    This code can also be configured to resize the 112x112 images to 32x32 pixels, as stored for the public database. 

- copy_img.py

    This code looks at the inferences created (at 1 second frequency) and copies the files into labeled folders, depending on classification confidence level.