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
from skimage.filters import threshold_otsu, threshold_local
from skimage.segmentation import clear_border
from skimage.measure import label, perimeter, find_contours
from skimage.morphology import closing, square, opening
from skimage.measure import regionprops
from skimage.color import label2rgb
from skimage.restoration import denoise_tv_chambolle
import numpy.lib.recfunctions as rfn

class ImageAnalysis():
    def __init__(self, value1, value2):
        self.img_before_tem = value1
        self.img_after_tem = value2
        self.Img_before = self.img_before_tem.copy()
        self.Img_after = self.img_after_tem.copy()
    def applyMask(self):
        
        self.Img_before = denoise_tv_chambolle(self.Img_before, weight=0.01)
        self.Img_after = denoise_tv_chambolle(self.Img_after, weight=0.01)
        
        thresh = threshold_otsu(self.Img_before)#-0.7#-55
        # -----------------------------------------------Adaptive thresholding-----------------------------------------------
        block_size = 335
        binary_adaptive = threshold_local(self.Img_before, block_size, offset=0)
        
        #mask = img_before > thresh # generate mask
        #binarymask = opening(self.Img_before > thresh, square(1))
        binary_adaptive1 = self.Img_before >= binary_adaptive
        binarymask = opening(binary_adaptive1, square(2))
        self.mask = closing(binarymask, square(3))
        
        #fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #ax.imshow(bw)# fig 2
        
        Segimg_bef = self.mask*self.Img_before.copy()
        Segimg_aft = self.mask*self.Img_after.copy()
              
        #fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #ax.imshow(Segimg_aft) #fig 3
        
        return Segimg_bef, Segimg_aft, self.mask, thresh
    
        
    def ratio(self, value1, value2):
        self.Segimg_bef_ratio = np.where(value1 == 0, 1, value1)
        Ratio = value2/self.Segimg_bef_ratio
        
        #fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #ax.imshow(Ratio) #fig 3 
        return Ratio
    
    def get_intensity_properties(self, smallest_size, theMask, threshold, intensity_bef, intensty_aft, i, j, dilationdegree1):
        # remove artifacts connected to image border
        self.Labelmask = theMask
        self.Imagbef = intensity_bef
        self.row_num = i
        self.column_num = j
        self.threshold = threshold
        self.Imageaft = intensty_aft
        self.dilationdegree = dilationdegree1
        
        cleared = self.Labelmask.copy()
        clear_border(cleared)
                # label image regions
        label_image = label(cleared)
        #image_label_overlay = label2rgb(label_image, image=image)
        
        #fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #ax.imshow(label_image)
        #contours = find_contours(original_intensity, self.threshold)
        dtype = [('Row index', 'i4'), ('Column index', 'i4'), ('Mean intensity', float), ('Circularity', float), ('Mean intensity in contour', float), ('Change', float)]
        
        region_mean_intensity_list = []
        region_circularit_list = []
        region_meanintensity_contour_list = []
        
        loopmun = 0
        dirforcellprp={}
        for region in regionprops(label_image,intensity_image=self.Imagbef): # USE image before perfusion as template
            
            # skip small images
            if region.area > smallest_size:
                               
                # draw rectangle around segmented coins
                minr, minc, maxr, maxc = region.bbox

                region_mean_intensity = region.mean_intensity #mean intensity of the region, 0 pixels are omitted.
                #allpixelnum = region.bbox_area
                #labeledpixelnum = region.area #number of pixels in region omitting 0.
                filledimg = region.filled_image
                filledperimeter = perimeter(filledimg)
                #Sliced_binary_region_image = region.image
                self.intensityimage_intensity = region.intensity_image # need a copy of this cause region will be altered by s.contour
                self.regionimage_before = self.intensityimage_intensity.copy()
                self.regionimage_after = self.Imageaft[minr:maxr, minc:maxc]
                #print(self.Imagbef[region.coords[0][0]][region.coords[0][1]])
                
                #localthresh = threshold_otsu(self.regionimage_after)-0.1
                #print(localthresh)
                #singlethresh = True
                #print(region.area)
                #print(region.bbox_area)
                #print(region_mean_intensity)
                s=imageanalysistoolbox()
                contourimage_intensity = s.contour(filledimg, self.intensityimage_intensity, 0.001) # after here self.intensityimage_intensity is changed with contour labeled with number 5
                contour_mask_of_intensity = s.inwarddilationmask(contourimage_intensity ,filledimg, self.dilationdegree)   


                #filledimg = region.filled_image #Binary region image with filled holes which has the same size as bounding box.
                #filledperimeter = perimeter(filledimg)
                regioncircularity = (4 * math.pi * region.filled_area) / (filledperimeter * filledperimeter) # region.perimeter will count in perimeters from the holes inside
                contour_origin_image_intensity = contour_mask_of_intensity*self.regionimage_before
                
                # Calculate mean contour intensity of image before perfusion
                contourprops_bef = regionprops(contour_mask_of_intensity, self.regionimage_before)
                contour_mean_bef = contourprops_bef[0].mean_intensity

                # Calculate mean contour intensity of image after perfusion
                contourprops_aft = regionprops(contour_mask_of_intensity, self.regionimage_after)
                contour_mean_aft = contourprops_aft[0].mean_intensity
                #print('contour_mean_bef:'+str(contour_mean_bef))
                
                #Calculate the intensity change
                ratio = contour_mean_aft/contour_mean_bef
                
                
                #print(region_mean_intensity)
                region_mean_intensity_list.append(region_mean_intensity)
                region_circularit_list.append(regioncircularity)
                region_meanintensity_contour_list.append(contour_mean_bef)
                
                dirforcellprp[loopmun] = (self.row_num, self.column_num, region_mean_intensity, regioncircularity, contour_mean_bef, ratio)
                
                loopmun = loopmun+1
        
        cell_properties = np.zeros(len(region_mean_intensity_list), dtype = dtype)
        for p in range(loopmun):
            cell_properties[p] = dirforcellprp[p]
            
        return region_mean_intensity_list, cell_properties, contour_mask_of_intensity, contour_origin_image_intensity,  self.regionimage_before, ratio
    
    
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
        
        
        self.fig_showlabel, self.ax_showlabel = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        #plt.figure(self.row_num+self.column_num)
        self.ax_showlabel.imshow(label_image)
        
        loopmun1 = 0
        for region in regionprops(label_image,intensity_image=self.OriginImag):
            # skip small images
            if region.area > smallest_size:
                               
                # draw rectangle around segmented coins
                minr, minc, maxr, maxc = region.bbox
                rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
                self.ax_showlabel.add_patch(rect)
                filledimg = region.filled_image #Binary region image with filled holes which has the same size as bounding box.
                #filledperimeter = perimeter(filledimg)
                #singlethresh = threshold_otsu(filledimg)
                
                #print(singlethresh)
                #print(filledperimeter)
                #print(region.perimeter)
                #print(region.filled_area)
                #print(str(minc)+', '+str(maxc)+', '+str(minr)+', '+str(maxr))
                #s=imageanalysistoolbox()
                #contourimage = s.contour(filledimg, self.intensityimage, singlethresh)
                #contour_mask = s.inwarddilationmask(contourimage ,filledimg, 15)

                contours = find_contours(filledimg, 0.8) # Find iso-valued contours in a 2D array for a given level value.
                
                for n, contour in enumerate(contours):
                    #print(contour[1,0])
                    #col = contour[:, 1]
                    #row = contour[:, 0]
                    #col1 = [int(round(i)) for i in col]
                    #row1 = [int(round(i)) for i in row]
                    
                    #for m in range(len(col1)):
                        #self.intensityimage[row1[m], col1[m]] = 5
                    #filledimg[contour[:, 0], contour[:, 1]] = 2
                    self.ax_showlabel.plot(contour[:, 1]+minc, contour[:, 0]+minr, linewidth=1, color='yellow')
                x1 = cell_properties['Change'][loopmun1]
                x2 = cell_properties['Mean intensity in contour'][loopmun1]
                
                #circularity = (4 * math.pi * region.filled_area) / (filledperimeter * filledperimeter) # region.perimeter will count in perimeters from the holes inside
                self.ax_showlabel.text((maxc + minc)/2, (maxr + minr)/2, str(round(x1, 3))+',    '+str(round(x2, 3)),fontsize=8, color='yellow', style='italic')#,bbox={'facecolor':'red', 'alpha':0.3, 'pad':8})
                
                
                #ax.plot(contours[:, 1], contours[:, 0], linewidth=2)
                
                loopmun1 = loopmun1+1
        #plt.show()       
        self.ax_showlabel.set_axis_off()
        #plt.tight_layout()
        #self.ax_showlabel.show()
        
        #return filledimg, Sliced_binary_region_image, intensityimage
    def showlabel_with_rank(self, smallest_size, theMask, original_intensity, cpstart, cpend, cell_properties, thekey_attri, num_hits):
        self.Labelmask = theMask
        self.OriginImag = original_intensity
        self.cp_start = cpstart
        self.cp_end = cpend
        #self.threshold = threshold
        self.thekey_attri= thekey_attri
        
        #cell_properties = np.flip(np.sort(cell_properties, order=self.thekey_attri), 0)
        #keyattri = cell_properties[self.thekey_attri].tolist()
        #keyattri = keyattri[:num_hits]
        #print(keyattri)
        
        #cell_properties = cell_properties[:num_hits]
        cell_properties = cell_properties[self.cp_start:self.cp_end+1] # trace back to i,j corresponding locations in cell properties list.
        cleared = self.Labelmask.copy()
        clear_border(cleared)
                # label image regions
        label_image = label(cleared)
        #image_label_overlay = label2rgb(label_image, image=image)
        
        
        fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(6, 6))
        ax.imshow(label_image)
        
        loopmun1 = 0
        for region in regionprops(label_image,intensity_image=self.OriginImag):
            # skip small images
            if region.area > smallest_size:         
                # draw rectangle around segmented coins
                minr, minc, maxr, maxc = region.bbox
                rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
                ax.add_patch(rect)
                filledimg = region.filled_image
                #singlethresh = threshold_otsu(filledimg)
                
                #print(singlethresh)
                #print(filledperimeter)
                #print(region.perimeter)
                #print(region.filled_area)
                #print(str(minc)+', '+str(maxc)+', '+str(minr)+', '+str(maxr))
                #s=imageanalysistoolbox()
                #contourimage = s.contour(filledimg, self.intensityimage, singlethresh)
                #contour_mask = s.inwarddilationmask(contourimage ,filledimg, 15)

                #contours = find_contours(filledimg, 0.8) # Find iso-valued contours in a 2D array for a given level value.
                    
                #for n, contour in enumerate(contours):
                    #print(contour[1,0])
                    #col = contour[:, 1]
                    #row = contour[:, 0]
                    #col1 = [int(round(i)) for i in col]
                    #row1 = [int(round(i)) for i in row]
                    
                    #for m in range(len(col1)):
                    #self.intensityimage[row1[m], col1[m]] = 5
                    #filledimg[contour[:, 0], contour[:, 1]] = 2
                    #ax.plot(contour[:, 1]+minc, contour[:, 0]+minr, linewidth=1, color='yellow')
                    #x1 = cell_properties['Circularity'][loopmun1]
                x2 = cell_properties['Mean intensity in contour'][loopmun1]
                x3 = cell_properties['Ranking'][loopmun1]
                if x3 < num_hits:
                    #circularity = (4 * math.pi * region.filled_area) / (filledperimeter * filledperimeter) # region.perimeter will count in perimeters from the holes inside
                    ax.text((maxc + minc)/2, (maxr + minr)/2, str(round(x2, 3))+ ',  '+str(x3), fontsize=8, color='yellow', style='italic')#,bbox={'facecolor':'red', 'alpha':0.3, 'pad':8})
                    
                    
                    #ax.plot(contours[:, 1], contours[:, 0], linewidth=2)
                loopmun1 = loopmun1+1
                
        ax.set_axis_off()
        #plt.tight_layout()
        plt.show()
        
    def sort_using_weight(self, cell_properties, property_1, property_2, weight_1, weight_2):
        
        max_p1 = np.amax(cell_properties[property_1])
        max_p2 = np.amax(cell_properties[property_2])
        
        #cell_properties = np.flip(np.sort(cell_properties, order=property_1), 0)
        cell_properties = rfn.append_fields(cell_properties, 'Nomalization according to '+property_1, cell_properties[property_1]/max_p1, usemask=False)

        #cell_properties = np.flip(np.sort(cell_properties, order=property_2), 0)
        cell_properties = rfn.append_fields(cell_properties, 'Nomalization according to '+property_2, cell_properties[property_2]/max_p2, usemask=False)
        
        weights = cell_properties['Nomalization according to '+property_1]*weight_1 + cell_properties['Nomalization according to '+property_2]*weight_2
        
        cell_properties = rfn.append_fields(cell_properties, 'evalution', weights, usemask=False)
        
        cell_properties = np.flip(np.sort(cell_properties, order='evalution'), 0)

        return cell_properties