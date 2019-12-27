# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 16:21:41 2019

Program for testing the camera. 

@author: douwe
"""

import sys
import numpy as np
import csv
import os
import time
'''
IMPORTANT

1. You must be running python 3.6.x for this to work! If you are using anaconda
you can use the conda install function to downgrade python. Otherwise do so
manually. 

2. Follow these instructions to get micro-manager to work with python 3.6;
 https://github.com/zfphil/micro-manager-python3 
 
3. Make sure you download a nightly build of micro-manager from between 
2016-06-09 and 2017-11-07!

The following lines of code will append the micro-manager to the python path so 
you can use all of its functionality.
'''

sys.path.append('C:\Program Files\Micro-Manager-2.0beta')
prev_dir = os.getcwd()
os.chdir('C:\Program Files\Micro-Manager-2.0beta') # MUST change to micro-manager directory for method to work

import MMCorePy

mmc = MMCorePy.CMMCore()
os.chdir(prev_dir)

# Success!
print("Micro-manager was loaded sucessfully!")  
from camera_backend_lab_5 import Camera



if __name__ == "__main__": 
    mmc.reset()
#    DEVICE = ['Camera', 'DemoCamera', 'DCam']
    DEVICE = ['Camera', 'HamamatsuHam', 'HamamatsuHam_DCAM']
    cam = Camera(DEVICE)
    cam.mmc.setCircularBufferMemoryFootprint(1500)
    
    cam.clear_roi()
    tot_width = cam.mmc.getImageWidth()
    tot_height = cam.mmc.getImageHeight()
    
#    cam.mmc.setExposure(1) #setting the exposure to the minimum ensures the max framerate
    
    def full_res_test():  
        cam.clear_roi() #ensure we are using the entire CMOS
        
        steps = 30
        start = 0.5
        stop = 12
        rectime = np.linspace(start,stop,steps)
        
        results = []
        
        for n in range(0,steps):
            cam.start_recording()
            time.sleep(rectime[n])
            cam.stop_recording()   
            buffer_images = cam.mmc.getRemainingImageCount()
            print(str(buffer_images) + "images left in buffer")
            
            while cam.mmc.getRemainingImageCount() > 0:
                time.sleep(0.1)
            
            results.append([cam.frames,rectime[n],buffer_images,cam.mmc.getProperty('Camera','ReadoutTime')])
            print("filmed for " + str(rectime[n]) + " seconds")
            print(str(cam.frames) + "frames")
            time.sleep(4) #Making sure the tiffwriter is done!           
            os.remove(cam.video_name) #removing the abundance of files while testing.
            
        with open('full_frame_test.csv', 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(results)
            
            
            
            
    def test_1000x1000():  
        set_roi_center(1000,1000)
        
        steps = 30
        start = 0.5
        stop = 12
        rectime = np.linspace(start,stop,steps)
        
        results = []
        
        for n in range(0,steps):
            cam.start_recording()
            time.sleep(rectime[n])
            cam.stop_recording()        
            buffer_images = cam.mmc.getRemainingImageCount()
            print(str(buffer_images) + "images left in buffer")
            while cam.mmc.getRemainingImageCount() > 0:
                time.sleep(0.1)
#                print("sleeping")
            
            results.append([cam.frames,rectime[n],buffer_images,cam.mmc.getProperty('Camera','ReadoutTime')])
            print("filmed for " + str(rectime[n]) + " seconds")
            print(str(cam.frames) + "frames")
            
            time.sleep(4) #Making sure the tiffwriter is done!           
            os.remove(cam.video_name) #removing the abundance of files while testing.
            
        with open('1000x1000_framerate_test2.csv', 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(results)
                   

    def test_varying_roi():  
        steps = 30
        start = tot_width
        stop = 20
        lenght = np.linspace(start,stop,steps)
        cam.set_buf_size(5000)
        results = []
        cam.mmc.setExposure(1)
        
        for n in range(0,steps):
            set_roi_center(lenght[n],lenght[n])
            
            cam.start_recording()
            time.sleep(5)
            cam.stop_recording()        
            buffer_images = cam.mmc.getRemainingImageCount()
            print(str(buffer_images) + " images left in buffer")
#            while cam.mmc.getRemainingImageCount() > 0:
#                time.sleep(0.5)
#                print("sleeping")
            
            results.append([buffer_images, cam.rec_time,lenght[n],cam.mmc.getProperty('Camera','ReadoutTime'),cam.mmc.getExposure()])
            print("filmed for " + str(cam.rec_time) + " seconds")
#            print(str(cam.frames) + " frames.")
            
#            os.remove(cam.video_name) #removing the abundance of files while testing.
            time.sleep(2)
        with open('varying_roi_test_nowrite.csv', 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(results)
            
    def test_varying_roi_framerate():  
        
        steps = 15
        start = 240
        stop = 20
        lenght = np.linspace(start,stop,steps)
        
        results = []
        cam.set_buf_size(5000)
        time.sleep(1)
        cam.mode = "framerate_tester"
        cam.tot_ims = 5000
         
        for n in range(0,steps):
            set_roi_center(lenght[n],lenght[n])
            time.sleep(1)
            cam.set_exposure_time(0.01)
            time.sleep(1)
            print(lenght[n])
            cam.start()       
            while not cam.done:
                print("sleeping")
                time.sleep(0.5)                  
            cam.done = False      
            results.append([lenght[n],cam.frames,cam.rec_time])

        with open('varying_roi_test_framerate_smaller.csv', 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(results)
                    
            
    def buffer_overflowed():  
        set_roi_center(1000,1000)
        
        steps = 10
        start = 1000
        stop = 50
        lenght = np.linspace(start,stop,steps)
        
        results = []
        
        for n in range(0,steps):
            overflowed = False
            
            set_roi_center(lenght[n],lenght[n])    
            cam.start_recording()
            start_time = time.time()
            while time.time()-start_time < 10:
                if cam.mmc.isBufferOverflowed():
                    overflowed = True
                    overflowed_time = time.time()-start_time
                    break
            cam.stop_recording()
            
            buffersize = cam.mmc.getImageBufferSize()
            buffer_images = cam.mmc.getRemainingImageCount()
            
            print("filmed with " + str(lenght[n]) + " width/heigth")
            if overflowed == True:
                print("buffer overflowed after "  + str(overflowed_time) + " seconds")
            else:
                print("not overflowed after 10 seconds!")
            
            results.append([lenght[n],buffer_images,buffersize,overflowed_time])
            
            while cam.mmc.getRemainingImageCount() > 0:
                time.sleep(0.1)            
                
            time.sleep(4) #Making sure the tiffwriter is done!           
#            os.remove(cam.video_name) #removing the abundance of files while testing.
            
        with open('buffer_overflowed_test_small_bigtiff.csv', 'w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(results)
            
            
    def set_roi_center(x_size, y_size):
        x_center = int(0.5*tot_width-0.5*x_size)
        y_center = int(0.5*tot_height-0.5*y_size)
        cam.set_cam_roi(x_center,y_center,int(x_size),int(y_size))

#    full_res_test()
#    test_1000x1000()
#    buffer_overflowed()
#    print(cam.mmc.getExposure())
#    set_roi_center(8,8)
#    cam.print_properties()
#    print(cam.get_framerate())
    test_varying_roi_framerate()
        
    cam.close_camera()