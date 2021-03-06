# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 15:10:53 2019

@author: xinmeng
-----------------------------------------------------------Threading class for evolution screening--------------------------------------------------------------------------------
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
import numpy.lib.recfunctions as rfn
from focuser import PIMotor
import math
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class ScanningExecutionThread(QThread):
    
    ScanningResult = pyqtSignal(np.ndarray, np.ndarray, object, object) #The signal for the measurement, we can connect to this signal
    
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
        
#        if len(self.GeneralSettingDict['FocusCorrectionMatrixDict']) > 0:# if focus correction matrix was generated.
        print('----------------------Starting to connect the Objective motor-------------------------')
        self.pi_device_instance = PIMotor()
        print('Objective motor connected.')
        
        self.ObjCurrentPos = self.pi_device_instance.pidevice.qPOS(self.pi_device_instance.pidevice.axes)
        
        for EachRound in range(int(len(self.RoundQueueDict)/2)): # EachRound is the round sequence number starting from 0, while the actual number used in dictionary is 1.
            print ('----------------------------------------------------------------------------')            
            print('Below is Round {}.'.format(EachRound+1)) # EachRound+1 is the corresponding round number when setting the dictionary starting from round 1.
            
            #--------------------------------------------------------Unpack the settings for each round---------------------------------------------------------------------------
            CoordOrder = 0      # Counter for n th coordinates, for appending cell properties array.      
            CellPropertiesDict = {}
#            All_cell_properties = []
            cp_end_index = -1
            self.IndexLookUpCellPropertiesDict = {} #look up dictionary for each cell properties
            #Unpack the focus stack information.
            ZStackinfor = self.GeneralSettingDict['FocusStackInfoDict']['RoundPackage_{}'.format(EachRound+1)]
            self.ZStackNum = int(ZStackinfor[ZStackinfor.index('Focus')+5])
            self.ZStackStep = float(ZStackinfor[ZStackinfor.index('Being')+5:len(ZStackinfor)])
            
            CoordsNum = int(len(self.RoundCoordsDict['CoordsPackage_{}'.format(EachRound+1)])/2) #Each pos has 2 coords
            
            for EachCoord in range(CoordsNum):
                print ('Round {}. Current index: {}.'.format(EachRound+1, self.RoundCoordsDict['CoordsPackage_{}'.format(EachRound+1)][EachCoord*2:EachCoord*2+2]))
                
                #-------------------------------------------Stage movement-----------------------------------------------------
                RowIndex = int(self.RoundCoordsDict['CoordsPackage_{}'.format(EachRound+1)][EachCoord*2:EachCoord*2+2][0])
                ColumnIndex = int(self.RoundCoordsDict['CoordsPackage_{}'.format(EachRound+1)][EachCoord*2:EachCoord*2+2][1])
                self.ludlStage.moveAbs(RowIndex,ColumnIndex)
                time.sleep(1)
                
                #-------------------------------------------Adjust focus position----------------------------------------
                if len(self.GeneralSettingDict['FocusCorrectionMatrixDict']) > 0:
                    FocusPosArray = self.GeneralSettingDict['FocusCorrectionMatrixDict']['RoundPackage_{}'.format(EachRound+1)]
#                    print(FocusPosArray)
                    FocusPos = FocusPosArray[EachCoord]
                    print('Target focus pos: '.format(FocusPos))
                    
                    pos = PIMotor.move(self.pi_device_instance.pidevice, FocusPos)
                    self.ObjCurrentPos = self.pi_device_instance.pidevice.qPOS(self.pi_device_instance.pidevice.axes)
                    print("Current position: {:.4f}".format(self.ObjCurrentPos['1']))
                    
                    time.sleep(0.5)
                    
                #-------------------------------------------Get the z stack objective positions ready----------------------------------------------------------------------------
                ZStacklinspaceStart = self.ObjCurrentPos['1'] - math.floor(self.ZStackNum/2)*self.ZStackStep
                ZStacklinspaceEnd = self.ObjCurrentPos['1'] + (self.ZStackNum - math.floor(self.ZStackNum/2)-1)*self.ZStackStep
                ZStackPosList = np.linspace(ZStacklinspaceStart, ZStacklinspaceEnd, num = self.ZStackNum)
                
                #-------------------------------------------Execute waveform packages------------------------------------
                self.WaveforpackageNum = int(len(self.RoundQueueDict['RoundPackage_{}'.format(EachRound+1)]))
                #Execute each individual waveform package
                print('*******************************************Round {}. Current index: {}.**************************************************'.format(EachRound+1, self.RoundCoordsDict['CoordsPackage_{}'.format(EachRound+1)][EachCoord*2:EachCoord*2+2]))
                for EachZStackPos in range(self.ZStackNum): # Move to Z stack focus 
                    
                    if self.ZStackNum > 1:
                        self.ZStackOrder = EachZStackPos +1 # Here the first one is 1, not starting from 0.
                        FocusPos = ZStackPosList[EachZStackPos]
                        print('Target focus pos: {}'.format(FocusPos))

                        pos = PIMotor.move(self.pi_device_instance.pidevice, FocusPos)
                        self.ObjCurrentPosInStack = self.pi_device_instance.pidevice.qPOS(self.pi_device_instance.pidevice.axes)
                        print("Current position: {:.4f}".format(self.ObjCurrentPosInStack['1']))
                        
                        time.sleep(0.3)
                    else:
                        self.ZStackOrder = 1
                    
                    for EachWaveform in range(self.WaveforpackageNum):
                        WaveformPackageToBeExecute = self.RoundQueueDict['RoundPackage_{}'.format(EachRound+1)]['WaveformPackage_{}'.format(EachWaveform+1)]
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
                            self.adcollector.set_waves(WaveformPackageToBeExecute[0], WaveformPackageToBeExecute[1], WaveformPackageToBeExecute[2], WaveformPackageToBeExecute[3]) #[0] = sampling rate, [1] = analogcontainer_array, [2] = digitalcontainer_array, [3] = readinchan
                            self.adcollector.collected_data.connect(self.ProcessData)
                            self.adcollector.run()
                            #self.ai_dev_scaling_coeff = self.adcollector.get_ai_dev_scaling_coeff()
                        elif self.clock_source == 'Cam as clock source' :
                            self.adcollector = execute_analog_and_readin_digital_optional_camtrig_thread()
                            self.adcollector.set_waves(WaveformPackageToBeExecute[0], WaveformPackageToBeExecute[1], WaveformPackageToBeExecute[2], WaveformPackageToBeExecute[3])
                            self.adcollector.collected_data.connect(self.ProcessData)
                            self.adcollector.run()
                    time.sleep(0.5) # Wait for receiving data to be done.
                time.sleep(0.3)
                print('*************************************************************************************************************************')
                
                # Image anaylsis part.
                if  EachRound+1 == self.GeneralSettingDict['AftRoundNum']: # When it's the round for after Kcl assay image acquisition.
                    
                    time.sleep(1) # Here to make sure self.ProcessData is run before Image anaylsis part. self.ProcessData and this part are started at the same time.                 
                    print('Image analysis start.')                    
                    #------------------------------------------------------------------ Image processing ----------------------------------------------------------------------
                    #Pull the Bef and Aft image from the dictionary
                    ImageBef = self.PMTimageDict['RoundPackage_{}'.format(self.GeneralSettingDict['BefRoundNum'])]['row_{}_column_{}_stack1'.format(RowIndex, ColumnIndex)]
                    ImageAft = self.PMTimageDict['RoundPackage_{}'.format(self.GeneralSettingDict['AftRoundNum'])]['row_{}_column_{}_stack1'.format(RowIndex, ColumnIndex)]            
                    print(ImageAft.shape) # NOT ready for 3d stack
                    
                    try:
                        self.ImageAnalysisInstance = ImageAnalysis(ImageBef, ImageAft)
                        MaskedImageBef, MaskedImageAft, MaskBef, MaskAft, thres = self.ImageAnalysisInstance.applyMask(self.GeneralSettingDict['openingfactor'], 
                                                                                                                  self.GeneralSettingDict['closingfactor'], 
                                                                                                                  self.GeneralSettingDict['binary_adaptive_block_size']) #v1 = Thresholded whole image
    
                        CellPropertiesArray, coutourmask, coutourimg, intensityimage_intensity, contour_change_ratio = self.ImageAnalysisInstance.get_intensity_properties(self.GeneralSettingDict['smallestsize'], 
                                                                                                                                                    MaskBef, thres, MaskedImageBef, MaskedImageAft, 
                                                                                                                                                    RowIndex, ColumnIndex, 
                                                                                                                                                    self.GeneralSettingDict['self_findcontour_thres'],
                                                                                                                                                    self.GeneralSettingDict['contour_dilation'],
                                                                                                                                                    self.GeneralSettingDict['cellopeningfactor'], 
                                                                                                                                                    self.GeneralSettingDict['cellclosingfactor'])
                        self.ImageAnalysisInstance.showlabel(self.GeneralSettingDict['smallestsize'], MaskBef, MaskedImageBef, thres, RowIndex, ColumnIndex, CellPropertiesArray)
    
                        print (CellPropertiesArray)
                        CellPropertiesDict[CoordOrder] = CellPropertiesArray
                        if CoordOrder == 0:
                            self.AllCellPropertiesDict = CellPropertiesDict[0]
                        if CoordOrder != 0:
                            self.AllCellPropertiesDict = np.append(self.AllCellPropertiesDict, CellPropertiesDict[CoordOrder], axis=0)
                        
                        cp_end_index = cp_end_index + len(CellPropertiesArray)
                        cp_start_index = cp_end_index - len(CellPropertiesArray) +1
                        self.IndexLookUpCellPropertiesDict['row_{}_column_{}'.format(RowIndex, ColumnIndex)] = [cp_start_index, cp_end_index]
                        # As cell properties are stored in sequence, the lookup dictionary provides information of to which stage coordinates the cp data in cell properties array belong.
                    except:
                        print('Image analysis failed.')
                    time.sleep(0.3)
                   
                    CoordOrder = CoordOrder+1
            
            # Sort the cell properties array
            if  EachRound+1 == self.GeneralSettingDict['AftRoundNum']: # When it's the round for after Kcl assay image acquisition.
                self.RankedAllCellProperties, self.FinalMergedCoords = self.SortingPropertiesArray(self.AllCellPropertiesDict)
        
        try:
            self.ScanningResult.emit(self.RankedAllCellProperties, self.FinalMergedCoords, self.IndexLookUpCellPropertiesDict, self.PMTimageDict)
        except:
            print('Failed to generate cell properties ranking.')
        
        try:
            PIMotor.CloseMotorConnection(self.pi_device_instance.pidevice)
            print('Objective motor disconnected.')
        except:
            pass
    #--------------------------------------------------------------Reconstruct and save images from 1D recorded array.--------------------------------------------------------------------------------       
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
                self.data_collected_0 = self.data_collected_0[0:len(self.data_collected_0)-1]
                print(len(self.data_collected_0))                
                for imageSequence in range(self.repeatnum):
                    
                    try:
                        self.PMT_image_reconstructed_array = self.data_collected_0[np.where(self.PMT_data_index_array == imageSequence+1)]
#                        if imageSequence == int(self.repeatnum)-1:
#                            self.PMT_image_reconstructed_array = self.PMT_image_reconstructed_array[0:len(self.PMT_image_reconstructed_array)-1] # Extra one sample at the end.
#                        print(self.PMT_image_reconstructed_array.shape)
                        Dataholder_average = np.mean(self.PMT_image_reconstructed_array.reshape(self.averagenum, -1), axis=0)
#                        print(Dataholder_average.shape)
                        Value_yPixels = int(self.lenSample_1/self.ScanArrayXnum)
                        self.PMT_image_reconstructed = np.reshape(Dataholder_average, (Value_yPixels, self.ScanArrayXnum))
                        
                        self.PMT_image_reconstructed = self.PMT_image_reconstructed[:, 50:550] # Crop size based on: M:\tnw\ist\do\projects\Neurophotonics\Brinkslab\Data\Xin\2019-12-30 2p beads area test 4um
                        
                        # Stack the arrays into a 3d array
                        if imageSequence == 0:
                            self.PMT_image_reconstructed_stack = self.PMT_image_reconstructed
                        else:
                            self.PMT_image_reconstructed_stack = np.concatenate((self.PMT_image_reconstructed_stack, self.PMT_image_reconstructed), axis=0)
                        
                        Localimg = Image.fromarray(self.PMT_image_reconstructed) #generate an image object
                        Localimg.save(os.path.join(self.scansavedirectory, 'Round'+str(self.RoundWaveformIndex[0])+'R'+str(self.CurrentPosIndex[0])+'C'+str(self.CurrentPosIndex[1])+'_PMT_'+str(imageSequence)+'Zpos'+str(self.ZStackOrder)+'.tif')) #save as tif
                        
                        plt.figure()
                        plt.imshow(self.PMT_image_reconstructed, cmap = plt.cm.gray)
                        plt.show()
                    except:
                        print('No.{} image failed to generate.'.format(imageSequence))
                    
        elif self.channel_number == 2: 
            if 'PMT' not in self.readinchan:
                pass
            elif 'PMT' in self.readinchan:

                self.data_collected_0 = data_waveformreceived[0]*-1
                self.data_collected_0 = self.data_collected_0[0:len(self.data_collected_0)-1]
                print(len(self.data_collected_0)) 
                for imageSequence in range(self.repeatnum):
                    try:
                        self.PMT_image_reconstructed_array = self.data_collected_0[np.where(self.PMT_data_index_array == imageSequence+1)]
                        if imageSequence == int(self.repeatnum)-1:
                            self.PMT_image_reconstructed_array = self.PMT_image_reconstructed_array[0:len(self.PMT_image_reconstructed_array)-1] # Extra one sample at the end.

                        Dataholder_average = np.mean(self.PMT_image_reconstructed_array.reshape(self.averagenum, -1), axis=0)
                        Value_yPixels = int(self.lenSample_1/self.ScanArrayXnum)
                        self.PMT_image_reconstructed = np.reshape(Dataholder_average, (Value_yPixels, self.ScanArrayXnum))
                        
                        self.PMT_image_reconstructed = self.PMT_image_reconstructed[:, 50:550]
                        
                        # Stack the arrays into a 3d array
                        if imageSequence == 0:
                            self.PMT_image_reconstructed_stack = self.PMT_image_reconstructed
                        else:
                            self.PMT_image_reconstructed_stack = np.concatenate((self.PMT_image_reconstructed_stack, self.PMT_image_reconstructed), axis=0)
                        
                        Localimg = Image.fromarray(self.PMT_image_reconstructed) #generate an image object
                        Localimg.save(os.path.join(self.scansavedirectory, 'Round'+str(self.RoundWaveformIndex[0])+'R'+str(self.CurrentPosIndex[0])+'C'+str(self.CurrentPosIndex[1])+'_PMT_'+str(imageSequence)+'Zpos'+str(self.ZStackOrder)+'.tif')) #save as tif
                        
                        plt.figure()
                        plt.imshow(self.PMT_image_reconstructed, cmap = plt.cm.gray)
                        plt.show()
                    except:
                        print('No.{} image failed to generate.'.format(imageSequence))

                  
        self.PMTimageDict['RoundPackage_{}'.format(self.RoundWaveformIndex[0])]['row_{}_column_{}_stack{}'.format(self.CurrentPosIndex[0], self.CurrentPosIndex[1], self.ZStackOrder)] = self.PMT_image_reconstructed_stack
        print('ProcessData executed.')
        
    #-----------------------------------------------------------------Sorting the cells------------------------------------------------------------------------------------------------------------
    def SortingPropertiesArray(self, All_cell_properties):  
        #------------------------------------------CAN use 'import numpy.lib.recfunctions as rfn' to append field--------------
        original_cp = rfn.append_fields(All_cell_properties, 'Original_sequence', list(range(0, len(All_cell_properties))), usemask=False)
        #print('*********************sorted************************')        
        sortedcp = self.ImageAnalysisInstance.sort_using_weight(original_cp, 'Mean intensity in contour','Contour soma ratio','Change', self.GeneralSettingDict['Mean intensity in contour weight'], self.GeneralSettingDict['Contour soma ratio weight'], self.GeneralSettingDict['Change weight'])
        #******************************Add ranking to it*********************************
        ranked_cp = rfn.append_fields(sortedcp, 'Ranking', list(range(0, len(All_cell_properties))), usemask=False)
        #print('***********************Original sequence with ranking**************************')        
        withranking_cp = np.sort(ranked_cp, order='Original_sequence')
       
        # All the cells are ranked, now we find the desired group and their position indexs, call the images and show labels of
        # these who meet the requirements, omitting bad ones.
        
        #get the index
        cell_properties_selected_hits = ranked_cp[0:self.GeneralSettingDict['selectnum']]
        cell_properties_selected_hits_index_sorted = np.sort(cell_properties_selected_hits, order=['Row index', 'Column index'])
        index_samples = np.vstack((cell_properties_selected_hits_index_sorted['Row index'],cell_properties_selected_hits_index_sorted['Column index']))
        
        merged_index_samples = index_samples[:,0] # Merge coordinates which are the same.

        #consider these after 1st one
        for i in range(1, len(index_samples[0])):
            #print(index_samples[:,i][0] - index_samples[:,i-1][0])    
            if index_samples[:,i][0] != index_samples[:,i-1][0] or index_samples[:,i][1] != index_samples[:,i-1][1]: 
                merged_index_samples = np.append(merged_index_samples, index_samples[:,i], axis=0)
        merged_index_samples = merged_index_samples.reshape(-1, 2) # 1st column=i, 2nd column=j
        
        return withranking_cp, merged_index_samples
    
#    def GetDataForShowingRank(self):
#        return self.RankedAllCellProperties, self.FinalMergedCoords, self.IndexLookUpCellPropertiesDict, self.PMTimageDict
    
class ShowTopCellsThread(QThread):
    
    PMTimageDictMeasurement = pyqtSignal(object) #The signal for the measurement, we can connect to this signal
    
    def __init__(self, GeneralSettingDict, RankedAllCellProperties, FinalMergedCoords, IndexLookUpCellPropertiesDict, PMTimage, MatdisplayFigureTopGuys, *args, **kwargs):        
        super().__init__(*args, **kwargs)
        self.GeneralSettingDict = GeneralSettingDict
        self.RankedAllCellProperties = RankedAllCellProperties
        self.CurrentPos = FinalMergedCoords
        self.IndexLookUpCellPropertiesDict = IndexLookUpCellPropertiesDict
        self.ShowTopCellImg = PMTimage
        self.MatdisplayFigureTopGuys = MatdisplayFigureTopGuys
        
        self.IndexLookUpCellPropertiesDictRow = self.IndexLookUpCellPropertiesDict['row_{}_column_{}'.format(self.CurrentPos[0], self.CurrentPos[1])][0]
        self.IndexLookUpCellPropertiesDictCol = self.IndexLookUpCellPropertiesDict['row_{}_column_{}'.format(self.CurrentPos[0], self.CurrentPos[1])][1]
        
        self.ludlStage = LudlStage("COM6")
    def run(self):
        self.TopCellAx = self.MatdisplayFigureTopGuys.add_subplot(111)

        print ('-----------------------------------')
        
        #stage movement
        self.ludlStage.moveAbs(self.CurrentPos[0],self.CurrentPos[1])
        time.sleep(1)
                        
        S = ImageAnalysis(self.ShowTopCellImg, self.ShowTopCellImg) #The same as ImageAnalysis(Data_dict_0[Pic_name], Data_dict_1[Pic_name]), call the same image with same dictionary index.
        v1, v2, mask_1, mask_2, thres = S.applyMask(self.GeneralSettingDict['openingfactor'], 
                                                    self.GeneralSettingDict['closingfactor'], 
                                                    self.GeneralSettingDict['binary_adaptive_block_size'])
        S.showlabel_with_rank_givenAx(self.GeneralSettingDict['smallestsize'], mask_1, v1, self.IndexLookUpCellPropertiesDictRow, self.IndexLookUpCellPropertiesDictCol, self.RankedAllCellProperties, 'Mean intensity in contour', self.GeneralSettingDict['selectnum'], self.TopCellAx)

        print ('-----------------------------------')

        

        