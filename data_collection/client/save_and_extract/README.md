# Overview

The `*_save.py` scripts are for saving the audio and images as pickles to facilitate transfer off
of the client antlets. 

Pickling the images made off-loading the data much quicker, while pickling the audio did not help much, 
and so was not used in the end. 

The `*_extract.py` scripts are for extracting the audio or images from the pickles, and should be
run on the computer you are using to process the collected data.
`audio_extract.py` returns CSV files with the data, instead of wav files, and was not used. 

`img_save.py` downsizes the image file from 336x336 to 112x112 pixels, and stores the result in a named tuple,
which is then pickled. 

