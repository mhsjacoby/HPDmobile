# HPD-Processing-Environmental

This repository contains the environmental processing and inferencing code for the HPDmobile project.

Helper files used: 
- gen_argparse.py
- my_functions.py

Author: Maggie Jacoby

---
# Repository Contents

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

