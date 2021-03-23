# HPD-Inference-Environmental ReadMe

This repository contains the environmental processing and inferencing code for the HPDmobile project.

Helper files used: 
- gen_argparse.py
- my_functions.py

Author: Maggie Jacoby


## To-Do
- Write up cleaning processes
- Move helper functions to subfolder
- add `post_env.py` call to `env_confidence.py`
- Modify inferencing code to use Sin Yong's STPN python package! 
- ~~Write up steps for performing inferencing.~~

## Processing-Environmental
- ProcessEnvData.py
    
    Run this on the originally collected env data (stored in .json files). This is the only processing file that needs to be run directly.  Outputs 4 different things:
        - CSVs cleaned (by day and by hub)
        - CSVs raw (by day and by hub)
        - Aggregated cleaned CSVs by hub -> these are used in the inferencing code
        - Aggregated raw CSVs by hub
    Cleaned CSVs contain infomration (binary) on which time points/modalities were cleaned

- HomeDataClasses.py
    Contains a class that which takes care of the reading and processing of the env files.

- cleanData.py
    Contains a function that is called in the HomeData class and actually performs the data cleaning. **Write more about this**

- Full_env_processing.ipynb
    code that was originally used for reading and combining the json files. Still used to generate CSVs for training. Does Minimal processing, but creates full CSVs, joins all days, and finds "complete" splits. 

## Inferencing-Environmental
- env_confidence.py

    This takes in the processed env data and performs inferences. Output is CSVs by hub and by modality, with binary decision and probability.

- post_env.py
    
    This takes the files by modality, and combines them into files by hub. Output is consistent with other modalities. 

- utility_func.py

    Contains helper functions for inferencing. 


## ARCHIVE
    Contains a few Jupyter notebooks where the above scripts were originally written. 

## Steps for processing and generating inferences on environmental modalities 
1. Run `Process-Environmental/ProcessEnvData.py` to get CSVs.

2. Run `Inference-Environmental/env_confidence.py` to get modality wise CSVs.

3. Run `Inference-Environmental/post_env.py` to combine modalities into one CSV per hub.