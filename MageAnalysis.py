# -*- coding: utf-8 -*-
"""
Created on Wed May  1 20:20:32 2019

@author: Meng
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math
from skimage import data
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, find_contours
from skimage.morphology import closing, square
from skimage.measure import regionprops
from skimage.color import label2rgb

class ImageAnalysis():
    def __init__(self, value1, value2):
        self.img_before_tem = value1
        self.img_after_tem = value2
        self.Img_before = self.img_before_tem.copy()
        self.Img_after = self.img_after_tem.copy()
    def applyMask(self):
        thresh = threshold_otsu(self.Img_before)
        #mask = img_before > thresh # generate mask
        binarymask = closing(self.Img_before >= thresh, square(3))
        self.mask = closing(self.Img_before >= thresh, square(3))
        
        #fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #ax.imshow(bw)# fig 2
        
        Segimg_bef = self.mask*self.Img_before.copy()
        Segimg_aft = self.mask*self.Img_after.copy()
              
        #fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #ax.imshow(Segimg_bef) #fig 3
        
        return Segimg_bef, Segimg_aft, binarymask, thresh
    
        
    def ratio(self, value1, value2):
        self.Segimg_bef_ratio = np.where(value1 == 0, 1, value1)
        Ratio = value2/self.Segimg_bef_ratio
        
        #fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #ax.imshow(Ratio) #fig 3 
        return Ratio
    
    def getproperties(self, smallest_size, theMask, original_intensity, threshold, i, j):
        # remove artifacts connected to image border
        self.Labelmask = theMask
        self.OriginImag = original_intensity
        self.row_num = i
        self.column_num = j
        self.threshold = threshold
        
        cleared = self.Labelmask.copy()
        clear_border(cleared)
                # label image regions
        label_image = label(cleared)
        #image_label_overlay = label2rgb(label_image, image=image)
        
        #fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #ax.imshow(label_image)
        #contours = find_contours(original_intensity, self.threshold)
        dtype = [('Row index', 'i4'), ('Column index', 'i4'), ('Ratio', float)]
        
        region_mean_intensity_list = []
        loopmun = 0
        dirforcellprp={}
        for region in regionprops(label_image,intensity_image=self.OriginImag):
        
            
            # skip small images
            if region.area > smallest_size:
                               
                # draw rectangle around segmented coins
                #minr, minc, maxr, maxc = region.bbox
                #rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
                #ax.add_patch(rect)
                #centroidint1 = int(region.centroid[0])
                #centroidint2 = int(region.centroid[1])
                #ax.text(centroidint1+50, centroidint2+55, round(region.mean_intensity,3),fontsize=15, style='italic',bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
                region_mean_intensity = region.mean_intensity
                
                #print(region_mean_intensity)
                region_mean_intensity_list.append(region_mean_intensity)
                dirforcellprp[loopmun] = (self.row_num, self.column_num, region_mean_intensity)
                
                loopmun = loopmun+1
        
        cell_properties = np.zeros(len(region_mean_intensity_list), dtype = dtype)
        for p in range(loopmun):
            cell_properties[p] = dirforcellprp[p]
                
        return region_mean_intensity_list, cell_properties
        #fig = plt.figure()
        #fig.show()
        #ax.savefig('foo.tif', dpi=300)
    def showlabel(self, smallest_size, theMask, original_intensity, threshold, i, j):
        # remove artifacts connected to image border
        self.Labelmask = theMask
        self.OriginImag = original_intensity
        self.row_num = i
        self.column_num = j
        self.threshold = threshold
        
        cleared = self.Labelmask.copy()
        clear_border(cleared)
                # label image regions
        label_image = label(cleared)
        #image_label_overlay = label2rgb(label_image, image=image)
        #contours = find_contours(original_intensity, self.threshold)
        
        fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        ax.imshow(label_image)
        
        loopmun = 0
        for region in regionprops(label_image,intensity_image=self.OriginImag):
            # skip small images
            if region.area > smallest_size:
                               
                # draw rectangle around segmented coins
                minr, minc, maxr, maxc = region.bbox
                rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
                ax.add_patch(rect)
                centroidint1 = int(region.centroid[0])
                centroidint2 = int(region.centroid[1])
                circularity = (4 * math.pi * region.filled_area) / (region.perimeter * region.perimeter)
                ax.text(centroidint1, centroidint2, str(region.mean_intensity)+','+str(circularity),fontsize=9, color='yellow', style='italic',bbox={'facecolor':'red', 'alpha':0.3, 'pad':8})
                
                
                #ax.plot(contours[:, 1], contours[:, 0], linewidth=2)
                
                loopmun = loopmun+1
        
        ax.set_axis_off()
        #plt.tight_layout()
        plt.show()
