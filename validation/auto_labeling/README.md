## Auto-Labeling

This contains 

Helper files used: 
- gen_argparse.py
- my_functions.py

Author: Maggie Jacoby

---
# Repository Contents

- copy_audio.py

    This code is similar to `copy_img.py`. It takes in the IMAGE inferences (the 10-second frequency final CSVs, eg stored in `.../H6-black/Inference_DB/BS2/img_inf/` ), looks for high probabilit occupied times, as predicted by the images, and copies the actual audio files that occur in occupied image blocks into labeled folders (eg `.../H6-black/Auto_Labeled/audio_BS2/`). Human verification is then used to confirm noise in the files.

- plot_audio.py

    Generates a plot of a single wav file.