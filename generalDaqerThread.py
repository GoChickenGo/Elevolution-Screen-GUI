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
from PyQt5.QtCore import pyqtSignal, QThread
import matplotlib.pyplot as plt
from PIL import Image

from configuration import Configuration

class execute_analog_readin_optional_digital_thread(QThread):
    collected_data = pyqtSignal(np.ndarray)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configs = Configuration()
        self.configdictionary = {'galvosx':self.configs.galvoXChannel,
                            'galvosy':'Dev1/ao1',#self.configs.galvoYChannel, 
                            '640AO':'Dev1/ao3',
                            '488AO':'Dev2/ao1',
                            '532AO':'Dev2/ao0',
                            'patchAO':self.configs.patchVoltInChannel,
                            'cameratrigger':"Dev1/port0/line25",
                            'galvotrigger':"Dev1/port0/line25",
                            'blankingall':"Dev1/port0/line4",
                            '640blanking':"Dev1/port0/line4",
                            '532blanking':"Dev1/port0/line6",
                            '488blanking':"Dev1/port0/line3",
                            'PMT':"Dev1/ai0",
                            'Vp':"Dev1/ai22",
                            'Ip':"Dev1/ai20",
                            'Perfusion_1':"Dev1/port0/line20"
                            }    
    def set_waves(self, samplingrate, analogsignals, digitalsignals, readinchannels):
        
        self.analogsignals = analogsignals
        self.digitalsignals = digitalsignals
        self.readinchannels=readinchannels
        self.Daq_sample_rate = samplingrate
        
        # some preparations for analog lines
        self.Totalscansamplesnumber = len(self.analogsignals['Waveform'][0])
        num_rows, num_cols = self.analogsignals['Waveform'].shape
        print("row number of analog signals:  "+str(num_rows))
        
        # Get the average number and y pixel number information from data
        self.averagenumber = 0
        self.ypixelnumber = 0
        for i in range(len(self.analogsignals['Sepcification'])):
            if 'galvosx' in self.analogsignals['Sepcification'][i]:
                self.averagenumber = int(self.analogsignals['Sepcification'][i][self.analogsignals['Sepcification'][i].index('_')+1:len(self.analogsignals['Sepcification'][i])])
                self.galvosx_originalkey = self.analogsignals['Sepcification'][i]
                self.analogsignals['Sepcification'][i] = 'galvosx'
            elif 'galvosy' in self.analogsignals['Sepcification'][i]:
                self.ypixelnumber = int(self.analogsignals['Sepcification'][i][self.analogsignals['Sepcification'][i].index('_')+1:len(self.analogsignals['Sepcification'][i])])
                self.galvosy_originalkey = self.analogsignals['Sepcification'][i]
                self.analogsignals['Sepcification'][i] = 'galvosy'
        
        # Devide samples from Dev1 or 2
        self.analogwritesamplesdev1_Sepcification = []
        self.analogwritesamplesdev2_Sepcification = []
        
        self.analogwritesamplesdev1 = []
        self.analogwritesamplesdev2 = []
        
        for i in range(int(num_rows)):
            if 'Dev1' in self.configdictionary[self.analogsignals['Sepcification'][i]]:
                self.analogwritesamplesdev1_Sepcification.append(self.configdictionary[self.analogsignals['Sepcification'][i]])
                self.analogwritesamplesdev1.append(self.analogsignals['Waveform'][i])
            else:
                self.analogwritesamplesdev2_Sepcification.append(self.configdictionary[self.analogsignals['Sepcification'][i]])
                self.analogwritesamplesdev2.append(self.analogsignals['Waveform'][i])
                
        self.analogsignal_dev1_number = len(self.analogwritesamplesdev1_Sepcification)
        self.analogsignal_dev2_number = len(self.analogwritesamplesdev2_Sepcification)
        
        self.analogsignalslinenumber = len(self.analogsignals['Waveform'])
        self.digitalsignalslinenumber = len(self.digitalsignals['Waveform'])
        
        # Stack the Analog samples of dev1 and dev2 individually
        # IN CASE OF ONLY ONE ARRAY, WE NEED TO CONVERT THE SHAPE TO (1,N) BY USING np.array([]) OUTSIDE THE ARRAY!!
        #------------------------------------------!!_________________________
        if self.analogsignal_dev1_number == 1:            
            self.writesamples_dev1 = np.array([self.analogwritesamplesdev1[0]])

        elif self.analogsignal_dev1_number == 0:
            self.writesamples_dev1 = []
        else:
            self.writesamples_dev1 = self.analogwritesamplesdev1[0]    
            for i in range(1, self.analogsignal_dev1_number):
                self.writesamples_dev1 = np.vstack((self.writesamples_dev1, self.analogwritesamplesdev1[i]))
                
        if self.analogsignal_dev2_number == 1:
            self.writesamples_dev2 = np.array([self.analogwritesamplesdev2[0]])
        elif self.analogsignal_dev2_number == 0:
            self.writesamples_dev2 = []    
        else:
            self.writesamples_dev2 = self.analogwritesamplesdev2[0]
            for i in range(1, self.analogsignal_dev2_number):
                self.writesamples_dev2 = np.vstack((self.writesamples_dev2, self.analogwritesamplesdev2[i]))
        
        # Stack the digital samples        
        if self.digitalsignalslinenumber == 1:
            self.holder2 = np.array([self.digitalsignals['Waveform'][0]])

        elif self.digitalsignalslinenumber == 0:
            self.holder2 = []
        else:
            self.holder2 = self.digitalsignals['Waveform'][0]
            for i in range(1, self.digitalsignalslinenumber):
                self.holder2 = np.vstack((self.holder2, self.digitalsignals['Waveform'][i]))
        

        # Set the dtype of digital signals
        # The same as (0b1 << n)
        self.holder2 = np.array(self.holder2, dtype = 'uint32')        
        for i in range(self.digitalsignalslinenumber):
            convernum = int(self.configdictionary[self.digitalsignals['Sepcification'][i]][self.configdictionary[self.digitalsignals['Sepcification'][i]].index('line')+4:len(self.configdictionary[self.digitalsignals['Sepcification'][i]])])
            self.holder2[i] = self.holder2[i]*(2**(convernum))
            
        # For example, to send commands to line 0 and line 3, you hava to write 1001 to digital port, convert to uint32 that is 9.
        if self.digitalsignalslinenumber > 1:
           self.holder2 = np.sum(self.holder2, axis = 0) # sum along the columns, for multiple lines
           self.holder2 = np.array([self.holder2]) # here convert the shape from (n,) to (1,n)
    
    def start(self):
        # Assume that dev1 is always employed
        with nidaqmx.Task() as slave_Task_1_analog_dev1, nidaqmx.Task() as slave_Task_1_analog_dev2, nidaqmx.Task() as master_Task_readin, nidaqmx.Task() as slave_Task_2_digitallines:
            # adding channels      
            # Set tasks from different devices apart
            for i in range(self.analogsignal_dev1_number):
                slave_Task_1_analog_dev1.ao_channels.add_ao_voltage_chan(self.analogwritesamplesdev1_Sepcification[i])

            #if len(digitalsignals['Sepcification']) != 0:
                #for i in range(len(digitalsignals['Sepcification'])):
                    #slave_Task_2_digitallines.do_channels.add_do_chan(self.configdictionary[digitalsignals['Sepcification'][i]], line_grouping=LineGrouping.CHAN_PER_LINE)#line_grouping??????????????One Channel For Each Line
            slave_Task_2_digitallines.do_channels.add_do_chan("/Dev1/port0", line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
            
            self.Dataholder = np.zeros((len(self.readinchannels), self.Totalscansamplesnumber))
            
            if 'PMT' in self.readinchannels:
                master_Task_readin.ai_channels.add_ai_voltage_chan(self.configdictionary['PMT'])
            if 'Vp' in self.readinchannels:
                master_Task_readin.ai_channels.add_ai_voltage_chan(self.configdictionary['Vp'])
            if 'Ip' in self.readinchannels:
                master_Task_readin.ai_channels.add_ai_current_chan(self.configdictionary['Ip'])
            
            # setting clock
            # Analog clock  USE clock on Dev1 as center clock
            slave_Task_1_analog_dev1.timing.cfg_samp_clk_timing(self.Daq_sample_rate, source='ai/SampleClock', sample_mode= AcquisitionType.FINITE, samps_per_chan=self.Totalscansamplesnumber)
            #slave_Task_1_analog_dev1.triggers.sync_type.SLAVE = True            
            # Readin clock as master clock
            master_Task_readin.timing.cfg_samp_clk_timing(self.Daq_sample_rate, sample_mode= AcquisitionType.FINITE, samps_per_chan=self.Totalscansamplesnumber)
            #master_Task_readin.triggers.sync_type.MASTER = True 
            #master_Task_readin.export_signals(Signal.SAMPLE_CLOCK, '/Dev1/PFI1')
            #master_Task_readin.export_signals(Signal.START_TRIGGER, '')
            master_Task_readin.export_signals.samp_clk_output_term = self.configs.clock1Channel#'/Dev1/PFI1'#
            master_Task_readin.export_signals.start_trig_output_term = self.configs.trigger1Channel#'/Dev1/PFI2'
            #slave_Task_1_analog_dev1.samp_clk_output_term
            #slave_Task_1_analog_dev1.samp_trig_output_term
            
            if self.analogsignal_dev2_number != 0:
                # By default assume that read master task is in dev1
                
                for i in range(self.analogsignal_dev2_number):
                    slave_Task_1_analog_dev2.ao_channels.add_ao_voltage_chan(self.analogwritesamplesdev2_Sepcification[i])
                
                dev2Clock = self.configs.clock2Channel#/Dev2/PFI1
                slave_Task_1_analog_dev2.timing.cfg_samp_clk_timing(self.Daq_sample_rate, source=dev2Clock, sample_mode= AcquisitionType.FINITE, samps_per_chan=self.Totalscansamplesnumber)
                #slave_Task_1_analog_dev2.triggers.sync_type.SLAVE = True
                
                #slave_Task_1_analog_dev2.triggers.start_trigger.cfg_dig_edge_start_trig(self.configs.trigger2Channel)#'/Dev2/PFI7'
                
                AnalogWriter = nidaqmx.stream_writers.AnalogMultiChannelWriter(slave_Task_1_analog_dev1.out_stream, auto_start= False)
                AnalogWriter.auto_start = False
                
                AnalogWriter_dev2 = nidaqmx.stream_writers.AnalogMultiChannelWriter(slave_Task_1_analog_dev2.out_stream, auto_start= False)
                AnalogWriter_dev2.auto_start = False
            
            # Digital clock
            if len(self.digitalsignals['Sepcification']) != 0: # or the source of sample clock could be PFI? or using start trigger: cfg_dig_edge_start_trig    slave_task.triggers.start_trigger.cfg_dig_edge_start_trig("/PXI1Slot3/ai/StartTrigger")
                slave_Task_2_digitallines.timing.cfg_samp_clk_timing(self.Daq_sample_rate, source='ai/SampleClock', sample_mode= AcquisitionType.FINITE, samps_per_chan=self.Totalscansamplesnumber)
                #slave_Task_2_digitallines.triggers.sync_type.SLAVE = True
            

        	# Configure the writer and reader
            AnalogWriter = nidaqmx.stream_writers.AnalogMultiChannelWriter(slave_Task_1_analog_dev1.out_stream, auto_start= False)
            AnalogWriter.auto_start = False
            if len(self.digitalsignals['Sepcification']) != 0:
                DigitalWriter = nidaqmx.stream_writers.DigitalMultiChannelWriter(slave_Task_2_digitallines.out_stream, auto_start= False)
                DigitalWriter.auto_start = False
            reader = AnalogMultiChannelReader(master_Task_readin.in_stream)        
            
            # ---------------------------------------------------------------------------------------------------------------------
            #-----------------------------------------------------Begin to execute in DAQ------------------------------------------
            AnalogWriter.write_many_sample(self.writesamples_dev1, timeout = 16.0)
            
            if self.analogsignal_dev2_number != 0:
                AnalogWriter_dev2.write_many_sample(self.writesamples_dev2, timeout = 16.0)
                
            if self.digitalsignalslinenumber != 0:     
                DigitalWriter.write_many_sample_port_uint32(self.holder2, timeout = 16.0)
                
            reader.read_many_sample(self.Dataholder, number_of_samples_per_channel =  self.Totalscansamplesnumber, timeout=16.0)
            
            print('^^^^^^^^^^^^^^^^^^Daq tasks start^^^^^^^^^^^^^^^^^^')
            if self.analogsignal_dev2_number != 0:
                slave_Task_1_analog_dev2.start()            
            slave_Task_1_analog_dev1.start()
            
            if self.digitalsignalslinenumber != 0:
                slave_Task_2_digitallines.start()
                
            master_Task_readin.start()
            
            self.data_PMT = []
            
            slave_Task_1_analog_dev1.wait_until_done()
            if self.analogsignal_dev2_number != 0:
                slave_Task_1_analog_dev2.wait_until_done()
            if self.digitalsignalslinenumber != 0:
                slave_Task_2_digitallines.wait_until_done()                
            master_Task_readin.wait_until_done()
            
            if 'PMT' in self.readinchannels:
                Dataholder_average = np.mean(self.Dataholder[0,:].reshape(self.averagenumber, -1), axis=0)
                
                self.ScanArrayXnum = int ((self.Totalscansamplesnumber/self.averagenumber)/self.ypixelnumber)
                self.data_PMT = np.reshape(Dataholder_average, (self.ypixelnumber, self.ScanArrayXnum))
                
                self.data_PMT= self.data_PMT*-1
                plt.figure()
                plt.imshow(self.data_PMT, cmap = plt.cm.gray)
                plt.show()
                
            slave_Task_1_analog_dev1.stop()
            if self.analogsignal_dev2_number != 0:
                slave_Task_1_analog_dev2.stop()
            if self.digitalsignalslinenumber != 0:
                slave_Task_2_digitallines.stop()
            master_Task_readin.stop()
            
            self.collected_data.emit(self.Dataholder)
            print('^^^^^^^^^^^^^^^^^^Daq tasks finish^^^^^^^^^^^^^^^^^^')
        # set the keys of galvos back for next round
        for i in range(len(self.analogsignals['Sepcification'])):
            if 'galvosx' in self.analogsignals['Sepcification'][i]:
                self.analogsignals['Sepcification'][i] = self.galvosx_originalkey
            elif 'galvosy' in self.analogsignals['Sepcification'][i]:
                self.analogsignals['Sepcification'][i] = self.galvosy_originalkey
               
    def read(self):
        return self.data_PMT
    
    def aboutToQuitHandler(self):
        self.requestInterruption()
        self.wait()            