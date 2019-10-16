#!/usr/bin/env python3

import os
import glob
import cairo
import numpy as np
from datetime import datetime

import scipy.ndimage as ndimage
from skimage.io import imread
from skimage.color import rgb2gray
from skimage.measure import compare_ssim

def generate_tmp_name():
    now = datetime.today()
    return "_tmp_%s.jpg" % now.strftime('%s')

def check_similarity(ref, img, black_white: bool = False):
    if black_white:
        r = rgb2gray(ref)
        i = rgb2gray(img)
        return compare_ssim(r, i, win_size=9, data_range=i.max() - i.min())
    return compare_ssim(ref, img, win_size=9, data_range=img.max() - img.min(), multichannel=True)

def check_similarity2(ref, img, black_white: bool = False):
    if black_white:
        r = rgb2gray(ref)
        i = rgb2gray(img) 
    else:
        r = ref
        i = img
    r = ndimage.gaussian_filter(r, sigma=(5, 5), order=0)
    i = ndimage.gaussian_filter(i, sigma=(5, 5), order=0)
    dif = np.sum(np.abs(r - i))
    ncomponents = ref.shape[0] * ref.shape[1] * ref.shape[2] if len(ref.shape) == 3 else ref.shape[0] * ref.shape[1]
    return 100*(dif / 255 / ncomponents)

def normalize_img(path: str, as_gray: bool = False, is_ref: bool = False, width: int = 1024, height: int = 1024):
    # if svg generate a png
    if path.endswith("svg") or path.endswith("eps") or path.endswith("pdf"):
        filename = generate_tmp_name()
        if is_ref:
            os.popen("convert -density 300 -trim -resize %dx%d -background white -compose Copy -gravity center %s %s" % (width, height, path, filename)).read()
        else:
            os.popen("convert -density 300 -trim -resize %dx%d -background white -compose Copy -gravity center -extent %dx%d %s %s" % (width, height, width, height, path, filename)).read()
        # create a image object
        return imread(filename, as_gray=as_gray)
    return imread(path, as_gray=as_gray)

if __name__ == "__main__":
    # check extension
    exts = [".cairo-svg", ".eps"]
    max_len = max(list(map(len, exts)))
    # get list of reference files *.svg
    references = glob.glob("./output/wavedrom_step*.svg")
    try:
        for k, reference in enumerate(references):
            s = "[%d/%d}]\t%s: " % (k, len(references), reference)
            print(s)
            print(''.join(['-']*len(s)))
            # convert images to PIL readable images
            ref = normalize_img(reference, False, True, 1024, '')
            # extract size
            # print(ref.shape)
            if len(ref.shape) == 3:
                h, w, _ = ref.shape
            else:
                h, w = ref.shape
            #width, height = ref.size
            for ext in exts:
                img = normalize_img(reference.replace(".svg", ext), False, False, w, h)
                # check the similarity
                i = check_similarity2(ref, img, True)
                n_tab = 1+(max_len - len(ext))//4
                print("\t%s" % reference.replace('.svg', ext) + ''.join(['\t']*n_tab)+"%0.3f %" % i)
    finally:
        # remove generated temp files
        os.popen("find . -name '_tmp_*' -exec rm {} +")
        #pass
