# HPDmobile-Processing-Audio

This repository contains the processing code for audio files used in the HPDmobile project. 

Helper files used: 
- gen_argparse.py
- my_functions.py

Author: Maggie Jacoby

---
# Repository Contents

Audio was collected in 10-second long .wav files for most homes. A few early homes had 20-second long files. Audio was pickled in some cases, but for most homes raw wav files were transferred directly. 

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