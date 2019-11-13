# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 19:20:34 2019

@author: xinmeng
"""

import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType, TaskMode

Daq_sample_rate = 50000

b=np.array([0], dtype = bool)
writting_value = b

with nidaqmx.Task() as writingtask:
    writingtask.do_channels.add_do_chan("Dev1/port0/line20")
    writingtask.write(writting_value)
