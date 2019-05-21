# -*- coding: utf-8 -*-
"""
Created on Mon May 20 17:51:19 2019

@author: xinmeng
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math
from skimage import data
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, perimeter, find_contours
from skimage.morphology import closing, square, dilation
from skimage.measure import regionprops

class imageanalysistoolbox():
    def contour(self, imagewithouthole, image, threshold):
        
        contours = find_contours(imagewithouthole, threshold) # Find iso-valued contours in a 2D array for a given level value.
                
        for n, contour in enumerate(contours):
            #print(contour[1,0])
            col = contour[:, 1]
            row = contour[:, 0]
            col1 = [int(round(i)) for i in col]
            row1 = [int(round(i)) for i in row]
                    
            for m in range(len(col1)):
                image[row1[m], col1[m]] = 5
                #filledimg[contour[:, 0], contour[:, 1]] = 2
            #ax.plot(contour[:, 1]+minc, contour[:, 0]+minr, linewidth=3, color='yellow')
        binarycontour = np.where(image == 5, 1, 0)
        return binarycontour
    
    def inwarddilationmask(self, binarycontour, imagewithouthole, dilationparameter):
        
        dilationimg = dilation(binarycontour, square(dilationparameter))
        
        contour_mask = dilationimg*imagewithouthole
        
        return contour_mask