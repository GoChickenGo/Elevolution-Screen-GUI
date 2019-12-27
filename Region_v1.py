# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 15:23:11 2019

@author: Meng
"""

import numpy as np
from trymageAnalysis_v3 import ImageAnalysis
from skimage.io import imread
from PIL import Image
import matplotlib.pyplot as plt
from IPython import get_ipython
from matplot import SelectFromCollection
import numpy.lib.recfunctions as rfn

Rawimgbef = imread(r'M:\tnw\ist\do\projects\Neurophotonics\Brinkslab\People\Xin Meng\Code\Daq_1.tif', as_gray=True)#(r"O:\Delft\data\PMT__2019-11-08_14-55-56.tif", as_gray=True)
Rawimgaft = imread(r'M:\tnw\ist\do\projects\Neurophotonics\Brinkslab\People\Xin Meng\Code\Daq_2.tif', as_gray=True)#(r"O:\Delft\data\PMT__2019-11-08_14-55-56.tif", as_gray=True)

Data_dict_0 = {}
Data_dict_0[str(-1500)+str(-1500)] = Rawimgbef[:, 15:515]#[134:360, 450:600]#[180:290, 220:330]###[40:100,300:350]
imagrarray = Rawimgbef#[40:100,300:350]

Data_dict_1 = {}
Data_dict_1[str(-1500)+str(-1500)] = Rawimgaft[:, 15:515]#[134:360, 450:600]#[180:290, 220:330]##[:, 53:553]#[40:100,300:350]

S = ImageAnalysis(Data_dict_0[str(-1500)+str(-1500)], Data_dict_1[str(-1500)+str(-1500)])
v1, v2, mask_1, mask_2, thres = S.applyMask(2,2,335)

cp, coutourmask, coutourimg, intensityimage_intensity, r = S.get_intensity_properties(300, mask_1, thres, v1, v2, -1500, -1500, 0.001,10, 1, 5)
#get_ipython().run_line_magic('matplotlib', 'qt')
S.showlabel(300, mask_1, v1, thres, -1500, -1500, cp)

cp = rfn.append_fields(cp, 'Original_sequence', list(range(0, len(cp))), usemask=False)
print (cp)

sorted_cp = S.sort_using_weight(cp, 'Circularity', 'Mean intensity in contour', 0.5, 0.5)
#mouse_select_points(cp['Circularity'], cp['Mean intensity in contour'])
