[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4655276.svg)](https://doi.org/10.5281/zenodo.4655276)


# HPDmobile

This repository contains the all the code used in connection with the mobile human presence detection system (HPDmobile) for residential occupancy detection. 

Data, which included images, sound, and indoor environmental readings, was collected from inside of residential homes. The code in this repository is divided as follows:

### Data Collection
This is the code that was used to collect the data, and includes how-tos and set-up instructions for the data acquisition system, which was based on Raspberry Pis. 

### Processing
This is code that was used to process the collected data types, both to make it easier to use, and to obfuscate images and noise, and remove any personally identifiable information.

### Validation
This contains the workflows for auto-generating subsets of labeled audio, code for validating the labeled images, and the inferencing code that was used to validate processed audio files. 

### File Management and Data Storage
This directory contains code for managing data, such as moving or renaming files, along with code for summarizing the completeness of the data. 

### Helpers
Contains some commonly used functions and JSON files with information used in subsetting and labeling the data.
