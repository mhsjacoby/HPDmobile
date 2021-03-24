# HPDmobile Validation

This repository contains the all the code used to process data collected in the HPDmobile project, before publishing publicly. 

Helper files used: 
- gen_argparse.py
- my_functions.py

Author: Maggie Jacoby

---
# Repository Contents

## Auto-labeling

- copy_audio.py

    This code is similar to `copy_img.py`. It takes in the IMAGE inferences (the 10-second frequency final CSVs, eg stored in `.../H6-black/Inference_DB/BS2/img_inf/` ) and copies the actual audio files that occur in occupied image blocks into labeled folders (eg `.../H6-black/Auto_Labeled/audio_BS2/`). Human verification is then used to confirm noise. 

- audio_to_audio_copy.py

    This code takes files that have been separated and labeled (manually or automatically from `copy_audio.py`), and copies the same timestamp audio wave for a different hub into a labeled folder. 

- copy_move_audio.py


- plot_audio.py


## Validate Image Labels



## Validate Processed Audio
