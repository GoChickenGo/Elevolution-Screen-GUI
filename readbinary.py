# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 09:59:08 2019

@author: xinmeng

Based on basicanalysis matlab code: 'import2pdaq.m'
"""

import numpy as np
import os
#sizebytes = os.path.getsize('M:/tnw/ist/do/projects/Neurophotonics/Brinkslab/Data/Patch clamp/2019-03-01/20190301-165244/20190301-165244--data.Ip')
#inputfilename = 'M:/tnw/ist/do/projects/Neurophotonics/Brinkslab/Data/Patch clamp/2019-03-01/20190301-165244/20190301-165244--data.Ip'

class readbinaryfile():
    def __init__(self, filepath):
        self.filepath = filepath
        
    def readbinarycurve(self):    
        
        sizebytes = os.path.getsize(self.filepath)
        inputfilename = (self.filepath)
        
        with open(inputfilename, 'rb') as fid:
            data_array_h1 = np.fromfile(fid, count=2, dtype='>d')
            data_array_sc = np.fromfile(fid, count=(int(data_array_h1[0])*int(data_array_h1[1])), dtype='>d')
            data_array_sc=np.reshape(data_array_sc, (int(data_array_h1[0]), int(data_array_h1[1])), order='F')
            
            data_array_h1[1]=1
            data_array_sc = data_array_sc[:,1]
            
            data_array_samplesperchannel =  (sizebytes-fid.tell())/2/data_array_h1[1]
            
            data_array_udat = np.fromfile(fid, count=(int(data_array_h1[1])*int(data_array_samplesperchannel)), dtype='>H')#read as uint16
            data_array_udat_1 = data_array_udat.astype(np.int32)#convertdtype here as data might be saturated, out of uint16 range
            data_array_sdat = data_array_udat_1-(2**15)
            
        temp=np.ones(int(data_array_samplesperchannel))*data_array_sc[1]
        
        for i in range(1, int(data_array_h1[0])-1):
            L=(np.ones(int(data_array_samplesperchannel))*data_array_sc[i+1])*np.power(data_array_sdat, i)
            temp=temp+L
        
        data = temp
        srate= data_array_sc[0]
        
        return data, srate