# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 11:54:58 2019

@author: lhuismans

This class contains all the constants that are frequently used and will stay unchanged
(for a long time).
"""

class MeasurementConstants:
    def __init__(self):
        self.patchSealSampRate = 5000 #Samples/s
        
class HardwareConstants:
    def __init__(self):
        self.maxGalvoSpeed = 20000.0 #Volt/s
        self.maxGalvoAccel = 1.54*10**8 #Acceleration galvo in volt/s^2