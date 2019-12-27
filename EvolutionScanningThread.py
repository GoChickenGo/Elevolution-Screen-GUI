# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 15:10:53 2019

@author: xinmeng
"""
from PyQt5.QtCore import pyqtSignal, QThread
import numpy as np
from stage import LudlStage
import time
from PIL import Image
from matplotlib import pyplot as plt
import os
from datetime import datetime
from generalDaqerThread import (execute_analog_readin_optional_digital_thread, execute_tread_singlesample_analog,
                                execute_tread_singlesample_digital, execute_analog_and_readin_digital_optional_camtrig_thread, DaqProgressBar)
from trymageAnalysis_v3 import ImageAnalysis

class ScanningExecutionThread(QThread):
    
    PMTimageDictMeasurement = pyqtSignal(np.ndarray) #The signal for the measurement, we can connect to this signal
    
    def __init__(self, RoundQueueDict, RoundCoordsDict, GeneralSettingDict, *args, **kwargs):        
        super().__init__(*args, **kwargs)
        self.RoundQueueDict = RoundQueueDict
        self.RoundCoordsDict = RoundCoordsDict
        self.GeneralSettingDict = GeneralSettingDict
        
        self.ludlStage = LudlStage("COM6")
        
        self.PMTimageDict = {}
        for i in range(int(len(self.RoundQueueDict)/2)): # initial the nested PMTimageDict dictionary.
            self.PMTimageDict['RoundPackage_{}'.format(i+1)] = {}
        self.clock_source = 'Dev1 as clock source' # Should be set by GUI.
        
        self.scansavedirectory = self.GeneralSettingDict['savedirectory']
        
    def run(self):

        for EachRound in range(int(len(self.RoundQueueDict)/2)): # EachRound is the round sequence number starting from 0, while the actual number used in dictionary is 1.
            print ('----------------------------------------------------------------------------')            
            print('Below is Round {}.'.format(EachRound+1)) # EachRound+1 is the corresponding round number when setting the dictionary starting from round 1.
            
            CoordOrder = 0            
            CellPropertiesDict = {}
#            All_cell_properties = []
            cp_end_index = -1
            IndexLookUpCellPropertiesDict = {} #look up dictionary for each cell properties
            
            CoordsNum = int(len(self.RoundCoordsDict['CoordsPackage_{}'.format(EachRound+1)])/2)
            for EachCoord in range(CoordsNum):
                print ('Current index: {}.'.format(self.RoundCoordsDict['CoordsPackage_{}'.format(EachRound+1)][EachCoord*2:EachCoord*2+2]))
                
                #stage movement
                RowIndex = int(self.RoundCoordsDict['CoordsPackage_{}'.format(EachRound+1)][EachCoord*2:EachCoord*2+2][0])
                ColumnIndex = int(self.RoundCoordsDict['CoordsPackage_{}'.format(EachRound+1)][EachCoord*2:EachCoord*2+2][1])
                self.ludlStage.moveAbs(RowIndex,ColumnIndex)
                time.sleep(1)
                
                #Execute waveform packages
                self.WaveforpackageNum = int(len(self.RoundQueueDict['RoundPackage_{}'.format(EachRound+1)]))
                #Execute each individual waveform package
                for EachWaveform in range(self.WaveforpackageNum):
                    WaveformPackageToBeExecute = self.RoundQueueDict['RoundPackage_{}'.format(EachRound+1)]['WavformPackage_{}'.format(EachWaveform+1)]
                    WaveformPackageGalvoInfor = self.RoundQueueDict['GalvoInforPackage_{}'.format(EachRound+1)]['GalvoInfor_{}'.format(EachWaveform+1)]  
                    self.readinchan = WaveformPackageToBeExecute[3]
                    self.RoundWaveformIndex = [EachRound+1, EachWaveform+1] # first is current round number, second is current waveform package number.
                    self.CurrentPosIndex = [RowIndex, ColumnIndex]
                    
                    if WaveformPackageGalvoInfor != 'NoGalvo': # Unpack the information of galvo scanning.
                        self.readinchan = WaveformPackageGalvoInfor[0]
                        self.repeatnum = WaveformPackageGalvoInfor[1]
                        self.PMT_data_index_array = WaveformPackageGalvoInfor[2]
                        self.averagenum = WaveformPackageGalvoInfor[3]
                        self.lenSample_1 = WaveformPackageGalvoInfor[4]
                        self.ScanArrayXnum = WaveformPackageGalvoInfor[5]

                    if self.clock_source == 'Dev1 as clock source':
                        self.adcollector = execute_analog_readin_optional_digital_thread()
                        self.adcollector.set_waves(WaveformPackageToBeExecute[0], WaveformPackageToBeExecute[1], WaveformPackageToBeExecute[2], WaveformPackageToBeExecute[3])
                        self.adcollector.collected_data.connect(self.ProcessData)
                        self.adcollector.run()
                        #self.ai_dev_scaling_coeff = self.adcollector.get_ai_dev_scaling_coeff()
                    elif self.clock_source == 'Cam as clock source' :
                        self.adcollector = execute_analog_and_readin_digital_optional_camtrig_thread()
                        self.adcollector.set_waves(WaveformPackageToBeExecute[0], WaveformPackageToBeExecute[1], WaveformPackageToBeExecute[2], WaveformPackageToBeExecute[3])
                        self.adcollector.collected_data.connect(self.ProcessData)
                        self.adcollector.run()
                
                time.sleep(1) # Here to make sure self.ProcessData is run before Image anaylsis part.

                # Image anaylsis part.
                if  EachRound+1 == self.GeneralSettingDict['AftRoundNum']: # When it's the round for after Kcl assay image acquisition.
                    print('Image analysis start.')                    
                    #------------------------------------------------------------------ Image processing ----------------------------------------------------------------------
                    #Pull the Bef and Aft image from the dictionary
                    ImageBef = self.PMTimageDict['RoundPackage_{}'.format(self.GeneralSettingDict['BefRoundNum'])]['row_{}_column_{}'.format(RowIndex, ColumnIndex)]
                    ImageAft = self.PMTimageDict['RoundPackage_{}'.format(self.GeneralSettingDict['AftRoundNum'])]['row_{}_column_{}'.format(RowIndex, ColumnIndex)]            
                    print(ImageAft.shape)
                    
                    try:
                        ImageAnalysisInstance = ImageAnalysis(ImageBef, ImageAft)
                        MaskedImageBef, MaskedImageAft, MaskBef, MaskAft, thres = ImageAnalysisInstance.applyMask(self.GeneralSettingDict['openingfactor'], 
                                                                                                                  self.GeneralSettingDict['closingfactor'], 
                                                                                                                  self.GeneralSettingDict['binary_adaptive_block_size']) #v1 = Thresholded whole image
    
                        CellPropertiesArray, coutourmask, coutourimg, intensityimage_intensity, contour_change_ratio= ImageAnalysisInstance.get_intensity_properties(self.GeneralSettingDict['smallestsize'], 
                                                                                                                                                    MaskBef, thres, MaskedImageBef, MaskedImageAft, 
                                                                                                                                                    RowIndex, ColumnIndex, 
                                                                                                                                                    self.GeneralSettingDict['self_findcontour_thres'],
                                                                                                                                                    self.GeneralSettingDict['contour_dilation'],
                                                                                                                                                    self.GeneralSettingDict['cellopeningfactor'], 
                                                                                                                                                    self.GeneralSettingDict['cellclosingfactor'])
                        ImageAnalysisInstance.showlabel(self.smallestsize, MaskBef, MaskedImageBef, thres, RowIndex, ColumnIndex, CellPropertiesArray)
    
                        print (CellPropertiesArray)
                        CellPropertiesDict[CoordOrder] = CellPropertiesArray
                        if CoordOrder == 0:
                            AllCellPropertiesDict = CellPropertiesDict[0]
                        if CoordOrder != 0:
                            AllCellPropertiesDict = np.append(AllCellPropertiesDict, CellPropertiesDict[CoordOrder], axis=0)
                        
                        cp_end_index = cp_end_index + len(CellPropertiesArray)
                        cp_start_index = cp_end_index - len(CellPropertiesArray) +1
                        IndexLookUpCellPropertiesDict['row_{}_column_{}'.format(RowIndex, ColumnIndex)] = [cp_start_index, cp_end_index] #get the location of individual cp index & put in dictionary， as they are stored in sequence.
                    except:
                        print('Image analysis failed.')
                    time.sleep(0.3)
                   
                    CoordOrder = CoordOrder+1
                    
    def ProcessData(self, data_waveformreceived):    

        self.adcollector.save_as_binary(self.scansavedirectory)
        
        self.channel_number = len(data_waveformreceived)
        if self.channel_number == 1:            
            if 'Vp' in self.readinchan:
                pass
            elif 'Ip' in self.readinchan:
                pass
            elif 'PMT' in self.readinchan:  # repeatnum, PMT_data_index_array, averagenum, ScanArrayXnum
                self.data_collected_0 = data_waveformreceived[0]*-1
                for imageSequence in range(self.repeatnum):
                    self.PMT_image_reconstructed_array = self.data_collected_0[np.where(self.PMT_data_index_array == imageSequence+1)]
                    Dataholder_average = np.mean(self.PMT_image_reconstructed_array.reshape(self.averagenum, -1), axis=0)
                    Value_yPixels = int(self.lenSample_1/self.ScanArrayXnum)
                    self.PMT_image_reconstructed = np.reshape(Dataholder_average, (Value_yPixels, self.ScanArrayXnum))
                    
                    self.PMT_image_reconstructed = self.PMT_image_reconstructed[:, 15:515] # By default with 5v scanning voltage it's how image should be cropped.
                    
                    # Stack the arrays into a 3d array
                    if imageSequence == 0:
                        self.PMT_image_reconstructed_stack = self.PMT_image_reconstructed
                    else:
                        self.PMT_image_reconstructed_stack = np.concatenate((self.PMT_image_reconstructed_stack, self.PMT_image_reconstructed), axis=0)
                    
                    Localimg = Image.fromarray(self.PMT_image_reconstructed) #generate an image object
                    Localimg.save(os.path.join(self.scansavedirectory, datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'_PMT_'+str(imageSequence)+'.tif')) #save as tif
                    
                    plt.figure()
                    plt.imshow(self.PMT_image_reconstructed, cmap = plt.cm.gray)
                    plt.show()
                
        elif self.channel_number == 2: 
            if 'PMT' not in self.readinchan:
                pass
            elif 'PMT' in self.readinchan:
                self.data_collected_0 = data_waveformreceived[0]*-1
                for imageSequence in range(self.repeatnum):
                    self.PMT_image_reconstructed_array = self.data_collected_0[np.where(self.PMT_data_index_array == imageSequence+1)]
                    Dataholder_average = np.mean(self.PMT_image_reconstructed_array.reshape(self.averagenum, -1), axis=0)
                    Value_yPixels = int(self.lenSample_1/self.ScanArrayXnum)
                    self.PMT_image_reconstructed = np.reshape(Dataholder_average, (Value_yPixels, self.ScanArrayXnum))
                    
                    self.PMT_image_reconstructed = self.PMT_image_reconstructed[:, 15:515]
                    
                    # Stack the arrays into a 3d array
                    if imageSequence == 0:
                        self.PMT_image_reconstructed_stack = self.PMT_image_reconstructed
                    else:
                        self.PMT_image_reconstructed_stack = np.concatenate((self.PMT_image_reconstructed_stack, self.PMT_image_reconstructed), axis=0)
                    
                    Localimg = Image.fromarray(self.PMT_image_reconstructed) #generate an image object
                    Localimg.save(os.path.join(self.scansavedirectory, datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'_PMT_'+str(imageSequence)+'.tif')) #save as tif
                    
                    plt.figure()
                    plt.imshow(self.PMT_image_reconstructed, cmap = plt.cm.gray)
                    plt.show()
                  
        self.PMTimageDict['RoundPackage_{}'.format(self.RoundWaveformIndex[0])]['row_{}_column_{}'.format(self.CurrentPosIndex[0], self.CurrentPosIndex[1])] = self.PMT_image_reconstructed_stack
        print('ProcessData executed.')