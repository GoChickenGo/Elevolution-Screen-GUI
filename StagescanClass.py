# -*- coding: utf-8 -*-
"""
Created on Thu May  2 10:41:31 2019

@author: xinmeng
"""
import time
from Stage import Stage
import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType, TaskMode
from nidaqmx.stream_writers import AnalogMultiChannelWriter, DigitalMultiChannelWriter
from nidaqmx.stream_readers import AnalogSingleChannelReader
import wavegenerator
import matplotlib.pyplot as plt
from PIL import Image
from MageAnalysis import ImageAnalysis

class Stagescan():
    def __init__(self, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11, value12, value13):
        # Settings for stage scan
        self.ludlStage = Stage("COM7")
        self.UI_row_start_stagescan = value1
        self.UI_row_end_stagescan = value2
        self.UI_column_start_stagescan = value3
        self.UI_column_end_stagescan = value4
        self.UI_step_stagescan = value5
        self.UI_Daq_sample_rate_stagescan = value6
        self.UI_voltXMin_stagescan = value7
        self.UI_voltXMax_stagescan = value8
        self.UI_voltYMin_stagescan = value9
        self.UI_voltYMax_stagescan = value10
        self.UI_Value_xPixels_stagescan = value11
        self.UI_Value_yPixels_stagescan = value12
        self.UI_Value_averagenum_stagescan = value13
        
    def start(self):
        # settings for scanning index
        position_index=[]
        row_start = self.UI_row_start_stagescan #position index start number
        row_end = self.UI_row_end_stagescan #end number
        
        column_start = self.UI_column_start_stagescan
        column_end = self.UI_column_end_stagescan
        
        step = self.UI_step_stagescan #length of each step, 1500 for -5~5V FOV
        
        #Settings for A/D output
        Daq_sample_rate = self.UI_Daq_sample_rate_stagescan
        
        #Scanning settings
        Value_voltXMin = self.UI_voltXMin_stagescan
        Value_voltXMax = self.UI_voltXMax_stagescan
        Value_voltYMin = self.UI_voltYMin_stagescan
        Value_voltYMax = self.UI_voltYMax_stagescan
        Value_xPixels = self.UI_Value_xPixels_stagescan
        Value_yPixels = self.UI_Value_yPixels_stagescan
        averagenum =self.UI_Value_averagenum_stagescan
        #Generate galvo samples
        samples_1, samples_2= wavegenerator.waveRecPic(sampleRate = Daq_sample_rate, imAngle = 0, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, 
                         voltYMin = Value_voltYMin, voltYMax = Value_voltYMax, xPixels = Value_xPixels, yPixels = Value_yPixels, 
                         sawtooth = True)
        #ScanArrayX = wavegenerator.xValuesSingleSawtooth(sampleRate = Daq_sample_rate, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, xPixels = Value_xPixels, sawtooth = True)
        Totalscansamples = len(samples_1)*averagenum # Calculate number of samples to feed to scanner, by default it's one frame 
        ScanArrayXnum = int (len(samples_1)/Value_yPixels)
        Galvo_samples = np.vstack((samples_1,samples_2)) #
        
            
            
        #generate dig samples
        One_Dig_samples = np.append(np.ones(25000,dtype=bool), np.zeros(25000,dtype=bool))
        Dig_repeat_times = int(Totalscansamples/len(One_Dig_samples))
        Dig_samples = []
        for i in range(Dig_repeat_times):
            Dig_samples = np.append(Dig_samples, One_Dig_samples)
            
        Dataholder = np.zeros(Totalscansamples)
        
        
        
        with nidaqmx.Task() as slave_Task3, nidaqmx.Task() as master_Task, nidaqmx.Task() as slave_Task2:
            #slave_Task3 = nidaqmx.Task()
            slave_Task3.ao_channels.add_ao_voltage_chan("/Dev1/ao0:1")
            master_Task.ai_channels.add_ai_voltage_chan("/Dev1/ai0")
            slave_Task2.do_channels.add_do_chan("/Dev1/port0/line25")
            
            #slave_Task3.ao_channels.add_ao_voltage_chan("/Dev1/ao1")
            # MultiAnalogchannels
            slave_Task3.timing.cfg_samp_clk_timing(Daq_sample_rate, source='ai/SampleClock', sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamples)
            slave_Task3.triggers.sync_type.SLAVE = True
            
            # Analoginput
            master_Task.timing.cfg_samp_clk_timing(Daq_sample_rate, sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamples)
            master_Task.triggers.sync_type.MASTER = True
            
            # Digital output
            slave_Task2.timing.cfg_samp_clk_timing(Daq_sample_rate, source='ai/SampleClock', sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamples)
            slave_Task2.triggers.sync_type.SLAVE = True
            
            AnalogWriter = nidaqmx.stream_writers.AnalogMultiChannelWriter(slave_Task3.out_stream, auto_start= False)
            AnalogWriter.auto_start = False
            DigitalWriter = nidaqmx.stream_writers.DigitalSingleChannelWriter(slave_Task2.out_stream, auto_start= False)
            DigitalWriter.auto_start = False
            reader = AnalogSingleChannelReader(master_Task.in_stream)
                
            time.sleep(2)
            
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
                    self.ludlStage.MoveAbs(i,j)
                    time.sleep(1)
                    
                    AnalogWriter .write_many_sample(Galvo_samples, timeout=16.0)
                    DigitalWriter.write_one_sample_one_line(Dig_samples, timeout=16.0)
                    
                    slave_Task3.start()
                    slave_Task2.start()
                    reader.read_many_sample(Dataholder, number_of_samples_per_channel =  Totalscansamples, timeout=16.0)
                    Dataholder_average = np.mean(Dataholder.reshape(averagenum, -1), axis=0)
                    data1 = np.reshape(Dataholder_average, (Value_yPixels, ScanArrayXnum))
                    
                    slave_Task3.wait_until_done()
                    slave_Task2.wait_until_done()
                    master_Task.wait_until_done()
                    
                    Pic_name =str(i)+str(j)
                    print('Picture index name:'+str(RepeatNum)+'|'+str(i)+'|'+str(j))
                    Data_dict_0[Pic_name] = data1[:,:Value_yPixels]*-1
                    Localimg = Image.fromarray(Data_dict_0[Pic_name]) #generate an image object
                    #Localimg.save(str(RepeatNum)+Pic_name+'out.tif') #save as tif
                    
                    plt.figure(loopnum)
                    plt.imshow(Data_dict_0[Pic_name], cmap = plt.cm.gray)
                    plt.show()
                    
                    
                    slave_Task3.stop()
                    master_Task.stop()
                    slave_Task2.stop()
                    
                    time.sleep(1)
                   
                    self.ludlStage.GetPos()
                    loopnum = loopnum+1
                    
                    
                    del position_index[-1]
                    print ('---------------^^^^---------------')
                position_index=[]
            print ('Finish round 1')
            
            time.sleep(1) 
            
            self.ludlStage.MoveAbs(row_start,column_start) #move to the start as preparation
            time.sleep(2)
            
            Data_dict_1 = {}
            
            RepeatNum = 1
            loopnum = 0        
            for i in range(row_start, row_end, step):
                position_index.append(i)
                for j in range(column_start, column_end, step):
                    position_index.append(j)
                    print ('-----------------------------------')
                    print (position_index)
                    
                    #stage movement
                    self.ludlStage.MoveAbs(i,j)
                    time.sleep(1)
                    
                    AnalogWriter .write_many_sample(Galvo_samples, timeout=16.0)
                    DigitalWriter.write_one_sample_one_line(Dig_samples, timeout=16.0)
                    
                    slave_Task3.start()
                    slave_Task2.start()
                    reader.read_many_sample(Dataholder, number_of_samples_per_channel =  Totalscansamples, timeout=16.0)
                    Dataholder_average = np.mean(Dataholder.reshape(averagenum, -1), axis=0)
                    data1 = np.reshape(Dataholder_average, (Value_yPixels, ScanArrayXnum))
                    
                    slave_Task3.wait_until_done()
                    slave_Task2.wait_until_done()
                    master_Task.wait_until_done()
                    
                    Pic_name = str(i)+str(j)
                    print('Picture index name:'+str(RepeatNum)+'|'+str(i)+'|'+str(j))
                    Data_dict_1[Pic_name] = data1[:,:Value_yPixels]*-1
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
                    R = S.ratio(v1, v2)
                    L, cp= S.get_intensity_properties(50, bw, R, thres, v2, i, j,4)
                    S.showlabel(50, bw, v2, thres, i, j, cp)
                    #print (L)
                    print (cp)
                    time.sleep(2)
                    
                    slave_Task3.stop()
                    master_Task.stop()
                    slave_Task2.stop()
                    
                    time.sleep(1)
                   
                    self.ludlStage.GetPos()
                    loopnum = loopnum+1
                    
                    
                    del position_index[-1]
                    print ('---------------^^^^---------------')
                position_index=[]
            print ('Finish round 2')