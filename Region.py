# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 17:58:53 2019

@author: xinmeng
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from skimage import data
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label
from skimage.morphology import closing, square
from skimage.measure import regionprops
from skimage.color import label2rgb

Rawimgbef = cv2.imread('E:\\Delft\\Code\\python\\Python_test\\Archon2.tif',0)
Rawimgaft = cv2.imread('E:\\Delft\\Code\\python\\Python_test\\Archon1.tif',0)


img_before = Rawimgbef[483:483+600,690:690+600]  #crop image
img_after = Rawimgaft[483:483+600,690:690+600]

fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
ax.imshow(img_before)# fig 1

thresh = threshold_otsu(img_before)
#mask = img_before > thresh # generate mask
bw = closing(img_before > thresh, square(3))
mask = closing(img_before > thresh, square(3))

fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
ax.imshow(bw)# fig 2

Segimg_bef = mask*img_before
Segimg_aft = mask*img_after

fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
ax.imshow(Segimg_bef) #fig 3

Segimg_bef_ratio = np.where(Segimg_bef == 0, 1, Segimg_bef)
Ratio = Segimg_aft/Segimg_bef_ratio

fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
ax.imshow(Ratio) #fig 4

# remove artifacts connected to image border
cleared = bw.copy()
clear_border(cleared)

# label image regions
label_image = label(cleared)
#image_label_overlay = label2rgb(label_image, image=image)

fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
ax.imshow(label_image)

for region in regionprops(label_image,intensity_image=Ratio):

    # skip small images
    if region.area < 100:
        continue

    # draw rectangle around segmented coins
    minr, minc, maxr, maxc = region.bbox
    rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                              fill=False, edgecolor='red', linewidth=2)
    ax.add_patch(rect)
    centroidint1 = int(region.centroid[0])
    centroidint2 = int(region.centroid[1])
    ax.text(centroidint1+50, centroidint2+55, round(region.mean_intensity,3),fontsize=15,
                    style='italic',bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
    print(region.mean_intensity)

plt.show() # fig 5