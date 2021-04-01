## Auto-Labeling

This contains 

Helper files used: 
- gen_argparse.py
- my_functions.py

---
# Repository Contents

- copy_audio.py

    This code is similar to `copy_img.py`. It takes in the IMAGE inferences (the 10-second frequency final CSVs, eg stored in `.../H6-black/Inference_DB/BS2/img_inf/` ), looks for high probability occupied times, as predicted by the images, and copies the actual audio files that occur in occupied image blocks into labeled folders (eg `.../H6-black/Auto_Labeled/audio_BS2/`). Human verification is then used to confirm noise in the files.

- plot_audio.py

    Generates a plot of a single wav file.

## Workflow for labeling audio files
1. After unpickling or transferring wav files, run image inferencing code (`*/inference_images\confidence.py`) on the *Training Dates* subset to generate occupancy predictions. 

2. Run `copy_audio.py` with img inference csvs as input. Generate autolabeled folders of audio files.

3. Listen to files and manually separate actual "noise" files. Try to include ones with human movement as well as speaking. Do this for a couple of the separated hubs (ones with different fields of view). Jasmine is helping with this part. Should have about 300-500 files total.