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
from skimage.morphology import closing, square, opening
from skimage.measure import regionprops
from skimage.color import label2rgb
from trymageAnalysis import ImageAnalysis
from skimage.io import imread

Rawimgbef = imread("D:/111out.tif", as_gray=True)
Rawimgaft = imread("D:/111out.tif", as_gray=True)
#Rawimgbef = cv2.imread('D:\\regiontest1.png',0)
#Rawimgaft = cv2.imread('D:\\regiontest1.png',0)
img_before = Rawimgbef#[0:190, 0:250]#[0:22, 0:400]#[140:190, 155:205]#[200:400,300:500]#[483:483+600,690:690+600]  #crop image
img_after = Rawimgaft#[0:190, 0:250]#[0:22, 0:400]#[140:190, 155:205]#[200:400,300:500]#[483:483+600,690:690+600]

S = ImageAnalysis(img_before, img_after)
v1, v2, bw, thres = S.applyMask()
R = S.ratio(v1, v2)
L, cp, coutourmask, coutourimg, sing = S.get_intensity_properties(100, bw, v2, thres, v2, -1500, -1500, 7)
S.showlabel(100, bw, v2, thres, -1500, -1500, cp)
#Fill, sliced, inten= S.showlabel(1000, bw, v2, thres, -1500, -1500, cp)
print (L)
print (cp)

Rawimgbef1 = imread("D:/222out.tif", as_gray=True)
Rawimgaft1 = imread("D:/222out.tif", as_gray=True)
#Rawimgbef = cv2.imread('D:\\regiontest1.png',0)
#Rawimgaft = cv2.imread('D:\\regiontest1.png',0)
img_before1 = Rawimgbef1#[0:190, 0:250]#[0:22, 0:400]#[140:190, 155:205]#[200:400,300:500]#[483:483+600,690:690+600]  #crop image
img_after1 = Rawimgaft1

S = ImageAnalysis(img_before1, img_after1)
v1, v2, bw, thres = S.applyMask()
R = S.ratio(v1, v2)
L1, cp1, coutourmask, coutourimg, sing = S.get_intensity_properties(100, bw, v2, thres, v2, -2500, -2500, 7)
S.showlabel(100, bw, v2, thres, -2500, -2500, cp1)
#Fill, sliced, inten= S.showlabel(1000, bw, v2, thres, -1500, -1500, cp)
print (L1)
print (cp1)

print('...........Original ..........')

loopnum = 1
All_cell_properties_dict = {}
All_cell_properties_dict[0] = []
All_cell_properties = []

All_cell_properties_dict[1] = cp
All_cell_properties_dict[2] = cp1
if loopnum != 0:
    All_cell_properties = np.append(All_cell_properties_dict[1], All_cell_properties_dict[2], axis=0)
else:
    pass
All_cell_properties = cp1
# Put all results in one

# Label the original order
original_dtype = np.dtype(All_cell_properties.dtype.descr + [('Original_sequence', '<i4')])
original_cp = np.zeros(All_cell_properties.shape, dtype=original_dtype)
original_cp['Row index'] = All_cell_properties['Row index']
original_cp['Column index'] = All_cell_properties['Column index']
original_cp['Mean intensity'] = All_cell_properties['Mean intensity']
original_cp['Circularity'] = All_cell_properties['Circularity']
original_cp['Mean intensity in contour'] = All_cell_properties['Mean intensity in contour']
original_cp['Original_sequence'] = list(range(0, len(All_cell_properties)))

print (original_cp['Mean intensity in contour'])
print('*********************sorted************************')
#sort
sortedcp = np.flip(np.sort(original_cp, order='Mean intensity in contour'), 0)
selected_num = 10 #determine how many we want
#unsorted_cp = All_cell_properties[:selected_num]
#targetcp = sortedcp[:selected_num]

rank_dtype = np.dtype(sortedcp.dtype.descr + [('Ranking', '<i4')])
ranked_cp = np.zeros(sortedcp.shape, dtype=rank_dtype)
ranked_cp['Row index'] = sortedcp['Row index']
ranked_cp['Column index'] = sortedcp['Column index']
ranked_cp['Mean intensity'] = sortedcp['Mean intensity']
ranked_cp['Circularity'] = sortedcp['Circularity']
ranked_cp['Mean intensity in contour'] = sortedcp['Mean intensity in contour']
ranked_cp['Original_sequence'] = sortedcp['Original_sequence']
ranked_cp['Ranking'] = list(range(0, len(All_cell_properties)))

print (ranked_cp['Mean intensity in contour'])
print('***********************Original sequence with ranking**************************')

#back to original sequence with ranking
withranking_cp = np.sort(ranked_cp, order='Original_sequence')
print (withranking_cp['Mean intensity in contour'])

S = ImageAnalysis(img_before1, img_after1)
S.showlabel_with_rank(100, bw, v2, thres, -1500, -1500, withranking_cp, 'Mean intensity in contour', 10)
