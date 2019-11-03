# -*- coding: utf-8 -*-
"""
Created on Thu May  2 10:41:31 2019

@author: xinmeng
"""
import time
from stage import LudlStage
import numpy as np
from nidaqmx.constants import AcquisitionType, TaskMode
from nidaqmx.stream_writers import AnalogMultiChannelWriter, DigitalMultiChannelWriter
from nidaqmx.stream_readers import AnalogSingleChannelReader
from generalDaqer import execute_analog_readin_optional_digital, execute_digital
import matplotlib.pyplot as plt
from PIL import Image
from trymageAnalysis_v3 import ImageAnalysis
import numpy.lib.recfunctions as rfn
import os

class Stagescan():
    def __init__(self, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11, value12, value13, value14, findcontour_thres, contour_dilationpara, cell_region_opening, cell_region_closing, saving_dir):
        # Settings for stage scan
        self.ludlStage = LudlStage("COM6")
        self.UI_row_start_stagescan = value1
        self.UI_row_end_stagescan = value2
        self.UI_column_start_stagescan = value3
        self.UI_column_end_stagescan = value4
        self.UI_step_stagescan = value5
        self.samplingrate = value6
        self.analogsignals = value7
        self.digitalsignals = value8
        self.readinchannels = value9
        self.selected_num = value10
        self.smallestsize = value11
        self.opening_factor = value12
        self.closing_factor = value13
        self.binary_adaptive_block_size = value14
        self.findcontour_thres = findcontour_thres
        self.contour_dilationpara = contour_dilationpara
        self.cell_region_opening = cell_region_opening
        self.cell_region_closing = cell_region_closing
        self.saving_dir = saving_dir
        
    def start(self):
        # settings for scanning index
        position_index=[]
        row_start = self.UI_row_start_stagescan #position index start number
        row_end = self.UI_row_end_stagescan #end number
        
        column_start = self.UI_column_start_stagescan
        column_end = self.UI_column_end_stagescan
        
        step = self.UI_step_stagescan #length of each step, 1500 for -5~5V FOV
        
        #Settings for A/D output
        Daq_sample_rate = self.samplingrate
            
        RepeatNum = 0
        Data_dict_0 = {}
        loopnum = 0        
        for i in range(row_start, row_end, step):
            position_index.append(i)
            for j in range(column_start, column_end, step):
                position_index.append(j)
                print ('-----------------------------------')
                print (position_index)
                
                #stage movement
                self.ludlStage.moveAbs(i,j)
                time.sleep(1)
                
                self.analog_to_feed = self.analogsignals.copy()
                
                doit = execute_analog_readin_optional_digital(Daq_sample_rate, self.analog_to_feed, self.digitalsignals, self.readinchannels)
                data1 = doit.read()
                
                Pic_name =str(i)+str(j)
                print('Picture index name:'+str(RepeatNum)+'|'+str(i)+'|'+str(j))
                # Assume that we are using 5v
                Data_dict_0[Pic_name] = data1[:, 15:515]#data1[:,:Value_yPixels]*-1
                Localimg = Image.fromarray(Data_dict_0[Pic_name]) #generate an image object
                Localimg.save(os.path.join(self.saving_dir, str(RepeatNum)+Pic_name+'out_1st.tif')) #save as tif
                
                plt.figure(loopnum)
                plt.imshow(Data_dict_0[Pic_name], cmap = plt.cm.gray)
                plt.show()
                
                time.sleep(0.3)
               
                #self.ludlStage.getPos()
                loopnum = loopnum+1
                                
                del position_index[-1]
                print ('---------------^^^^---------------')
            position_index=[]
        print ('Finish round 1')
        
        time.sleep(1) 
        
        self.ludlStage.moveAbs(row_start,column_start) #move to the start as preparation
        time.sleep(2)
        input("Press Enter to continue...")
        
        Data_dict_1 = {} #dictionary for images
        All_cell_properties_dict = {}
        All_cell_properties = []
        cp_end_index = -1
        cp_index_dict = {} #dictionary for each cell properties
        
        RepeatNum = 1
        loopnum = 0        
        for i in range(row_start, row_end, step):
            position_index.append(i)
            for j in range(column_start, column_end, step):
                position_index.append(j)
                print ('----(´・ω・`)---------vvv-Start-vvv-------(´・ω・`)--------')
                print (position_index)
                
                #stage movement
                self.ludlStage.moveAbs(i,j)
                time.sleep(1)
                
                self.analog_to_feed = self.analogsignals.copy()
                
                doit = execute_analog_readin_optional_digital(Daq_sample_rate, self.analog_to_feed, self.digitalsignals, self.readinchannels)
                data1 = doit.read()
                
                Pic_name = str(i)+str(j)
                print('Picture index name:'+str(RepeatNum)+'|'+str(i)+'|'+str(j))
                Data_dict_1[Pic_name] = data1[:, 15:515]#[:,:Value_yPixels]*-1
                Localimg = Image.fromarray(Data_dict_1[Pic_name]) #generate an image object
                Localimg.save(os.path.join(self.saving_dir, str(RepeatNum)+Pic_name+'out.tif')) #save as tif
                plt.figure(loopnum)
                plt.imshow(Data_dict_1[Pic_name], cmap = plt.cm.gray)
                plt.show()
                time.sleep(0.3)
                # Image processing
                #kkk = Data_dict_1[Pic_name]/Data_dict_0[Pic_name]
                S = ImageAnalysis(Data_dict_0[Pic_name], Data_dict_1[Pic_name])
                v1, v2, mask_1, mask_2, thres = S.applyMask(self.opening_factor, self.closing_factor, self.binary_adaptive_block_size) #v1 = Thresholded whole image
                #R = S.ratio(v1, v2)
                cp, coutourmask, coutourimg, intensityimage_intensity, contour_change_ratio= S.get_intensity_properties(self.smallestsize, mask_1, thres, v1, v2, i, j, self.findcontour_thres, self.contour_dilationpara, self.cell_region_opening, self.cell_region_closing)
                S.showlabel(self.smallestsize, mask_1, v1, thres, i, j, cp)
                #print (L)
                print (cp)
                All_cell_properties_dict[loopnum] = cp
                if loopnum == 0:
                    All_cell_properties = All_cell_properties_dict[0]
                if loopnum != 0:
                    All_cell_properties = np.append(All_cell_properties, All_cell_properties_dict[loopnum], axis=0)
                
                cp_end_index = cp_end_index + len(cp)
                cp_start_index = cp_end_index - len(cp) +1
                cp_index_dict[Pic_name] = [cp_start_index, cp_end_index] #get the location of individual cp index & put in dictionary， as they are stored in sequence.
                               
                time.sleep(1)
               
                #self.ludlStage.getPos()
                loopnum = loopnum+1
                
                
                del position_index[-1]
                print ('-----(⊙⊙！)-----^^^^END^^^------结束-----')
            position_index=[]
        
        print ('End of round 2')
        #print(All_cell_properties)
        
        time.sleep(2)
        #Sorting and trace back
        #------------------------------------------CAN use 'import numpy.lib.recfunctions as rfn' to append field--------------
        original_cp = rfn.append_fields(All_cell_properties, 'Original_sequence', list(range(0, len(All_cell_properties))), usemask=False)
        #print (original_cp['Mean intensity in contour'])
        #print('*********************sorted************************')
        #sort
        sortedcp = S.sort_using_weight(original_cp, 'Change', 'Mean intensity in contour', 0.5, 0.5)
        #sortedcp = np.flip(np.sort(original_cp, order='Mean intensity in contour'), 0)
        #selected_num = 10 #determine how many we want
        #unsorted_cp = All_cell_properties[:selected_num]
        #targetcp = sortedcp[:selected_num]
        ranked_cp = rfn.append_fields(sortedcp, 'Ranking', list(range(0, len(All_cell_properties))), usemask=False)
        withranking_cp = np.sort(ranked_cp, order='Original_sequence')
        
        #print (ranked_cp)
        #print('***********************Original sequence with ranking**************************')
        
        # All the cells are ranked, now we find the desired group and their position indexs, call the images and show labels of
        # these who meet the requirements, omitting bad ones.
        
        #get the index
        cell_properties_selected_hits = ranked_cp[0:self.selected_num]
        cell_properties_selected_hits_index_sorted = np.sort(cell_properties_selected_hits, order=['Row index', 'Column index'])
        index_samples = np.vstack((cell_properties_selected_hits_index_sorted['Row index'],cell_properties_selected_hits_index_sorted['Column index']))
        
        merged_index_samples = index_samples[:,0]

        #consider these after 1st one
        for i in range(1, len(index_samples[0])):
            #print(index_samples[:,i][0] - index_samples[:,i-1][0])    
            if index_samples[:,i][0] != index_samples[:,i-1][0] or index_samples[:,i][1] != index_samples[:,i-1][1]: 
                merged_index_samples = np.append(merged_index_samples, index_samples[:,i], axis=0)
        merged_index_samples = merged_index_samples.reshape(-1, 2) # 1st column=i, 2nd column=j
        
        # then we move back to each of this positions and show the labels
        input("Press Enter to continue...")
        print(merged_index_samples)
        print(withranking_cp)

        for i in range(len(merged_index_samples)):
            print ('-----------------------------------')
                
            #stage movement
            self.ludlStage.moveAbs(merged_index_samples[i,:].tolist()[0],merged_index_samples[i,:].tolist()[1])
            time.sleep(1)
                
            Pic_name_trace = str(merged_index_samples[i,:].tolist()[0])+str(merged_index_samples[i,:].tolist()[1])
                
            S = ImageAnalysis(Data_dict_0[Pic_name_trace], Data_dict_1[Pic_name_trace]) #The same as ImageAnalysis(Data_dict_0[Pic_name], Data_dict_1[Pic_name]), call the same image with same dictionary index.
            v1, v2, mask_1, mask_2, thres = S.applyMask(self.opening_factor, self.closing_factor, self.binary_adaptive_block_size)
            S.showlabel_with_rank(self.smallestsize, mask_1, v1, cp_index_dict[Pic_name_trace][0], cp_index_dict[Pic_name_trace][1], withranking_cp, 'Mean intensity in contour', self.selected_num)
            print ( ' i: '+ str(merged_index_samples[i,:].tolist()[0]) + ' j: '+ str(merged_index_samples[i,:].tolist()[1]))
            print ('-----------------------------------')
            input("Press Enter to continue...")
