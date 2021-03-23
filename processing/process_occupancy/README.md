# HPD-Processing-Occupancy

This repository contains the occupancy processing code for the HPDmobile project.

Helper files used: 
- gen_argparse.py
- my_functions.py

Author: Maggie Jacoby

---
# Repository Contents

- calculate_groundtruth.py 

    Reads in the raw "enter/exit" files for all persons in a home, and creates a pandas dataframe with occupancy for the home and occupancy counts. Saves this by day. 
