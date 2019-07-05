# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 11:12:44 2019

@author: Meng
"""

import numpy as np

class generate_AO_for640():
    def __init__(self, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11):
        self.Daq_sample_rate = value1
        self.wavefrequency_2 = value2
        self.waveoffset_2 = value3
        self.waveperiod_2 = value4
        self.waveDC_2 = value5
        self.waverepeat_2 = value6
        self.wavegap_2 = value7
        self.wavestartamplitude_2 = value8
        self.wavebaseline_2 = value9
        self.wavestep_2 = value10
        self.wavecycles_2 = value11
        
    def generate(self):
        self.offsetsamples_number_2 = int(1 + (self.waveoffset_2/1000)*self.Daq_sample_rate) # By default one 0 is added so that we have a rising edge at the beginning.
        self.offsetsamples_2 = self.wavebaseline_2 * np.ones(self.offsetsamples_number_2) # Be default offsetsamples_number is an integer.
        
        self.sample_num_singleperiod_2 = round((int((self.waveperiod_2/1000)*self.Daq_sample_rate))/self.wavefrequency_2)
        self.true_sample_num_singleperiod_2 = round((self.waveDC_2/100)*self.sample_num_singleperiod_2)
        self.false_sample_num_singleperiod_2 = self.sample_num_singleperiod_2 - self.true_sample_num_singleperiod_2
        
        self.sample_singleperiod_2 = np.append(self.wavestartamplitude_2 * np.ones(self.true_sample_num_singleperiod_2), self.wavebaseline_2 * np.ones(self.false_sample_num_singleperiod_2))
        self.repeatnumberintotal_2 = self.wavefrequency_2*(self.waveperiod_2/1000)
        # In default, pulses * sample_singleperiod_2 = period
        self.sample_singlecycle_2 = np.tile(self.sample_singleperiod_2, int(self.repeatnumberintotal_2)) # At least 1 rise and fall during one cycle
        
        self.waveallcycle_2 = []
        # Adding steps to cycles
        for i in range(self.wavecycles_2):
            cycle_roof_value = self.wavestep_2 * i
            self.cycleappend = np.where(self.sample_singlecycle_2 < self.wavestartamplitude_2, self.wavebaseline_2, self.wavestartamplitude_2 + cycle_roof_value)
            self.waveallcycle_2 = np.append(self.waveallcycle_2, self.cycleappend)
        
        if self.wavegap_2 != 0:
            self.gapsample = self.wavebaseline_2 * np.ones(self.wavegap_2)
            self.waveallcyclewithgap_2 = np.append(self.waveallcycle_2, self.gapsample)
        else:
            self.waveallcyclewithgap_2 = self.waveallcycle_2
            
        self.waverepeated = np.tile(self.waveallcyclewithgap_2, self.waverepeat_2)
        
        self.finalwave_640 = np.append(self.offsetsamples_2, self.waverepeated)    
        
        return self.finalwave_640
    
class generate_AO_for488():
    def __init__(self, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11):
        self.Daq_sample_rate = value1
        self.wavefrequency_488 = value2
        self.waveoffset_488 = value3
        self.waveperiod_488 = value4
        self.waveDC_488 = value5
        self.waverepeat_488 = value6
        self.wavegap_488 = value7
        self.wavestartamplitude_488 = value8
        self.wavebaseline_488 = value9
        self.wavestep_488 = value10
        self.wavecycles_488 = value11
        
    def generate(self):
        self.offsetsamples_number_488 = int(1 + (self.waveoffset_488/1000)*self.Daq_sample_rate) # By default one 0 is added so that we have a rising edge at the beginning.
        self.offsetsamples_488 = self.wavebaseline_488 * np.ones(self.offsetsamples_number_488) # Be default offsetsamples_number is an integer.
        
        self.sample_num_singleperiod_488 = round((int((self.waveperiod_488/1000)*self.Daq_sample_rate))/self.wavefrequency_488)
        self.true_sample_num_singleperiod_488 = round((self.waveDC_488/100)*self.sample_num_singleperiod_488)
        self.false_sample_num_singleperiod_488 = self.sample_num_singleperiod_488 - self.true_sample_num_singleperiod_488
        
        self.sample_singleperiod_488 = np.append(self.wavestartamplitude_488 * np.ones(self.true_sample_num_singleperiod_488), self.wavebaseline_488 * np.ones(self.false_sample_num_singleperiod_488))
        self.repeatnumberintotal_488 = self.wavefrequency_488*(self.waveperiod_488/1000)
        # In default, pulses * sample_singleperiod_2 = period
        self.sample_singlecycle_488 = np.tile(self.sample_singleperiod_488, int(self.repeatnumberintotal_488)) # At least 1 rise and fall during one cycle
        
        self.waveallcycle_488 = []
        # Adding steps to cycles
        for i in range(self.wavecycles_488):
            cycle_roof_value = self.wavestep_488 * i
            self.cycleappend = np.where(self.sample_singlecycle_488 < self.wavestartamplitude_488, self.wavebaseline_488, self.wavestartamplitude_488 + cycle_roof_value)
            self.waveallcycle_488 = np.append(self.waveallcycle_488, self.cycleappend)
        
        if self.wavegap_488 != 0:
            self.gapsample = self.wavebaseline_488 * np.ones(self.wavegap_488)
            self.waveallcyclewithgap_488 = np.append(self.waveallcycle_488, self.gapsample)
        else:
            self.waveallcyclewithgap_488 = self.waveallcycle_488
            
        self.waverepeated = np.tile(self.waveallcyclewithgap_488, self.waverepeat_488)
        
        self.finalwave_488 = np.append(self.offsetsamples_488, self.waverepeated)    
        
        return self.finalwave_488
    
class generate_AO_for532():
    def __init__(self, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11):
        self.Daq_sample_rate = value1
        self.wavefrequency_532 = value2
        self.waveoffset_532 = value3
        self.waveperiod_532 = value4
        self.waveDC_532 = value5
        self.waverepeat_532 = value6
        self.wavegap_532 = value7
        self.wavestartamplitude_532 = value8
        self.wavebaseline_532 = value9
        self.wavestep_532 = value10
        self.wavecycles_532 = value11
        
    def generate(self):
        self.offsetsamples_number_532 = int(1 + (self.waveoffset_532/1000)*self.Daq_sample_rate) # By default one 0 is added so that we have a rising edge at the beginning.
        self.offsetsamples_532 = self.wavebaseline_532 * np.ones(self.offsetsamples_number_532) # Be default offsetsamples_number is an integer.
        
        self.sample_num_singleperiod_532 = round((int((self.waveperiod_532/1000)*self.Daq_sample_rate))/self.wavefrequency_532)
        self.true_sample_num_singleperiod_532 = round((self.waveDC_532/100)*self.sample_num_singleperiod_532)
        self.false_sample_num_singleperiod_532 = self.sample_num_singleperiod_532 - self.true_sample_num_singleperiod_532
        
        self.sample_singleperiod_532 = np.append(self.wavestartamplitude_532 * np.ones(self.true_sample_num_singleperiod_532), self.wavebaseline_532 * np.ones(self.false_sample_num_singleperiod_532))
        self.repeatnumberintotal_532 = self.wavefrequency_532*(self.waveperiod_532/1000)
        # In default, pulses * sample_singleperiod_2 = period
        self.sample_singlecycle_532 = np.tile(self.sample_singleperiod_532, int(self.repeatnumberintotal_532)) # At least 1 rise and fall during one cycle
        
        self.waveallcycle_532 = []
        # Adding steps to cycles
        for i in range(self.wavecycles_532):
            cycle_roof_value = self.wavestep_532 * i
            self.cycleappend = np.where(self.sample_singlecycle_532 < self.wavestartamplitude_532, self.wavebaseline_532, self.wavestartamplitude_532 + cycle_roof_value)
            self.waveallcycle_532 = np.append(self.waveallcycle_532, self.cycleappend)
        
        if self.wavegap_532 != 0:
            self.gapsample = self.wavebaseline_532 * np.ones(self.wavegap_532)
            self.waveallcyclewithgap_532 = np.append(self.waveallcycle_532, self.gapsample)
        else:
            self.waveallcyclewithgap_532 = self.waveallcycle_532
            
        self.waverepeated = np.tile(self.waveallcyclewithgap_532, self.waverepeat_532)
        
        self.finalwave_532 = np.append(self.offsetsamples_532, self.waverepeated)    
        
        return self.finalwave_532
    
class generate_DO_forcameratrigger():
    def __init__(self, value1, value2, value3, value4, value5, value6, value7):
        self.Daq_sample_rate = value1
        self.wavefrequency_cameratrigger = value2
        self.waveoffset_cameratrigger = value3
        self.waveperiod_cameratrigger = value4
        self.waveDC_cameratrigger = value5
        self.waverepeat_cameratrigger_number = value6
        self.wavegap_cameratrigger = value7
        
    def generate(self):
        
        self.offsetsamples_number_cameratrigger = int(1 + (self.waveoffset_cameratrigger/1000)*self.Daq_sample_rate) # By default one 0 is added so that we have a rising edge at the beginning.
        self.offsetsamples_cameratrigger = np.zeros(self.offsetsamples_number_cameratrigger, dtype=bool) # Be default offsetsamples_number is an integer.
        
        self.sample_num_singleperiod_cameratrigger = round((int((self.waveperiod_cameratrigger/1000)*self.Daq_sample_rate))/self.wavefrequency_cameratrigger)
        self.true_sample_num_singleperiod_cameratrigger = round((self.waveDC_cameratrigger/100)*self.sample_num_singleperiod_cameratrigger)
        self.false_sample_num_singleperiod_cameratrigger = self.sample_num_singleperiod_cameratrigger - self.true_sample_num_singleperiod_cameratrigger
        
        self.sample_singleperiod_cameratrigger = np.append(np.ones(self.true_sample_num_singleperiod_cameratrigger, dtype=bool), np.zeros(self.false_sample_num_singleperiod_cameratrigger, dtype=bool))
        self.repeatnumberintotal_cameratrigger = self.wavefrequency_cameratrigger*(self.waveperiod_cameratrigger/1000)
        # In default, pulses * sample_singleperiod_2 = period
        self.sample_singlecycle_cameratrigger = np.tile(self.sample_singleperiod_cameratrigger, int(self.repeatnumberintotal_cameratrigger)) # At least 1 rise and fall during one cycle
        
        if self.wavegap_cameratrigger != 0:
            self.gapsample_cameratrigger = np.zeros(self.wavegap_cameratrigger, dtype=bool)
            self.waveallcyclewithgap_cameratrigger = np.append(self.sample_singlecycle_cameratrigger, self.gapsample_cameratrigger)
        else:
            self.waveallcyclewithgap_cameratrigger = self.sample_singlecycle_cameratrigger
            
        self.waverepeated_cameratrigger = np.tile(self.waveallcyclewithgap_cameratrigger, self.waverepeat_cameratrigger_number)
        
        self.finalwave_cameratrigger = np.append(self.offsetsamples_cameratrigger, self.waverepeated_cameratrigger)
        
        return self.finalwave_cameratrigger
    
class generate_DO_for640blanking():
    def __init__(self, value1, value2, value3, value4, value5, value6, value7):
        self.Daq_sample_rate = value1
        self.wavefrequency_640blanking = value2
        self.waveoffset_640blanking = value3
        self.waveperiod_640blanking = value4
        self.waveDC_640blanking = value5
        self.waverepeat_640blanking_number = value6
        self.wavegap_640blanking = value7
        
    def generate(self):
        
        self.offsetsamples_number_640blanking = int(1 + (self.waveoffset_640blanking/1000)*self.Daq_sample_rate) # By default one 0 is added so that we have a rising edge at the beginning.
        self.offsetsamples_640blanking = np.zeros(self.offsetsamples_number_640blanking, dtype=bool) # Be default offsetsamples_number is an integer.
        
        self.sample_num_singleperiod_640blanking = round((int((self.waveperiod_640blanking/1000)*self.Daq_sample_rate))/self.wavefrequency_640blanking)
        self.true_sample_num_singleperiod_640blanking = round((self.waveDC_640blanking/100)*self.sample_num_singleperiod_640blanking)
        self.false_sample_num_singleperiod_640blanking = self.sample_num_singleperiod_640blanking - self.true_sample_num_singleperiod_640blanking
        
        self.sample_singleperiod_640blanking = np.append(np.ones(self.true_sample_num_singleperiod_640blanking, dtype=bool), np.zeros(self.false_sample_num_singleperiod_640blanking, dtype=bool))
        self.repeatnumberintotal_640blanking = self.wavefrequency_640blanking*(self.waveperiod_640blanking/1000)
        # In default, pulses * sample_singleperiod_2 = period
        self.sample_singlecycle_640blanking = np.tile(self.sample_singleperiod_640blanking, int(self.repeatnumberintotal_640blanking)) # At least 1 rise and fall during one cycle
        
        if self.wavegap_640blanking != 0:
            self.gapsample_640blanking = np.zeros(self.wavegap_640blanking, dtype=bool)
            self.waveallcyclewithgap_640blanking = np.append(self.sample_singlecycle_640blanking, self.gapsample_640blanking)
        else:
            self.waveallcyclewithgap_640blanking = self.sample_singlecycle_640blanking
            
        self.waverepeated_640blanking = np.tile(self.waveallcyclewithgap_640blanking, self.waverepeat_640blanking_number)
        
        self.finalwave_640blanking = np.append(self.offsetsamples_640blanking, self.waverepeated_640blanking)
        
        return self.finalwave_640blanking