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

class execute_analog_readin_optional_digital():
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
                            'Ip':"Dev1/ai20",
                            'Perfusion_1':"Dev1/port0/line20"
                            }
        
        Daq_sample_rate = samplingrate
        
        # some preparations for analog lines
        Totalscansamplesnumber = len(analogsignals['Waveform'][0])
        num_rows, num_cols = analogsignals['Waveform'].shape
        print("row number of analog signals:  "+str(num_rows))
        
        # Get the average number and y pixel number information from data
        self.averagenumber = 0
        self.ypixelnumber = 0
        for i in range(len(analogsignals['Sepcification'])):
            if 'galvosx' in analogsignals['Sepcification'][i]:
                self.averagenumber = int(analogsignals['Sepcification'][i][analogsignals['Sepcification'][i].index('_')+1:len(analogsignals['Sepcification'][i])])
                self.galvosx_originalkey = analogsignals['Sepcification'][i]
                analogsignals['Sepcification'][i] = 'galvosx'
            elif 'galvosy' in analogsignals['Sepcification'][i]:
                self.ypixelnumber = int(analogsignals['Sepcification'][i][analogsignals['Sepcification'][i].index('_')+1:len(analogsignals['Sepcification'][i])])
                self.galvosy_originalkey = analogsignals['Sepcification'][i]
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
        # IN CASE OF ONLY ONE ARRAY, WE NEED TO CONVERT THE SHAPE TO (1,N) BY USING np.array([]) OUTSIDE THE ARRAY!!
        #------------------------------------------!!_________________________
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
        

        # Set the dtype of digital signals
        # The same as (0b1 << n)
        holder2 = np.array(holder2, dtype = 'uint32')        
        for i in range(digitalsignalslinenumber):
            convernum = int(configdictionary[digitalsignals['Sepcification'][i]][configdictionary[digitalsignals['Sepcification'][i]].index('line')+4:len(configdictionary[digitalsignals['Sepcification'][i]])])
            print(convernum)
            holder2[i] = holder2[i]*(2**(convernum))
            
        # For example, to send commands to line 0 and line 3, you hava to write 1001 to digital port, convert to uint32 that is 9.
        if digitalsignalslinenumber > 1:
           holder2 = np.sum(holder2, axis = 0) # sum along the columns, for multiple lines
           holder2 = np.array([holder2]) # here convert the shape from (n,) to (1,n)

        # Assume that dev1 is always employed
        with nidaqmx.Task() as slave_Task_1_analog_dev1, nidaqmx.Task() as slave_Task_1_analog_dev2, nidaqmx.Task() as master_Task_readin, nidaqmx.Task() as slave_Task_2_digitallines:
            # adding channels      
            # Set tasks from different devices apart
            for i in range(analogsignal_dev1_number):
                slave_Task_1_analog_dev1.ao_channels.add_ao_voltage_chan(analogwritesamplesdev1_Sepcification[i])

            #if len(digitalsignals['Sepcification']) != 0:
                #for i in range(len(digitalsignals['Sepcification'])):
                    #slave_Task_2_digitallines.do_channels.add_do_chan(configdictionary[digitalsignals['Sepcification'][i]], line_grouping=LineGrouping.CHAN_PER_LINE)#line_grouping??????????????One Channel For Each Line
            slave_Task_2_digitallines.do_channels.add_do_chan("/Dev1/port0", line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
            
            Dataholder = np.zeros((len(readinchannels), Totalscansamplesnumber))
            
            if 'PMT' in readinchannels:
                master_Task_readin.ai_channels.add_ai_voltage_chan(configdictionary['PMT'])
            if 'Vp' in readinchannels:
                master_Task_readin.ai_channels.add_ai_voltage_chan(configdictionary['Vp'])
            if 'Ip' in readinchannels:
                master_Task_readin.ai_channels.add_ai_current_chan(configdictionary['Ip'])
            
            # setting clock
            # Analog clock  USE clock on Dev1 as center clock
            slave_Task_1_analog_dev1.timing.cfg_samp_clk_timing(Daq_sample_rate, source='ai/SampleClock', sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamplesnumber)
            #slave_Task_1_analog_dev1.triggers.sync_type.SLAVE = True            
            # Readin clock as master clock
            master_Task_readin.timing.cfg_samp_clk_timing(Daq_sample_rate, sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamplesnumber)
            #master_Task_readin.triggers.sync_type.MASTER = True 
            #master_Task_readin.export_signals(Signal.SAMPLE_CLOCK, '/Dev1/PFI1')
            #master_Task_readin.export_signals(Signal.START_TRIGGER, '')
            master_Task_readin.export_signals.samp_clk_output_term = configs.clock1Channel#'/Dev1/PFI1'#
            master_Task_readin.export_signals.start_trig_output_term = configs.trigger1Channel#'/Dev1/PFI2'
            #slave_Task_1_analog_dev1.samp_clk_output_term
            #slave_Task_1_analog_dev1.samp_trig_output_term
            
            if analogsignal_dev2_number != 0:
                # By default assume that read master task is in dev1
                
                for i in range(analogsignal_dev2_number):
                    slave_Task_1_analog_dev2.ao_channels.add_ao_voltage_chan(analogwritesamplesdev2_Sepcification[i])
                
                dev2Clock = configs.clock2Channel#/Dev2/PFI1
                slave_Task_1_analog_dev2.timing.cfg_samp_clk_timing(Daq_sample_rate, source=dev2Clock, sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamplesnumber)
                #slave_Task_1_analog_dev2.triggers.sync_type.SLAVE = True
                
                #slave_Task_1_analog_dev2.triggers.start_trigger.cfg_dig_edge_start_trig(configs.trigger2Channel)#'/Dev2/PFI7'
                
                AnalogWriter = nidaqmx.stream_writers.AnalogMultiChannelWriter(slave_Task_1_analog_dev1.out_stream, auto_start= False)
                AnalogWriter.auto_start = False
                
                AnalogWriter_dev2 = nidaqmx.stream_writers.AnalogMultiChannelWriter(slave_Task_1_analog_dev2.out_stream, auto_start= False)
                AnalogWriter_dev2.auto_start = False
            
            # Digital clock
            if len(digitalsignals['Sepcification']) != 0: # or the source of sample clock could be PFI? or using start trigger: cfg_dig_edge_start_trig    slave_task.triggers.start_trigger.cfg_dig_edge_start_trig("/PXI1Slot3/ai/StartTrigger")
                slave_Task_2_digitallines.timing.cfg_samp_clk_timing(Daq_sample_rate, source='ai/SampleClock', sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamplesnumber)
                #slave_Task_2_digitallines.triggers.sync_type.SLAVE = True
            

        	# Configure the writer and reader
            AnalogWriter = nidaqmx.stream_writers.AnalogMultiChannelWriter(slave_Task_1_analog_dev1.out_stream, auto_start= False)
            AnalogWriter.auto_start = False
            if len(digitalsignals['Sepcification']) != 0:
                DigitalWriter = nidaqmx.stream_writers.DigitalMultiChannelWriter(slave_Task_2_digitallines.out_stream, auto_start= False)
                DigitalWriter.auto_start = False
            reader = AnalogMultiChannelReader(master_Task_readin.in_stream)        
            
            # ---------------------------------------------------------------------------------------------------------------------
            #-----------------------------------------------------Begin to execute in DAQ------------------------------------------
            AnalogWriter.write_many_sample(writesamples_dev1, timeout = 16.0)
            
            if analogsignal_dev2_number != 0:
                AnalogWriter_dev2.write_many_sample(writesamples_dev2, timeout = 16.0)
                
            if digitalsignalslinenumber != 0:     
                DigitalWriter.write_many_sample_port_uint32(holder2, timeout = 16.0)
                
            reader.read_many_sample(Dataholder, number_of_samples_per_channel =  Totalscansamplesnumber, timeout=16.0)
            
            if analogsignal_dev2_number != 0:
                slave_Task_1_analog_dev2.start()            
            slave_Task_1_analog_dev1.start()
            
            if digitalsignalslinenumber != 0:
                slave_Task_2_digitallines.start()
                
            master_Task_readin.start()
            
            self.data_PMT = []
            
            slave_Task_1_analog_dev1.wait_until_done()
            if analogsignal_dev2_number != 0:
                slave_Task_1_analog_dev2.wait_until_done()
            if digitalsignalslinenumber != 0:
                slave_Task_2_digitallines.wait_until_done()                
            master_Task_readin.wait_until_done()
            
            if 'PMT' in readinchannels:
                Dataholder_average = np.mean(Dataholder[0,:].reshape(self.averagenumber, -1), axis=0)
                
                ScanArrayXnum = int ((Totalscansamplesnumber/self.averagenumber)/self.ypixelnumber)
                self.data_PMT = np.reshape(Dataholder_average, (self.ypixelnumber, ScanArrayXnum))
                
                self.data_PMT= self.data_PMT*-1
                plt.figure()
                plt.imshow(self.data_PMT, cmap = plt.cm.gray)
                plt.show()
                
            slave_Task_1_analog_dev1.stop()
            if analogsignal_dev2_number != 0:
                slave_Task_1_analog_dev2.stop()
            if digitalsignalslinenumber != 0:
                slave_Task_2_digitallines.stop()
            master_Task_readin.stop()
            
            slave_Task_1_analog_dev1.close()
            if analogsignal_dev2_number != 0:
                slave_Task_1_analog_dev2.close()
            if digitalsignalslinenumber != 0:
                slave_Task_2_digitallines.close()
            master_Task_readin.close()
        # set the keys of galvos back for next round
        for i in range(len(analogsignals['Sepcification'])):
            if 'galvosx' in analogsignals['Sepcification'][i]:
                analogsignals['Sepcification'][i] = self.galvosx_originalkey
            elif 'galvosy' in analogsignals['Sepcification'][i]:
                analogsignals['Sepcification'][i] = self.galvosy_originalkey
               
    def read(self):
        return self.data_PMT
            
class execute_digital():
    def __init__(self, samplingrate, digitalsignals):
        
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
                            'Ip':"Dev1/ai20",
                            'Perfusion_1':"Dev1/port0/line20"
                            }
        
        Daq_sample_rate = samplingrate
        
        # some preparations for digital lines
        Totalscansamplesnumber = len(digitalsignals['Waveform'][0])
        
        digitalsignalslinenumber = len(digitalsignals['Waveform'])
                
        # Stack the digital samples        
        if digitalsignalslinenumber == 1:
            holder2 = np.array([digitalsignals['Waveform'][0]])

        elif digitalsignalslinenumber == 0:
            holder2 = []
        else:
            holder2 = digitalsignals['Waveform'][0]
            for i in range(1, digitalsignalslinenumber):
                holder2 = np.vstack((holder2, digitalsignals['Waveform'][i]))
        
        # Set the dtype of digital signals
        #
        holder2 = np.array(holder2, dtype = 'uint32')        
        for i in range(digitalsignalslinenumber):
            convernum = int(configdictionary[digitalsignals['Sepcification'][i]][configdictionary[digitalsignals['Sepcification'][i]].index('line')+4:len(configdictionary[digitalsignals['Sepcification'][i]])])
            print(convernum)
            holder2[i] = holder2[i]*(2**(convernum))
        # For example, to send commands to line 0 and line 3, you hava to write 1001 to digital port, convert to uint32 that is 9.
        if digitalsignalslinenumber > 1:
           holder2 = np.sum(holder2, axis = 0) # sum along the columns, for multiple lines        
           holder2 = np.array([holder2]) # here convert the shape from (n,) to (1,n)
        #print(holder2.shape)
        #holder2 = holder2*16 

        #print(type(holder2[0][1]))
        #print(holder2[0][1])

        # Assume that dev1 is always employed
        with nidaqmx.Task() as slave_Task_2_digitallines:
            # adding channels      
            # Set tasks from different devices apart
            #for i in range(len(digitalsignals['Sepcification'])):
                #slave_Task_2_digitallines.do_channels.add_do_chan(configdictionary[digitalsignals['Sepcification'][i]], line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)#line_grouping??????????????One Channel For Each Line
            slave_Task_2_digitallines.do_channels.add_do_chan("/Dev1/port0", line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
            # Digital clock
            slave_Task_2_digitallines.timing.cfg_samp_clk_timing(Daq_sample_rate, sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamplesnumber)

        	# Configure the writer and reader
            DigitalWriter = nidaqmx.stream_writers.DigitalMultiChannelWriter(slave_Task_2_digitallines.out_stream, auto_start= False)
            DigitalWriter.auto_start = False
                  
            # ---------------------------------------------------------------------------------------------------------------------
            #-----------------------------------------------------Begin to execute in DAQ------------------------------------------
                
            DigitalWriter.write_many_sample_port_uint32(holder2, timeout = 26.0)
            
            slave_Task_2_digitallines.start()

            slave_Task_2_digitallines.wait_until_done()                

            slave_Task_2_digitallines.stop()
            
class execute_constant_vpatch():
    def __init__(self, constant):
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
                            'Ip':"Dev1/ai20",
                            'Perfusion_1':"Dev1/port0/line20"
                            }        
        self.task = nidaqmx.Task()
        self.task.ao_channels.add_ao_voltage_chan(configdictionary['patchAO'])
        
        self.task.write(constant)
        
    def close(self):
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
                            'Ip':"Dev1/ai20",
                            'Perfusion_1':"Dev1/port0/line20"
                            }
        with nidaqmx.Task() as self.task:
            self.task.ao_channels.add_ao_voltage_chan(configdictionary['patchAO'])
            
            self.task.write(0)
        
class execute_contineous_analog():
    def __init__(self, samplingrate, analogsignals):
        
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
                            'Ip':"Dev1/ai20",
                            'Perfusion_1':"Dev1/port0/line20"
                            }
        
        Daq_sample_rate = samplingrate
        
        # some preparations for analog lines
        #Totalscansamplesnumber = len(analogsignals['Waveform'][0])
        Totalscansamplesnumber = 1000000
        num_rows, num_cols = analogsignals['Waveform'].shape
        print("row number of analog signals:  "+str(num_rows))
        
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
        self.analogsignal_dev2_number_continue = len(analogwritesamplesdev2_Sepcification)
        
        # Stack the Analog samples of dev1 and dev2 individually
        # IN CASE OF ONLY ONE ARRAY, WE NEED TO CONVERT THE SHAPE TO (1,N) BY USING np.array([]) OUTSIDE THE ARRAY!!
        #------------------------------------------!!_________________________
        if analogsignal_dev1_number == 1:            
            writesamples_dev1 = np.array([analogwritesamplesdev1[0]])

        elif analogsignal_dev1_number == 0:
            writesamples_dev1 = []
        else:
            writesamples_dev1 = analogwritesamplesdev1[0]    
            for i in range(1, analogsignal_dev1_number):
                writesamples_dev1 = np.vstack((writesamples_dev1, analogwritesamplesdev1[i]))
                
        if self.analogsignal_dev2_number_continue == 1:
            writesamples_dev2 = np.array([analogwritesamplesdev2[0]])
        elif self.analogsignal_dev2_number_continue == 0:
            writesamples_dev2 = []    
        else:
            writesamples_dev2 = analogwritesamplesdev2[0]
            for i in range(1, self.analogsignal_dev2_number_continue):
                writesamples_dev2 = np.vstack((writesamples_dev2, analogwritesamplesdev2[i]))
        
        # Assume that dev1 is always employed
        with nidaqmx.Task() as self.analog_dev1, nidaqmx.Task() as self.analog_dev2:
            # adding channels      
            # Set tasks from different devices apart
            for i in range(analogsignal_dev1_number):
                self.analog_dev1.ao_channels.add_ao_voltage_chan(analogwritesamplesdev1_Sepcification[i])
            
            # setting clock
            # Analog clock  USE clock on Dev1 as center clock
            self.analog_dev1.timing.cfg_samp_clk_timing(Daq_sample_rate, source='ai/SampleClock', sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamplesnumber)
            
            if self.analogsignal_dev2_number_continue != 0:
                # By default assume that read master task is in dev1
                
                for i in range(self.analogsignal_dev2_number_continue):
                    self.analog_dev2.ao_channels.add_ao_voltage_chan(analogwritesamplesdev2_Sepcification[i])
                
                dev2Clock = configs.clock2Channel#/Dev2/PFI1
                self.analog_dev2.timing.cfg_samp_clk_timing(Daq_sample_rate, source=dev2Clock, sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamplesnumber)
                #slave_Task_1_analog_dev2.triggers.sync_type.SLAVE = True
                
                #slave_Task_1_analog_dev2.triggers.start_trigger.cfg_dig_edge_start_trig(configs.trigger2Channel)#'/Dev2/PFI7'
                
                AnalogWriter = nidaqmx.stream_writers.AnalogMultiChannelWriter(self.analog_dev1.out_stream, auto_start= False)
                AnalogWriter.auto_start = False
                
                AnalogWriter_dev2 = nidaqmx.stream_writers.AnalogMultiChannelWriter(self.analog_dev2.out_stream, auto_start= False)
                AnalogWriter_dev2.auto_start = False

        	# Configure the writer and reader
            AnalogWriter = nidaqmx.stream_writers.AnalogMultiChannelWriter(self.analog_dev1.out_stream, auto_start= False)
            AnalogWriter.auto_start = False      
            
            # ---------------------------------------------------------------------------------------------------------------------
            #-----------------------------------------------------Begin to execute in DAQ------------------------------------------
            AnalogWriter.write_many_sample(writesamples_dev1, timeout = 16.0)
            
            if self.analogsignal_dev2_number_continue != 0:
                AnalogWriter_dev2.write_many_sample(writesamples_dev2, timeout = 16.0)
            
            if self.analogsignal_dev2_number_continue != 0:
                self.analog_dev2.start()            
            self.analog_dev1.start()
            
            self.analog_dev1.wait_until_done()
            if self.analogsignal_dev2_number_continue != 0:
                self.analog_dev2.wait_until_done()
                

               
    def stop_close(self):
        self.analog_dev1.stop()
        if self.analogsignal_dev2_number_continue != 0:
            self.analog_dev2.stop()
            
        self.analog_dev1.close()
        if self.analogsignal_dev2_number_continue != 0:
            self.analog_dev2.close()     
