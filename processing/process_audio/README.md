# HPDmobile-Processing-Audio

This repository contains the processing code for audio files used in the HPDmobile project. 

Helper files used: 
- gen_argparse.py
- my_functions.py

Author: Maggie Jacoby

## To-Do
- **Add in unpickling file.**
- Split out `process_wav` function from `Process_count_Audio.py`. 
- Check and possibly edit `Process_count_Audio.py` to fit latest practices.
- Write code to automatically subset files based on amplitude (similar to or to be used after `copy_audio.py`).
- ~~Write code to split 20-second long files into two 10-second long files.~~
- ~~Modify `4_RF_audio_occ_pred.py` to use `gen_argparse` functions.~~
- ~~Work on plotting code for wave files.~~


---
# Repository Contents

Audio was collected in 10-second long .wav files for most homes. A few early homes had 20-second long files. Audio was pickled in some cases, but for most homes raw wav files were transferred directly. 

- process_count_audio.py

    This code takes raw wav files and processes them, outputting downsampled and/or dicrete cosine transformed data in arrays. The arrays are saved as .npz files on an hourly basis. Downsampled files are intended to be used to for the public database (`*_ds.npz`) and for inferencing. 

- AudioFunctions.py

    Contains helper functions for `Process_count_Audio.py`.

- process_wav.py

    Function for processing and downsampling audio files
    To be used in Process_count_Audio.py - not implemented yet

    ### LabelingWorkflow
    - copy_audio.py

        This code is similar to `copy_img.py`. It takes in the IMAGE inferences (the 10-second frequency final CSVs, eg stored in `.../H6-black/Inference_DB/BS2/img_inf/` ) and copies the actual audio files that occur in occupied image blocks into labeled folders (eg `.../H6-black/Auto_Labeled/audio_BS2/`). Human verification is then used to confirm noise. 

    - audio_to_audio_copy.py

        This code takes files that have been separated and labeled (manually or automatically from `copy_audio.py`), and copies the same timestamp audio wave for a different hub into a labeled folder. 

    - split_way.py

        Takes 20 second wav files and splits into two 10 seconds files (appropriately timestamped).


    ### WaveFileExplorationPlotting
    - Audio_Plotting.ipynb 

        This contains starter code for plotting wave files (from raw waves and .npz files). Pretty messy and in need of documentation.

    - Plot_Audio_simple.ipynb

        Simpler code for plotting wavefiles and downsampled files.


## Inference-Audio
- audio_confidence.py
    This takes in a path to the processed audio files and outputs occupancy probabilities and decisions (0/1 based on a 50% probability cutoff).

- test_audio_classifier.py
    Takes testing/training sets and performs classifcation, reporting accuracy results.


    ### Audio_CNN
    All the model files stored in the folder `model-94_96`.

## ARCHIVE
- audio_predict.py

    Similar to `audio_confidence.py`, but doesn't output confidence level (only binary prediction). 

- load_data.py, load_saved_models.py (multiple versions)

    Previous testing code from SY.

    ### random_forest_clf
    Before switching to a convolutional neural network, inferences were done with a random forest classifer. This is the code and model for that. 

    - 4_RF_audio_occ_pred.py
    
    This takes in a path to the processed audio files and outputs occupancy decisions. 
    
    - trained_RL(3.7.6-64).joblib

        This is the old audio classifier.

---
## Workflow for labeling audio files
1. After unpickling or transferring .wav files, run image inferencing code (`HPD-Inference_and_Processing/Images/Inference-Images\confidence.py`) on the *Training Dates* subset to generate occupajncy predictions. 

2. Run `copy_audio.py` with img inferences csvs as input. Generate autolabeled folders of audio files. Upload to google drive if someone else performs step 3.

3. Listen to files and manually separate actual "noise" files. Try to include ones with human movement as well as speaking. Do this for a couple of the separated hubs (ones with different fields of view). Jasmine is helping with this part. Should have about 300-500 files total.

4. Run `audio_to_audio_copy.py` on manually confirmed hubs and other hubs. Upload to google drive if someone else does step 5.

5. Re-do step 3 on the newly identified files. 

6. Gather "quiet" files from unoccupied times or late night/early morning. Try to get a variety of street sounds, heater sounds, no sounds. Upload zip files for audio classifer training and cross testing. 



## Steps for generating inferences on Audio:
0.  a. Run `Process-Audio/extract_audioPickles.py` to unpickle audio files if necessary. Should be in
    .wav format. 

    b. If neccessary, run `Process-Audio/LabelingWorkflow/split_wav.py` to split 20 second files into 10 second files. 

1. Process using `Process-Audio/Process_count_Audio.py` to get `*_ds.npz` files (downsampled, but not discrete cosine transformed. These should be stored in `.../H6-black/BS2/processsed_audio/audio_downsampled` in folders by day, and .npz files by hour.

2. Perform inference using `Inference-Audio/audio_confidence.py` on the downsampled files.  Output is a complete daywise csv with 10-second frequency probabilities and predictions stored in `.../H6-black/Inference_DB/BS3/audio_inf/`.
