"""Exports a YOLOv5 *.pt model to *.onnx and *.torchscript formats

Usage:
    $ export PYTHONPATH="$PWD" && python models/export.py --weights ./weights/yolov5s.pt --img 640 --batch 1
"""

import argparse

import onnx

from models.common import *
from utils import google_utils

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='./yolov5s.pt', help='weights path')
    parser.add_argument('--img-size', nargs='+', type=int, default=[640, 640], help='image size')
    parser.add_argument('--batch-size', type=int, default=1, help='batch size')
    opt = parser.parse_args()
    opt.img_size *= 2 if len(opt.img_size) == 1 else 1  # expand
    print(opt)

    # Input
    img = torch.zeros((opt.batch_size, 3, *opt.img_size))  # image size, (1, 3, 320, 192) iDetection

    # Load PyTorch model
    google_utils.attempt_download(opt.weights)
    model = torch.load(opt.weights, map_location=torch.device('cpu'))['model'].float()
    model.eval()
    model.model[-1].export = True  # set Detect() layer export=True
    _ = model(img)  # dry run

    # Export to torchscript
    try:
        f = opt.weights.replace('.pt', '.torchscript')  # filename
        ts = torch.jit.trace(model, img)
        ts.save(f)
        print('Torchscript export success, saved as %s' % f)
    except:
        print('Torchscript export failed.')

    # Export to ONNX
    try:
        f = opt.weights.replace('.pt', '.onnx')  # filename
        model.fuse()  # only for ONNX
        torch.onnx.export(model, img, f, verbose=False, opset_version=11, input_names=['images'],
                          output_names=['output'])  # output_names=['classes', 'boxes']

        # Checks
        onnx_model = onnx.load(f)  # load onnx model
        onnx.checker.check_model(onnx_model)  # check onnx model
        print(onnx.helper.printable_graph(onnx_model.graph))  # print a human readable representation of the graph
        print('ONNX export success, saved as %s\nView with https://github.com/lutzroeder/netron' % f)
    except:
        print('ONNX export failed.')
