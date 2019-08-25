#!/usr/bin/env python3

import os
import cairo
import numpy as np

from skimage.io import imread
from skimage.color import rgb2gray
from skimage.measure import compare_ssim

def check_similirity(ref, img, black_white: bool = False):
    if black_white:
        r = rgb2gray(ref)
        i = rgb2gray(img)
        index = compare_ssim(r, i, data_range=i.max() - i.min())
    else:
        index = compare_ssim(ref, img, data_range=img.max() - img.min())
    print(index)

def normalize_img(path: str, as_gray: bool = False):
    # if svg generate a png
    if path.endswith(".svg"):
        os.popen(f"inkscape -z {path} -e _tmp.png").read()
        # create a image object
        return imread("_tmp.png", as_gray=as_gray)
    return imread(path, as_gray=as_gray)

if __name__ == "__main__":
    ref = normalize_img("./output/wavedrom_step1.svg")
    img = normalize_img("./output/wavedrom_step1.cairo-svg")
    check_similirity(ref, img)
