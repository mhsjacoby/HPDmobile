# HPDmobile File Management and Data Storage

This repository contains the all the code used to get generate summaries about the data, and to get it ready for the public release. 

Helper files used: 
- gen_argparse.py
- my_functions.py
- start_end_dates.json

---
# Repository Contents

- process_HPD_files_for_storage.ipynb

    A jupyter notebook that was run right before publishing the data. Depending on the modality, this code may:

    - rename the directories
    - subset the days of interest
    - copy files to a new location
    - zip the final data
    - writes the zone labels

## Summarize Data
Some code for reading in the files name or file contents, and determining the completeness of the modalities.


## File Handling
Code (run in jupyter notebooks) for renaming and moving files.