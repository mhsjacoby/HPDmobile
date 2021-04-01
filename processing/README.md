# HPDmobile Processing

This repository contains the all the code used to process data collected in the HPDmobile project, before publishing publicly. 

Helper files used: 
- gen_argparse.py
- my_functions.py

---
# Repository Contents

## Audio 
Audio was collected in 10-second long .wav files for most homes. A few early homes had 20-second long files. Audio was pickled in some cases, but for most homes raw wav files were transferred directly. The code here reads in the audio files and processes to downsize or (if desired) filter and perform a discrete cosine transform (DCT). Files are saved as CSV.

- process_count_audio.py

    This code takes raw wav files and processes them, outputting downsampled and/or dicrete cosine transformed data in arrays. The arrays are saved as .npz files on an hourly basis. Downsampled files are intended to be used for the public database (`*_ds.npz`) and for inferencing. 

- AudioFunctions.py

    Contains audio processing helper functions for `process_count_audio.py`.

- extract_audioPickles.py

    This files takes a list of pickled objects and extracts the audio files to .csv.
    The pickled objects are organized by hour. Extracts audio that were pickled with `audio_save.py`
    in the `data_collection/client` directory

- save_as_wav.py

    This function takes csv files and changes them back into wav files.
    It was used for testing the reconstructability of audio processing steps.

- split_way.py

    Takes 20 second wav files and splits into two 10 seconds files (appropriately timestamped).


## Images
Images were captured in grey-scale, every second, at 336x336 pixels. After images were collected by the HPDmobile system, they were either pickled and then transferred (most of the homes), or transferred directly (first few homes). The code here resizes the images. Images are saved as PNG. 

- Image_Resize.py / Image_Resize_unpickled.py

    This code takes images that were exported at 336x336 (without pickling), and resizes them to 112x112 pixels. This is only needed in the homes where the images were not pickled. 

    This code can also be configured to resize the 112x112 images to 32x32 pixels, as stored for the public database. 

- copy_img.py

    This code looks at the inferences created (at 1 second frequency) and copies the files into labeled folders, depending on classification confidence level.


## Environmental
Environmental data was captured every 10 seconds and stored in JSON files. The code here reads in the JSON files and creates pandas data frames. Processing (such as outlier removal) can be performed if desired. Data is stored as CSV. 


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


## Occupancy

- calculate_groundtruth.py 

    Reads in the raw "enter/exit" files for all persons in a home, and creates a pandas dataframe with occupancy for the home and occupancy counts. Saves this by day. 


