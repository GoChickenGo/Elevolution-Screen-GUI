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
from findcontour import imageanalysistoolbox
from skimage import data
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, perimeter, find_contours
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
        binarymask = closing(self.Img_before > thresh, square(4))
        self.mask = closing(self.Img_before > thresh, square(4))
        
        #fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #ax.imshow(bw)# fig 2
        
        Segimg_bef = self.mask*self.Img_before.copy()
        Segimg_aft = self.mask*self.Img_after.copy()
              
        fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        ax.imshow(Segimg_aft) #fig 3
        
        return Segimg_bef, Segimg_aft, binarymask, thresh
    
        
    def ratio(self, value1, value2):
        self.Segimg_bef_ratio = np.where(value1 == 0, 1, value1)
        Ratio = value2/self.Segimg_bef_ratio
        
        #fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #ax.imshow(Ratio) #fig 3 
        return Ratio
    
    def get_ratio_properties(self, smallest_size, theMask, ratio_intensity, threshold, Img_after, i, j):
        # remove artifacts connected to image border
        self.Labelmask = theMask
        self.ratioImag = ratio_intensity
        self.row_num = i
        self.column_num = j
        self.threshold = threshold
        self.originimg = Img_after
        
        cleared = self.Labelmask.copy()
        clear_border(cleared)
                # label image regions
        label_image = label(cleared)
        #image_label_overlay = label2rgb(label_image, image=image)
        
        #fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #ax.imshow(label_image)
        #contours = find_contours(original_intensity, self.threshold)
        dtype = [('Row index', 'i4'), ('Column index', 'i4'), ('Mean intensity', float), ('Circularity', float), ('Mean intensity in contour', float)]
        
        region_mean_intensity_list = []
        region_circularit_list = []
        region_meanintensity_contour_list = []
        
        loopmun = 0
        dirforcellprp={}
        for region in regionprops(label_image,intensity_image=self.ratioImag):
        
            
            # skip small images
            if region.area > smallest_size:
                               
                # draw rectangle around segmented coins
                #minr, minc, maxr, maxc = region.bbox
                #rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
                #ax.add_patch(rect)
                #centroidint1 = int(region.centroid[0])
                #centroidint2 = int(region.centroid[1])
                #ax.text(centroidint1+50, centroidint2+55, round(region.mean_intensity,3),fontsize=15, style='italic',bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
                region_mean_intensity = region.mean_intensity #mean intensity of the region, 0 pixels are omitted.
                #allpixelnum = region.bbox_area
                #labeledpixelnum = region.area #number of pixels in region omitting 0.
                filledimg = region.filled_image
                filledperimeter = perimeter(filledimg)
                #Sliced_binary_region_image = region.image
                intensityimage = region.intensity_image
                singlethresh = threshold_otsu(filledimg)
                #print(region.area)
                #print(region.bbox_area)
                #print(region_mean_intensity)
                s=imageanalysistoolbox()
                contourimage = s.contour(filledimg, intensityimage, singlethresh)
                contour_mask = s.inwarddilationmask(contourimage ,filledimg, 3)                

                filledimg = region.filled_image #Binary region image with filled holes which has the same size as bounding box.
                filledperimeter = perimeter(filledimg)
                regioncircularity = (4 * math.pi * region.filled_area) / (filledperimeter * filledperimeter) # region.perimeter will count in perimeters from the holes inside
                contour_origin_image = contour_mask*intensityimage
                contourprops = regionprops(contour_mask, intensityimage)
                contour_mean = contourprops[0].mean_intensity
                #print('contour_mean:'+str(contour_mean))
                
                #print(region_mean_intensity)
                region_mean_intensity_list.append(region_mean_intensity)
                region_circularit_list.append(regioncircularity)
                region_meanintensity_contour_list.append(contour_mean)
                
                dirforcellprp[loopmun] = (self.row_num, self.column_num, region_mean_intensity, regioncircularity, contour_mean)
                
                loopmun = loopmun+1
        
        cell_properties = np.zeros(len(region_mean_intensity_list), dtype = dtype)
        for p in range(loopmun):
            cell_properties[p] = dirforcellprp[p]
                
        return region_mean_intensity_list, cell_properties, contour_origin_image
        #fig = plt.figure()
        #fig.show()
        #ax.savefig('foo.tif', dpi=300)
    def get_intensity_properties(self, smallest_size, theMask, ratio_intensity, threshold, intensty_img, i, j):
        # remove artifacts connected to image border
        self.Labelmask = theMask
        self.ratioImag = ratio_intensity
        self.row_num = i
        self.column_num = j
        self.threshold = threshold
        self.originimg = intensty_img
        
        cleared = self.Labelmask.copy()
        clear_border(cleared)
                # label image regions
        label_image = label(cleared)
        #image_label_overlay = label2rgb(label_image, image=image)
        
        #fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #ax.imshow(label_image)
        #contours = find_contours(original_intensity, self.threshold)
        dtype = [('Row index', 'i4'), ('Column index', 'i4'), ('Mean intensity', float), ('Circularity', float), ('Mean intensity in contour', float)]
        
        region_mean_intensity_list = []
        region_circularit_list = []
        region_meanintensity_contour_list = []
        
        loopmun = 0
        dirforcellprp={}
        for region in regionprops(label_image,intensity_image=self.originimg):
        
            
            # skip small images
            if region.area > smallest_size:
                               
                # draw rectangle around segmented coins
                #minr, minc, maxr, maxc = region.bbox
                #rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
                #ax.add_patch(rect)
                #centroidint1 = int(region.centroid[0])
                #centroidint2 = int(region.centroid[1])
                #ax.text(centroidint1+50, centroidint2+55, round(region.mean_intensity,3),fontsize=15, style='italic',bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
                region_mean_intensity = region.mean_intensity #mean intensity of the region, 0 pixels are omitted.
                #allpixelnum = region.bbox_area
                #labeledpixelnum = region.area #number of pixels in region omitting 0.
                filledimg = region.filled_image
                filledperimeter = perimeter(filledimg)
                #Sliced_binary_region_image = region.image
                intensityimage = region.intensity_image
                singlethresh = threshold_otsu(filledimg)
                #print(region.area)
                #print(region.bbox_area)
                #print(region_mean_intensity)
                s=imageanalysistoolbox()
                contourimage = s.contour(filledimg, intensityimage, singlethresh)
                contour_mask = s.inwarddilationmask(contourimage ,filledimg, 15)                

                filledimg = region.filled_image #Binary region image with filled holes which has the same size as bounding box.
                filledperimeter = perimeter(filledimg)
                regioncircularity = (4 * math.pi * region.filled_area) / (filledperimeter * filledperimeter) # region.perimeter will count in perimeters from the holes inside
                contour_origin_image = contour_mask*intensityimage
                contourprops = regionprops(contour_mask, intensityimage)
                contour_mean = contourprops[0].mean_intensity
                #print('contour_mean:'+str(contour_mean))
                
                #print(region_mean_intensity)
                region_mean_intensity_list.append(region_mean_intensity)
                region_circularit_list.append(regioncircularity)
                region_meanintensity_contour_list.append(contour_mean)
                
                dirforcellprp[loopmun] = (self.row_num, self.column_num, region_mean_intensity, regioncircularity, contour_mean)
                
                loopmun = loopmun+1
        
        cell_properties = np.zeros(len(region_mean_intensity_list), dtype = dtype)
        for p in range(loopmun):
            cell_properties[p] = dirforcellprp[p]
                
        return region_mean_intensity_list, cell_properties, contour_origin_image
    
    
    def showlabel(self, smallest_size, theMask, original_intensity, threshold, i, j, cell_properties):
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
                filledimg = region.filled_image #Binary region image with filled holes which has the same size as bounding box.
                #filledperimeter = perimeter(filledimg)
                Sliced_binary_region_image = region.image
                intensityimage = region.intensity_image
                singlethresh = threshold_otsu(filledimg)
                
                #print(singlethresh)
                #print(filledperimeter)
                #print(region.perimeter)
                #print(region.filled_area)
                #print(str(minc)+', '+str(maxc)+', '+str(minr)+', '+str(maxr))
                #s=imageanalysistoolbox()
                #contourimage = s.contour(filledimg, intensityimage, singlethresh)
                #contour_mask = s.inwarddilationmask(contourimage ,filledimg, 15)

                contours = find_contours(filledimg, singlethresh) # Find iso-valued contours in a 2D array for a given level value.
                
                for n, contour in enumerate(contours):
                    #print(contour[1,0])
                    #col = contour[:, 1]
                    #row = contour[:, 0]
                    #col1 = [int(round(i)) for i in col]
                    #row1 = [int(round(i)) for i in row]
                    
                    #for m in range(len(col1)):
                        #intensityimage[row1[m], col1[m]] = 5
                    #filledimg[contour[:, 0], contour[:, 1]] = 2
                    ax.plot(contour[:, 1]+minc, contour[:, 0]+minr, linewidth=3, color='yellow')
                x1 = cell_properties['Circularity'][loopmun]
                x2 = cell_properties['Mean intensity in contour'][loopmun]
                
                #circularity = (4 * math.pi * region.filled_area) / (filledperimeter * filledperimeter) # region.perimeter will count in perimeters from the holes inside
                ax.text((maxc + minc)/2, (maxr + minr)/2, str(round(x1, 3))+',    '+str(round(x2, 3)),fontsize=12, color='yellow', style='italic',bbox={'facecolor':'red', 'alpha':0.3, 'pad':8})
                
                
                #ax.plot(contours[:, 1], contours[:, 0], linewidth=2)
                
                loopmun = loopmun+1
                
        ax.set_axis_off()
        #plt.tight_layout()
        plt.show()
        
        return filledimg, Sliced_binary_region_image, intensityimage