Author: Sin Yong Tan, 2020-08-05

--------------------
Creating Env using yml file
--------------------
Option 1:
- `conda env create -f SY_yolov5.yml`


Activate env:
- `conda activate SY_yolov5`


Option 2: (If first option doesn't work)
- `conda update conda`
- `conda create -n SY_yolov5 python==3.7 pip`
- `conda activate SY_yolov5`
- `conda install numpy==1.17`
- `conda install -c pytorch torchvision`
- `pip install -U -r requirements.txt`




--------------------
Performance on Beast
--------------------
On CPU with (112,112) images
S : ~20-30 FPS
M: ~10-20 FPS
L: ~5-15 FPS
X: ~5-10 FPS

On CPU with (336,336) images
X: ~2-7 FPS


---------
Inference
---------
images go in inference/images folder
select model with argument in detect.py (line 141 or --weights=[path to weights.pt])
Changed device argument to use cpu by default


----------
Detections
----------
Saved each detections using each model to corresponding folder names in inference/output
x2 used an image size of (336,336), the rest used (112,112)





------------
Environments (Already taken care of in first section)
------------
YOLOv5 (on Beast)
For local/no gpu
install numpy first with: conda install numpy==1.17 (gives an error with pip for some reason)
install torch with: conda install pytorch torchvision cpuonly -c pytorch
install rest of requirements from modified requirements.txt with: pip install -U -r requirements.txt




------------
Other...
------------
Homagni yolov5 installation pycocotools error fix...:
https://github.com/cocodataset/cocoapi/issues/169
