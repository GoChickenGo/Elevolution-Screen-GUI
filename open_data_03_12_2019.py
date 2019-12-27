#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 11:18:11 2019

@author: sabinejonkman
"""

import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
import numpy as np
import math
import os
from sklearn.linear_model import LinearRegression
from IPython import get_ipython
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
get_ipython().run_line_magic('matplotlib', 'qt')
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import scipy
from scipy import optimize
from scipy.optimize import curve_fit
from scipy.special import expit
from matplotlib import style
import matplotlib.font_manager as font_manager

style.use('seaborn-white')

# open the saved numpy arrays containing the weighted traces and save them in a variable  
savedirectory = os.path.join(os.path.expanduser("~"), r"M:\tnw\ist\do\projects\Neurophotonics\Brinkslab\Data\Sabine\3-12-2019")
data_1 = np.load(savedirectory + '/Weighted_trace 0312_1.npy',mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
data_2 = np.load(savedirectory + '/Weighted_trace 0312_2.npy',mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
data_3 = np.load(savedirectory + '/Weighted_trace 0312_3.npy',mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
data_4 = np.load(savedirectory + '/Weighted_trace 0312_4.npy',mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
data_5 = np.load(savedirectory + '/Weighted_trace 0312_5.npy',mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
data_6 = np.load(savedirectory + '/Weighted_trace 0312_6.npy',mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
#data_7 = np.load(savedirectory + '/Weighted_trace 2211_7.npy',mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
#data_8 = np.load(savedirectory + '/Weighted_trace 2211_8.npy',mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')
#data_9 = np.load(savedirectory + '/Weighted_trace 2211_9.npy',mmap_mode=None, allow_pickle=False, fix_imports=True, encoding='ASCII')

data_1_offset = np.min(data_1)
data_2_offset = np.min(data_2)
data_3_offset = np.min(data_3)
data_4_offset = np.min(data_4)
data_5_offset = np.min(data_5)
data_6_offset = np.min(data_6)
smallest_offset = np.min([data_1_offset, data_2_offset, data_3_offset, data_4_offset, data_5_offset, data_6_offset])

# correct for the camera noise by subtracting the average pixel value when there is no laser on 
data_1 = [x - 100 for x in data_1]
data_2 = [x - 100 for x in data_2]
data_3 = [x - 100 for x in data_3]
data_4 = [x - 100 for x in data_4]
data_5 = [x - 100 for x in data_5]
data_6 = [x - 100 for x in data_6]
#data_7 = [x - 100 for x in data_7]
#data_8 = [x - 100 for x in data_8]
#data_9 = [x - 100 for x in data_9]

# open the saved numpy arrays containing input waveform and save them into a variable 
savedirectory2 = os.path.join(os.path.expanduser("~"), r"M:\tnw\ist\do\projects\Neurophotonics\Brinkslab\Data\Sabine\3-12-2019")
waveform_1 = np.load(savedirectory2 + '/2019-12-03_17-01-28__Wavefroms_sr_50000.npy',mmap_mode=None, allow_pickle=True, fix_imports=True, encoding='ASCII')
waveform_2 = np.load(savedirectory2 + '/2019-12-03_17-02-05__Wavefroms_sr_50000.npy',mmap_mode=None, allow_pickle=True, fix_imports=True, encoding='ASCII')
waveform_3 = np.load(savedirectory2 + '/2019-12-03_17-02-49__Wavefroms_sr_50000.npy',mmap_mode=None, allow_pickle=True, fix_imports=True, encoding='ASCII')
waveform_4 = np.load(savedirectory2 + '/2019-12-03_17-03-41__Wavefroms_sr_50000.npy',mmap_mode=None, allow_pickle=True, fix_imports=True, encoding='ASCII')
waveform_5 = np.load(savedirectory2 + '/2019-12-03_17-04-37__Wavefroms_sr_50000.npy',mmap_mode=None, allow_pickle=True, fix_imports=True, encoding='ASCII')
waveform_6 = np.load(savedirectory2 + '/2019-12-03_17-05-12__Wavefroms_sr_50000.npy',mmap_mode=None, allow_pickle=True, fix_imports=True, encoding='ASCII')
#waveform_7 = np.load(savedirectory2 + '/2019-11-29_12-27-41__Wavefroms_sr_50000.npy',mmap_mode=None, allow_pickle=True, fix_imports=True, encoding='ASCII')
#waveform_8 = np.load(savedirectory2 + '/2019-11-29_12-28-44__Wavefroms_sr_50000.npy',mmap_mode=None, allow_pickle=True, fix_imports=True, encoding='ASCII')

# extract the data from the waveform numpy arrays 
def open_waveform(data):
    data_list = np.ndarray.tolist(data) # convert it to a list
    data_tuple_red = data_list[0] # select the red laser tuple
    data_red = data_tuple_red[0] # select the intensities 

    data_tuple_blue = data_list[1] # select the blue laser tuple
    data_blue = data_tuple_blue[0] # select the intensities 

    data_tuple_green = data_list[2] # select the green laser tuple
    data_green = data_tuple_green[0] # select the intensities 

    t = np.array(range(0,len(data_blue))) # calculate the lengths of the waveform
    t = t/50000 # devide by the sampling rate
    return [t, data_red, data_blue, data_green] # return the time, and the laser intensities

# save the data ina return array 
result = open_waveform(waveform_1)
result_2 = open_waveform(waveform_2)
result_3 = open_waveform(waveform_3)
result_4 = open_waveform(waveform_4)
result_5 = open_waveform(waveform_5)
result_6 = open_waveform(waveform_6)
#result_7 = open_waveform(waveform_7)
#result_8 = open_waveform(waveform_8)
#result_9 = open_waveform(waveform_9)


sampling_rate = 250 # frames per second of the camera

#create a time x-axis for each dataset 
t = np.array(range(0,len(data_1)))/sampling_rate
t_2 = np.array(range(0,len(data_2)))/sampling_rate
t_3 = np.array(range(0,len(data_3)))/sampling_rate
t_4 = np.array(range(0,len(data_4)))/sampling_rate
t_5 = np.array(range(0,len(data_5)))/sampling_rate
t_6 = np.array(range(0,len(data_6)))/sampling_rate

# plotting the data of the input and the output for all the datasets 
fig1, axs = plt.subplots(2)
axs[1].plot(t,data_1)
axs[0].plot(result[0],result[1],'r') # plot
axs[0].plot(result[0],result[2], 'b') # plot
axs[0].plot(result[0],result[3], 'g') # plot
axs[0].set_title('Blue increasing  green constant')

fig2, axs = plt.subplots(2)
axs[1].plot(t_2,data_2)
axs[0].plot(result_2[0],result_2[1],'r') # plot
axs[0].plot(result_2[0],result_2[2], 'b') # plot
axs[0].plot(result_2[0],result_2[3], 'g') # plot
axs[0].set_title('Blue increasing red constant')

fig3, axs = plt.subplots(2)
axs[1].plot(t_3,data_3)
axs[0].plot(result_3[0],result_3[1],'r') # plot
axs[0].plot(result_3[0],result_3[2], 'b') # plot
axs[0].plot(result_3[0],result_3[3], 'g') # plot
axs[0].set_title('Green increasing blue constant')

fig4, axs = plt.subplots(2)
axs[1].plot(t_4,data_4)
axs[0].plot(result_4[0],result_4[1],'r') # plot
axs[0].plot(result_4[0],result_4[2], 'b') # plot
axs[0].plot(result_4[0],result_4[3], 'g') # plot
axs[0].set_title('Green first red second')

fig5, axs = plt.subplots(2)
axs[1].plot(t_5,data_5)
axs[0].plot(result_5[0],result_5[1],'r') # plot
axs[0].plot(result_5[0],result_5[2], 'b') # plot
axs[0].plot(result_5[0],result_5[3], 'g') # plot
axs[0].set_title('Red increasing green constant')

fig6, axs = plt.subplots(2)
axs[1].plot(t_6,data_6)
axs[0].plot(result_6[0],result_6[1],'r') # plot
axs[0].plot(result_6[0],result_6[2], 'b') # plot
axs[0].plot(result_6[0],result_6[3], 'g') # plot
axs[0].set_title('Red increasing blue constant')

#fig7 = plt.figure(7)
#plt.plot(t_7,data_7)
#title_7 = plt.title('Green first red second')
#
#fig8 = plt.figure(8)
#plt.plot(t_8,data_8)
#title_8 = plt.title('Green first blue second')
#
#fig9 = plt.figure(9)
#plt.plot(t_9,data_9)
#title_9 = plt.title('Blue first green second')

# split the data in parts where the laser intensity is equal 
def splitting_data(data):
    amount_movies = 31# amount of different laser intensities, including control and laser off periods 
    time_sample = 0 # initializing the time variable 
    time_sample_not_round = 0 # initializing the time variable 
    result_list = [] 
    time_list = []
    first_point = []
    last_point = []
    first_point_control = []
    for i in range(amount_movies):
        if i==0:
            length_sample = 47 #46.875 #samples 
        else:
            length_sample = 31.25
        time_sample_start_nr = time_sample_not_round
        time_sample_start = int(round(time_sample_start_nr,0)) + 1
        time_sample_not_round = time_sample_not_round + length_sample 
        time_sample = int(round((time_sample_not_round),0))
        a = time_sample_start
        b = time_sample 
        result_array = []
        time_array = []
        t = 0;
        result_first = data[a]
        result_last = data[b]
        while a<b:
             result = data[a]
             a = a + 1;
             t = t+1
             result_array = np.append(result_array, result)
             time_array = np.append(time_array, t)
             
        result_list.append(result_array) 
        time_list.append(time_array) 
        range_var = list(range(2,31,4))
        if i in range_var:
            first_point = np.append(first_point, result_first)
            last_point = np.append(last_point, result_last)
        range_var_control = list(range(4,31,4))
        if i in range_var_control:
            first_point_control.append(result_first)
    return result_list, time_list, first_point, last_point,first_point_control


def regression(result,time):
    result_1 = result
    result_1_reshape = result_1.reshape(-1, 1)
    result_1_array = np.array(result_1_reshape)
    t_1 = time
    t_1_reshape = t_1.reshape(-1, 1)
    t_1_array = np.array(t_1_reshape)
    regression_model = LinearRegression()
    regression_model.fit(t_1_reshape,result_1_reshape)
    y_predicted = regression_model.predict(t_1_reshape)
    score_linear = regression_model.score(t_1_reshape, result_1_reshape)
    coef1 = regression_model.coef_
    intercept_linear = regression_model.intercept_
    y_plot_1 = []
    for count, degree in enumerate([2]):
        model = make_pipeline(PolynomialFeatures(degree), Ridge())
        model.fit(t_1_reshape, result_1_reshape)
        y_plot_1 = np.append(y_plot_1, model.predict(t_1_reshape))
        parameters = model.get_params(deep=True)
    def func(x, aa, bb, c):
            bb = bb/100
            return aa * np.exp(-bb * x) + c    
    xdata = t_1
    ydata = result_1
    try:
        popt, pcov = optimize.curve_fit(func, xdata, ydata,maxfev=1000)
        aa = popt[0]
        bb = popt[1]*100
        cc = popt[2]
        y_exp = func(xdata, *popt)
    except (RuntimeError): 
        pass
        aa = 0
        bb = 0
        cc = 0
        y_exp = func(xdata, aa, bb, cc)
    return [t_1,result_1,y_predicted,y_plot_1,y_exp,score_linear,coef1,intercept_linear, aa, bb, cc, parameters]

figs2 = {}
axs2 = {}

data_matrix = [data_1, data_2, data_3, data_4, data_5, data_6]
power_640 = [21, 37, 52, 67, 74, 90, 95, 90]
power_532 = [11, 18, 25, 33, 36, 45, 47, 50]
power_433 = [1.5, 2.5, 3.7, 4.5, 4.8, 5.8, 6, 6.8]

# def correction_first(index):
#     laser_on_corrected = []
#     ww = 0
#     result_list, time_list, first_point, last_point, first_point_control = splitting_data(data_matrix[index])
#     def substract_first(data_laser_on, data_laser_off):
#         average_value = np.average(data_laser_off)
#         data_laser_on = data_laser_on - average_value 
#         return data_laser_on
#     for qq in range(0,31,4): 
#         correct = substract_first(first_point[ww], result_list[qq])
#         laser_on_corrected.append(correct)
#         ww = ww + 1
#     return laser_on_corrected 

def correction_first(first_point):
    laser_on_corrected = []
    firstpoints_data = splitting_data(data_matrix[hh])
    def substract_first(data_laser_on, data_laser_off):
        average_value = np.average(data_laser_off)
        data_laser_on = data_laser_on - average_value 
        return data_laser_on
    for qq in list(range(1,30,4)): 
        correct = substract_first(first_point[qq], firstpoints_data[0][qq-1])
        laser_on_corrected.append(correct)
    return laser_on_corrected 

fig = plt.figure()
first_point_control_matrix = []
for hh in range(6):
    firstpoint = []
    first_point_control = []
    firstpoints_data = splitting_data(data_matrix[hh])
    for tt in range(31):
        firstpoint.append(firstpoints_data[0][tt][1])
    firstpoints_corrected = correction_first(firstpoint)
    # firstpoints = splitting_data(data_matrix[hh])
    # firstpoints_corrected = correction_first(hh)
    print(firstpoint[3])
    for rr in list(range(3,30,4)): 
        first_point_control.append(firstpoint[rr])
    first_point_control_matrix.append(first_point_control)
    average = np.average(first_point_control)
    error = [x/average for x in first_point_control]
    percentage = [x - 1 for x in error]
    percentage_max = max(percentage)
    percentage_min = min(percentage)
    dy_min = [x*percentage_min for x in firstpoints_corrected]
    dy_max = [x*percentage_max for x in firstpoints_corrected]
    dy_min = np.asarray(dy_min)
    dy_max = np.asarray(dy_max)
    if hh in [0,1]:           
        axs2[hh]=fig.add_subplot(311)
        if hh == 0:
            axs2[hh].plot(power_433, firstpoints_corrected,'g.', label='Green constant')
        if hh == 1:
            axs2[hh].plot(power_433, firstpoints_corrected,'r.', label='Red constant')
        axs2[hh].set_title('Blue')
        axs2[hh].set_xlabel('Laser power (W)')
        axs2[hh].set_ylabel('Fluorescence response')
        axs2[hh].xaxis.set_label_coords(1, -0.2)
        axs2[hh].fill_between(power_433, firstpoints_corrected - dy_min, firstpoints_corrected + dy_max, color='gray', alpha=0.2)
        axs2[hh].set_xlim([2,7])
        leg = plt.legend();
        axs2[hh].legend(bbox_to_anchor=(1.1, 1.05))
    if hh in [2]:
        axs2[hh]=fig.add_subplot(313)
        axs2[hh].plot(power_532, firstpoints_corrected,'b.', label = 'Blue constant')
        axs2[hh].set_title('Green')
        axs2[hh].set_xlabel('Laser power (W) ')
        axs2[hh].xaxis.set_label_coords(1, -0.2)
        axs2[hh].set_ylabel('Fluorescence response')
        axs2[hh].fill_between(power_532, firstpoints_corrected - dy_min, firstpoints_corrected + dy_max, color='gray', alpha=0.2)
        leg = plt.legend();
        axs2[hh].legend(bbox_to_anchor=(1.1, 1.05))
    if hh in [3,4,5]:
        axs2[hh]=fig.add_subplot(312)
        if hh==3:
            axs2[hh].plot(power_640, firstpoints_corrected,'g.', label = 'Green constant')
        if hh==4:
            axs2[hh].plot(power_640, firstpoints_corrected,'g.', label = 'Green constant')
        if hh==5:
            axs2[hh].plot(power_640, firstpoints_corrected,'b.', label = 'Blue constant')
        axs2[hh].set_title('Red')
        axs2[hh].set_xlabel('Laser power (W)')
        axs2[hh].xaxis.set_label_coords(1, -0.2)
        axs2[hh].set_ylabel('Fluorescence response')
        axs2[hh].fill_between(power_640, firstpoints_corrected - dy_min, firstpoints_corrected + dy_max, color='gray', alpha=0.2)
        leg = plt.legend();
        axs2[hh].legend(bbox_to_anchor=(1.1, 1.05))
    plt.subplots_adjust(top=0.849,bottom=0.121,left=0.126,right=0.9,hspace=1.0,wspace=1.0)
fig.suptitle('Response to different laser power')
plt.rc('figure', titlesize=12) 
plt.rc('axes', titlesize=8)     # fontsize of the axes title
plt.rc('axes', labelsize=8)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=8)    # fontsize of the tick labels
plt.rc('ytick', labelsize=8)    # fontsize of the tick labels
plt.rc('legend', fontsize=8)    # legend fontsize

fig = plt.figure()
plt.plot(first_point_control_matrix[0])
fig = plt.figure()
plt.plot(first_point_control_matrix[1])
fig = plt.figure()
plt.plot(first_point_control_matrix[2])
fig = plt.figure()
plt.plot(first_point_control_matrix[3])
fig = plt.figure()
plt.plot(first_point_control_matrix[4])
fig = plt.figure()
plt.plot(first_point_control_matrix[5])

def correction_last(last_point):
    laser_on_corrected = []
    lastpoints_data = splitting_data(data_matrix[hh])
    def substract_first(data_laser_on, data_laser_off):
        average_value = np.average(data_laser_off)
        data_laser_on = data_laser_on - average_value 
        return data_laser_on
    for qq in list(range(1,30,4)): 
        correct = substract_first(last_point[qq], lastpoints_data[0][qq-1])
        laser_on_corrected.append(correct)
    return laser_on_corrected 

fig = plt.figure()
for hh in range(6):
    lastpoint = []
    lastpoints_data = splitting_data(data_matrix[hh])
    for tt in range(31):
        lastpoint.append(lastpoints_data[0][tt][-1])
    lastpoints_corrected = correction_last(lastpoint)
    average = np.average(lastpoints_data[4])
    error = [x/average for x in lastpoints_data[4]]
    percentage = [x - 1 for x in error]
    percentage_max = max(percentage)
    percentage_min = min(percentage)
    dy_min = [x*percentage_min for x in lastpoints_corrected]
    dy_max = [x*percentage_max for x in lastpoints_corrected]
    dy_min = np.asarray(dy_min)
    dy_max = np.asarray(dy_max)
    if hh in [0,1]:           
        axs2[hh]=fig.add_subplot(311)
        if hh == 0:
            axs2[hh].plot(power_433, lastpoints_corrected,'g.', label='Green constant')
        if hh == 1:
            axs2[hh].plot(power_433, lastpoints_corrected,'r.', label='Red constant')
        axs2[hh].set_title('Blue')
        axs2[hh].set_xlabel('Laser power (W)')
        axs2[hh].set_ylabel('Fluorescence response')
        axs2[hh].xaxis.set_label_coords(1, -0.2)
        axs2[hh].fill_between(power_433, lastpoints_corrected - dy_min, lastpoints_corrected + dy_max, color='gray', alpha=0.2)
        axs2[hh].set_xlim([2,7])
        leg = plt.legend();
        axs2[hh].legend(bbox_to_anchor=(1.1, 1.05))
    if hh in [2]:
        axs2[hh]=fig.add_subplot(313)
        axs2[hh].plot(power_532, lastpoints_corrected,'b.', label = 'Blue constant')
        axs2[hh].set_title('Green')
        axs2[hh].set_xlabel('Laser power (W) ')
        axs2[hh].xaxis.set_label_coords(1, -0.2)
        axs2[hh].set_ylabel('Fluorescence response')
        axs2[hh].fill_between(power_532, lastpoints_corrected - dy_min, lastpoints_corrected + dy_max, color='gray', alpha=0.2)
        leg = plt.legend();
        axs2[hh].legend(bbox_to_anchor=(1.1, 1.05))
    if hh in [3,4,5]:
        axs2[hh]=fig.add_subplot(312)
        if hh==3:
            axs2[hh].plot(power_640, lastpoints_corrected,'g.', label = 'Green constant')
        if hh==4:
            axs2[hh].plot(power_640, lastpoints_corrected,'g.', label = 'Green constant')
        if hh==5:
            axs2[hh].plot(power_640, lastpoints_corrected,'b.', label = 'Blue constant')
        axs2[hh].set_title('Red')
        axs2[hh].set_xlabel('Laser power (W)')
        axs2[hh].xaxis.set_label_coords(1, -0.2)
        axs2[hh].set_ylabel('Fluorescence response')
        axs2[hh].fill_between(power_640, lastpoints_corrected - dy_min, lastpoints_corrected + dy_max, color='gray', alpha=0.2)
        leg = plt.legend();
        axs2[hh].legend(bbox_to_anchor=(1.1, 1.05))
    plt.subplots_adjust(top=0.849,bottom=0.121,left=0.126,right=0.9,hspace=1.0,wspace=1.0)
fig.suptitle('Response to different laser power')
plt.rc('figure', titlesize=12) 
plt.rc('axes', titlesize=8)     # fontsize of the axes title
plt.rc('axes', labelsize=8)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=8)    # fontsize of the tick labels
plt.rc('ytick', labelsize=8)    # fontsize of the tick labels
plt.rc('legend', fontsize=8)    # legend fontsize

# figs3 = {}
# axs3 = {} 
# for zz in range(6):
#     lastpoints = splitting_data(data_matrix[hh])
#     figs3[zz] = plt.figure()
#     plt.plot(lastpoints[2])
#     plt.plot(lastpoints[3])

def correction(index):
    laser_on_corrected = []
    result_list, time_list, first_point, last_point, first_point_control = splitting_data(data_matrix[index])
    def substract(data_laser_on, data_laser_off):
        average_value = np.average(data_laser_off)
        data_laser_on = [x - average_value for x in data_laser_on]
        return data_laser_on
    for qq in range(0,31,4): 
        correct = substract(result_list[qq+1], result_list[qq])
        laser_on_corrected.append(correct)
    return laser_on_corrected 
  
laser_on_corrected_1 = correction(0)
laser_on_corrected_2 = correction(1)
laser_on_corrected_3 = correction(2)
laser_on_corrected_4 = correction(3)
laser_on_corrected_5 = correction(4)
laser_on_corrected_6 = correction(5)
time_laser_corrected = np.arange(0,(len(laser_on_corrected_1[0])/sampling_rate), (1/sampling_rate))
     
figs={}
axs={}  
a_corrected = []
b_corrected = []
c_corrected = []
for jj in range(8): 
    laser_on_corrected_extract = laser_on_corrected_2[jj]
    laser_on_corrected_extract_2  = np.asarray(laser_on_corrected_extract)
    regression_result = regression(laser_on_corrected_extract_2,time_laser_corrected)
    extract = regression_result[6] ; extract_2 = extract[0] ; extract_3= extract_2[0] ; extract_4 = regression_result[7]; extract_5= extract_4[0]; extract_6 = regression_result[7]; extract_7 = extract_6[0]      
    figs[jj] = plt.figure()
    # axs[jj]=figs[jj].add_subplot(221)
    plt.plot(time_laser_corrected, laser_on_corrected_extract_2, label = 'data set corrected: '+ str(1) + 'sample number ' + str(jj))
    leg = plt.legend();
    # axs[jj]=figs[jj].add_subplot(222)
    plt.plot(regression_result[0], regression_result[2],label='score = '+ str(round(regression_result[5],2)) + ' a = ' + str(round(extract_3, 2)) + ' b = ' + str(round(extract_5)) + 'in ax + b')
    leg = plt.legend();
    # axs[jj]=figs[jj].add_subplot(223)
    plt.plot(regression_result[0], regression_result[3])
    leg = plt.legend();
    # axs[jj]=figs[jj].add_subplot(224)
    plt.plot(regression_result[0], regression_result[4], label = 'a = ' + str(round(extract_7,2)) +' b = ' + str(round(regression_result[8],2))+ ' c = ' + str(round(regression_result[9],2)) + ' in a*exp(-b*x) + c')
    leg = plt.legend();
    a_corrected.append(round(extract_7,2))
    b_corrected.append(round(regression_result[8],2))
    c_corrected.append(round(regression_result[9],2))
    
def get_high_values(x): 
    range_var = list(range(1,31,4))
    x_high = []
    for tt in range(len(x)):
        if tt in range_var:
            x_high = np.append(x_high, x[tt])
    return x_high

fig20 = plt.figure()
plt.subplot(3, 1, 1)
plt.plot(a_corrected,'.', label = 'a')
leg = plt.legend();
plt.subplot(3, 1, 2)
plt.plot(b_corrected,'.', label = 'b')
leg = plt.legend();
plt.subplot(3, 1, 3)
plt.plot(c_corrected,'.', label = 'c')
leg = plt.legend();
plt.title('Corrected laser on values ')

 
result_list, time_list, first_point, last_point, first_point_control = splitting_data(data_matrix[1])      
figs={}
axs={}  
a = []
b = []
c = [] 
for jj in range(30): 
    try:
        regression_result = regression(result_list[jj],time_list[jj])
    except (RuntimeError): 
        pass
    extract = regression_result[6] ; extract_2 = extract[0] ; extract_3= extract_2[0] ; extract_4 = regression_result[7]; extract_5= extract_4[0]; extract_6 = regression_result[7]; extract_7 = extract_6[0]      
    figs[jj] = plt.figure()
    # axs[jj]=figs[jj].add_subplot(221)
    if jj == 1:
        cc = 'b'
    plt.plot(time_list[jj], result_list[jj], label = 'data set: '+ str(1) + 'sample number ' + str(jj))
    leg = plt.legend();
    # axs[jj]=figs[jj].add_subplot(222)
    plt.plot(regression_result[0], regression_result[2],label='score = '+ str(round(regression_result[5],2)) + ' a = ' + str(round(extract_3, 2)) + ' b = ' + str(round(extract_5)) + 'in ax + b')
    leg = plt.legend();
    # axs[jj]=figs[jj].add_subplot(223)
    plt.plot(regression_result[0], regression_result[3])
    leg = plt.legend();
    # axs[jj]=figs[jj].add_subplot(224)
    plt.plot(regression_result[0], regression_result[4], label = 'a = ' + str(round(extract_7,2)) +' b = ' + str(round(regression_result[8],2))+ ' c = ' + str(round(regression_result[9],2)) + ' in a*exp(-b*x) + c')
    leg = plt.legend();
    a.append(round(extract_7,2))
    b.append(round(regression_result[8],2))
    c.append(round(regression_result[9],2))




fig40 = plt.figure()
plt.subplot(3, 1, 1)
plt.plot(a,'.', label = 'a')
leg = plt.legend();
plt.subplot(3, 1, 2)
plt.plot(b,'.', label = 'b')
leg = plt.legend();
plt.subplot(3, 1, 3)
plt.plot(c,'.', label = 'c')
leg = plt.legend();
plt.title('Uncorrected all values')

fig41 = plt.figure()
plt.subplot(3, 1, 1)
plt.plot(get_high_values(a),'.', label = 'a')
leg = plt.legend();
plt.subplot(3, 1, 2)
plt.plot(get_high_values(b),'.', label = 'b')
leg = plt.legend();
plt.subplot(3, 1, 3)
plt.plot(get_high_values(c),'.' , label = 'c')
leg = plt.legend();
plt.title('Uncorrected only laser on values')








