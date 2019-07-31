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
from trymageAnalysis import ImageAnalysis

class Stagescan():
    def __init__(self, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11):
        # Settings for stage scan
        self.ludlStage = LudlStage("COM7")
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
                Data_dict_0[Pic_name] = data1#data1[:,:Value_yPixels]*-1
                Localimg = Image.fromarray(Data_dict_0[Pic_name]) #generate an image object
                Localimg.save(str(RepeatNum)+Pic_name+'out_1st.tif') #save as tif
                
                plt.figure(loopnum)
                plt.imshow(Data_dict_0[Pic_name], cmap = plt.cm.gray)
                plt.show()
                
                time.sleep(1)
               
                self.ludlStage.getPos()
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
                Data_dict_1[Pic_name] = data1#[:,:Value_yPixels]*-1
                Localimg = Image.fromarray(Data_dict_1[Pic_name]) #generate an image object
                Localimg.save(str(RepeatNum)+Pic_name+'out.tif') #save as tif
                plt.figure(loopnum)
                plt.imshow(Data_dict_1[Pic_name], cmap = plt.cm.gray)
                plt.show()
                time.sleep(1)
                # Image processing
                #kkk = Data_dict_1[Pic_name]/Data_dict_0[Pic_name]
                S = ImageAnalysis(Data_dict_0[Pic_name], Data_dict_1[Pic_name])
                v1, v2, bw, thres = S.applyMask()
                #R = S.ratio(v1, v2)
                L, cp, coutourmask, coutourimg, sing = S.get_intensity_properties(self.smallestsize, bw, v2, thres, v2, i, j, 8)
                S.showlabel(self.smallestsize, bw, v2, thres, i, j, cp)
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
               
                self.ludlStage.getPos()
                loopnum = loopnum+1
                
                
                del position_index[-1]
                print ('-----(⊙⊙！)-----^^^^END^^^------结束-----')
            position_index=[]
        
        print ('End of round 2')
        #print(All_cell_properties)
        
        time.sleep(2)
        #Sorting and trace back
        original_dtype = np.dtype(All_cell_properties.dtype.descr + [('Original_sequence', '<i4')])
        original_cp = np.zeros(All_cell_properties.shape, dtype=original_dtype)
        original_cp['Row index'] = All_cell_properties['Row index']
        original_cp['Column index'] = All_cell_properties['Column index']
        original_cp['Mean intensity'] = All_cell_properties['Mean intensity']
        original_cp['Circularity'] = All_cell_properties['Circularity']
        original_cp['Mean intensity in contour'] = All_cell_properties['Mean intensity in contour']
        original_cp['Original_sequence'] = list(range(0, len(All_cell_properties)))
        
        #print (original_cp['Mean intensity in contour'])
        #print('*********************sorted************************')
        #sort
        sortedcp = np.flip(np.sort(original_cp, order='Mean intensity in contour'), 0)
        #selected_num = 10 #determine how many we want
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
            v1, v2, bw, thres = S.applyMask()
            S.showlabel_with_rank(100, bw, v2, cp_index_dict[Pic_name_trace][0], cp_index_dict[Pic_name_trace][1], withranking_cp, 'Mean intensity in contour', self.selected_num)
            print ( ' i: '+ str(merged_index_samples[i,:].tolist()[0]) + ' j: '+ str(merged_index_samples[i,:].tolist()[1]))
            print ('-----------------------------------')
            input("Press Enter to continue...")
