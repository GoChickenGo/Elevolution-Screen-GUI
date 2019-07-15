# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 10:38:29 2019

@author: xinmeng
"""
# The adaptive NI DAQ tool

import time
import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType, TaskMode, LineGrouping, Signal
from nidaqmx.stream_writers import AnalogMultiChannelWriter, DigitalMultiChannelWriter
from nidaqmx.stream_readers import AnalogSingleChannelReader, AnalogMultiChannelReader

import matplotlib.pyplot as plt
from PIL import Image

from configuration import Configuration

class execute():
    def __init__(self, samplingrate, analogsignals, digitalsignals, readinchannels):
        
        configs = Configuration()
        configdictionary = {'galvosx':configs.galvoXChannel,
                            'galvosy':'Dev1/ao1',#configs.galvoYChannel, 
                            '640AO':'Dev1/ao3',
                            '488AO':'Dev2/ao1',
                            '532AO':'Dev2/ao0',
                            'patchAO':configs.patchVoltInChannel,
                            'cameratrigger':"Dev1/port0/line25",
                            'galvotrigger':"Dev1/port0/line25",
                            'blankingall':"Dev1/port0/line4",
                            '640blanking':"Dev1/port0/line4",
                            '532blanking':"Dev1/port0/line6",
                            '488blanking':"Dev1/port0/line3",
                            'PMT':"Dev1/ai0",
                            'Vp':"Dev1/ai22",
                            'Ip':"Dev1/ai20"
                            }
        
        Daq_sample_rate = samplingrate
        Totalscansamplesnumber = len(analogsignals['Waveform'][0])
        num_rows, num_cols = analogsignals['Waveform'].shape
        print("row number of analog signals:  "+str(num_rows))
        
        self.averagenumber = 0
        self.ypixelnumber = 0
        for i in range(len(analogsignals['Sepcification'])):
            if 'galvosx' in analogsignals['Sepcification'][i]:
                self.averagenumber = int(analogsignals['Sepcification'][i][analogsignals['Sepcification'][i].index('_')+1:len(analogsignals['Sepcification'][i])])
                analogsignals['Sepcification'][i] = 'galvosx'
            elif 'galvosy' in analogsignals['Sepcification'][i]:
                self.ypixelnumber = int(analogsignals['Sepcification'][i][analogsignals['Sepcification'][i].index('_')+1:len(analogsignals['Sepcification'][i])])
                analogsignals['Sepcification'][i] = 'galvosy'
        
        # Devide samples from Dev1 or 2
        analogwritesamplesdev1_Sepcification = []
        analogwritesamplesdev2_Sepcification = []
        
        analogwritesamplesdev1 = []
        analogwritesamplesdev2 = []
        
        for i in range(int(num_rows)):
            if 'Dev1' in configdictionary[analogsignals['Sepcification'][i]]:
                analogwritesamplesdev1_Sepcification.append(configdictionary[analogsignals['Sepcification'][i]])
                analogwritesamplesdev1.append(analogsignals['Waveform'][i])
            else:
                analogwritesamplesdev2_Sepcification.append(configdictionary[analogsignals['Sepcification'][i]])
                analogwritesamplesdev2.append(analogsignals['Waveform'][i])
                
        analogsignal_dev1_number = len(analogwritesamplesdev1_Sepcification)
        analogsignal_dev2_number = len(analogwritesamplesdev2_Sepcification)
        
        analogsignalslinenumber = len(analogsignals['Waveform'])
        digitalsignalslinenumber = len(digitalsignals['Waveform'])
        
        # Stack the Analog samples of dev1 and dev2 individually
        if analogsignal_dev1_number == 1:            
            writesamples_dev1 = np.array([analogwritesamplesdev1[0]])

        elif analogsignal_dev1_number == 0:
            writesamples_dev1 = []
        else:
            writesamples_dev1 = analogwritesamplesdev1[0]    
            for i in range(1, analogsignal_dev1_number):
                writesamples_dev1 = np.vstack((writesamples_dev1, analogwritesamplesdev1[i]))
                
        if analogsignal_dev2_number == 1:
            writesamples_dev2 = np.array([analogwritesamplesdev2[0]])
        elif analogsignal_dev2_number == 0:
            writesamples_dev2 = []    
        else:
            writesamples_dev2 = analogwritesamplesdev2[0]
            for i in range(1, analogsignal_dev2_number):
                writesamples_dev2 = np.vstack((writesamples_dev2, analogwritesamplesdev2[i]))
        
        # Stack the digital samples        
        if digitalsignalslinenumber == 1:
            holder2 = np.array([digitalsignals['Waveform'][0]])

        elif digitalsignalslinenumber == 0:
            holder2 = []
        else:
            holder2 = digitalsignals['Waveform'][0]
            for i in range(1, digitalsignalslinenumber):
                holder2 = np.vstack((holder2, digitalsignals['Waveform'][i]))
        
        #holder = np.vstack((analogsignals['Waveform'][0], analogsignals['Waveform'][1]))
        holder2 = np.array(holder2, dtype = 'uint32')
        
        #print(writesamples_dev2.shape)
        print(holder2.shape)
        print(holder2.dtype)
        #print(analogsignals['Waveform'].flags)
        


        
        # Assume that dev1 is always employed
        with nidaqmx.Task() as slave_Task_1_dev1, nidaqmx.Task() as slave_Task_1_dev2, nidaqmx.Task() as master_Task, nidaqmx.Task() as slave_Task_2:
            # adding channels      
            '''
            for i in range(len(analogsignals['Sepcification'])):
                slave_Task_1.ao_channels.add_ao_voltage_chan(configdictionary[analogsignals['Sepcification'][i]])
            '''
            # Set tasks from different devices apart
            for i in range(analogsignal_dev1_number):
                slave_Task_1_dev1.ao_channels.add_ao_voltage_chan(analogwritesamplesdev1_Sepcification[i])

            if len(digitalsignals['Sepcification']) != 0:
                for i in range(len(digitalsignals['Sepcification'])):
                    slave_Task_2.do_channels.add_do_chan(configdictionary[digitalsignals['Sepcification'][i]], line_grouping=LineGrouping.CHAN_PER_LINE)#line_grouping??????????????One Channel For Each Line

            Dataholder = np.zeros((len(readinchannels), Totalscansamplesnumber))
            
            if 'PMT' in readinchannels:
                master_Task.ai_channels.add_ai_voltage_chan(configdictionary['PMT'])
            if 'Vp' in readinchannels:
                master_Task.ai_channels.add_ai_voltage_chan(configdictionary['Vp'])
            if 'Ip' in readinchannels:
                master_Task.ai_channels.add_ai_current_chan(configdictionary['Ip'])
            
            # setting clock
            # Analog clock  USE clock on Dev1 as center clock
            slave_Task_1_dev1.timing.cfg_samp_clk_timing(Daq_sample_rate, source='ai/SampleClock', sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamplesnumber)
            #slave_Task_1_dev1.triggers.sync_type.SLAVE = True            
            # Readin clock as master clock
            master_Task.timing.cfg_samp_clk_timing(Daq_sample_rate, sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamplesnumber)
            #master_Task.triggers.sync_type.MASTER = True 
            #master_Task.export_signals(Signal.SAMPLE_CLOCK, '/Dev1/PFI1')
            #master_Task.export_signals(Signal.START_TRIGGER, '')
            master_Task.export_signals.samp_clk_output_term = configs.clock1Channel#'/Dev1/PFI1'#
            master_Task.export_signals.start_trig_output_term = configs.trigger1Channel#'/Dev1/PFI2'
            #slave_Task_1_dev1.samp_clk_output_term
            #slave_Task_1_dev1.samp_trig_output_term
            
            if analogsignal_dev2_number != 0:
                # Be default assume that read master task is in dev1
                
                for i in range(analogsignal_dev2_number):
                    slave_Task_1_dev2.ao_channels.add_ao_voltage_chan(analogwritesamplesdev2_Sepcification[i])
                
                dev2Clock = configs.clock2Channel#/Dev2/PFI1
                slave_Task_1_dev2.timing.cfg_samp_clk_timing(Daq_sample_rate, source=dev2Clock, sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamplesnumber)
                #slave_Task_1_dev2.triggers.sync_type.SLAVE = True
                
                slave_Task_1_dev2.triggers.start_trigger.cfg_dig_edge_start_trig(configs.trigger2Channel)#'/Dev2/PFI7'
                
                AnalogWriter = nidaqmx.stream_writers.AnalogMultiChannelWriter(slave_Task_1_dev1.out_stream, auto_start= False)
                AnalogWriter.auto_start = False
                
                AnalogWriter_dev2 = nidaqmx.stream_writers.AnalogMultiChannelWriter(slave_Task_1_dev2.out_stream, auto_start= False)
                AnalogWriter_dev2.auto_start = False
            
            # Digital clock
            if len(digitalsignals['Sepcification']) != 0: # or the source of sample clock could be PFI? or using start trigger: cfg_dig_edge_start_trig    slave_task.triggers.start_trigger.cfg_dig_edge_start_trig("/PXI1Slot3/ai/StartTrigger")
                slave_Task_2.timing.cfg_samp_clk_timing(Daq_sample_rate, source='ai/SampleClock', sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamplesnumber)
                #slave_Task_2.triggers.sync_type.SLAVE = True
            


            AnalogWriter = nidaqmx.stream_writers.AnalogMultiChannelWriter(slave_Task_1_dev1.out_stream, auto_start= False)
            AnalogWriter.auto_start = False
            if len(digitalsignals['Sepcification']) != 0:
                DigitalWriter = nidaqmx.stream_writers.DigitalMultiChannelWriter(slave_Task_2.out_stream, auto_start= False)
                DigitalWriter.auto_start = False
            reader = AnalogMultiChannelReader(master_Task.in_stream)        
            
            # ----------------------------------Run in conditions of presence of at least one digital line.!!!!!!!!!!!!!!!!!!!!!!!!!!
            AnalogWriter.write_many_sample(writesamples_dev1, timeout = 16.0)
            if analogsignal_dev2_number != 0:
                AnalogWriter_dev2.write_many_sample(writesamples_dev2, timeout = 16.0)
            DigitalWriter.write_many_sample_port_uint32(holder2, timeout = 16.0)
            reader.read_many_sample(Dataholder, number_of_samples_per_channel =  Totalscansamplesnumber, timeout=16.0)
            
            if analogsignal_dev2_number != 0:
                slave_Task_1_dev2.start()            
            slave_Task_1_dev1.start()
            slave_Task_2.start()
            master_Task.start()

            
            if 'PMT' in readinchannels:
                Dataholder_average = np.mean(Dataholder[0,:].reshape(self.averagenumber, -1), axis=0)
                
                ScanArrayXnum = int ((Totalscansamplesnumber/self.averagenumber)/self.ypixelnumber)
                data1 = np.reshape(Dataholder_average, (self.ypixelnumber, ScanArrayXnum))
                
                data1= data1*-1
                plt.figure()
                plt.imshow(data1, cmap = plt.cm.gray)
                plt.show()
            
            slave_Task_1_dev1.wait_until_done()
            if analogsignal_dev2_number != 0:
                slave_Task_1_dev2.wait_until_done()
            master_Task.wait_until_done()
            
            slave_Task_1_dev1.stop()
            if analogsignal_dev2_number != 0:
                slave_Task_1_dev2.stop()
            master_Task.stop()
