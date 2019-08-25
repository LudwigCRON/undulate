#!/usr/bin/env python3

import os
import cairo
import numpy as np
from datetime import datetime

from skimage.io import imread
from skimage.color import rgb2gray
from skimage.measure import compare_ssim

def generate_tmp_name():
    now = datetime.today()
    return f"_tmp_{now.strftime('%Y_%m_%d_%H_%M_%S_%s')}.jpg"

def check_similirity(ref, img, black_white: bool = False):
    if black_white:
        r = rgb2gray(ref)
        i = rgb2gray(img)
        index = compare_ssim(r, i, data_range=i.max() - i.min())
    else:
        index = compare_ssim(ref, img, data_range=img.max() - img.min(), multichannel=True)
    print(index)

def normalize_img(path: str, as_gray: bool = False):
    # if svg generate a png
    if path.endswith("svg"):
        filename = generate_tmp_name()
        os.popen(f"convert -resize 1024x1024 {path} {filename}").read()
        # create a image object
        return imread(filename, as_gray=as_gray)
    return imread(path, as_gray=as_gray)

if __name__ == "__main__":
    # convert images to PIL readable images
    ref = normalize_img("./output/wavedrom_step1.svg")
    img = normalize_img("./output/wavedrom_step1.cairo-svg")
    # check the similarity
    check_similirity(ref, ref)
    check_similirity(ref, img)
    # remove generated temp files
    os.popen("find . -name '_tmp_*' -exec rm {} +")
