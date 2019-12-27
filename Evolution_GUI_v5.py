# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 23:40:26 2019

@author: Meng
"""

from __future__ import division
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPoint, QRect, QObject
from PyQt5.QtGui import QColor, QPen, QPixmap, QIcon, QTextCursor, QFont

from PyQt5.QtWidgets import (QWidget, QButtonGroup, QLabel, QSlider, QSpinBox, QDoubleSpinBox, QGridLayout, QPushButton, QGroupBox, 
                             QLineEdit, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QTabWidget, QCheckBox, QRadioButton, 
                             QFileDialog, QProgressBar, QTextEdit)

import pyqtgraph as pg
from IPython import get_ipython
import sys
import numpy as np
import csv
from code_5nov import generate_AO
from pmt_thread import pmtimagingTest, pmtimagingTest_contour
from Stagemovement_Thread import StagemovementThread
from Filtermovement_Thread import FiltermovementThread
from constants import MeasurementConstants
from generalDaqer import execute_constant_vpatch
import wavegenerator
from generalDaqer import execute_analog_readin_optional_digital, execute_digital
from generalDaqerThread import (execute_analog_readin_optional_digital_thread, execute_tread_singlesample_analog,
                                execute_tread_singlesample_digital, execute_analog_and_readin_digital_optional_camtrig_thread, DaqProgressBar)
from PIL import Image
from adfunctiongenerator import (generate_AO_for640, generate_AO_for488, generate_DO_forcameratrigger, generate_DO_for640blanking,
                                 generate_AO_for532, generate_AO_forpatch, generate_DO_forblankingall, generate_DO_for532blanking,
                                 generate_DO_for488blanking, generate_DO_forPerfusion, generate_DO_for2Pshutter, generate_ramp)
from pyqtgraph import PlotDataItem, TextItem
from matlabAnalysis import readbinaryfile, extractV
import os
import scipy.signal as sg
from scipy import interpolate
import time
from datetime import datetime
from skimage.io import imread
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from constants import HardwareConstants
import Waveformer_for_screening
from EvolutionScanningThread import ScanningExecutionThread # This is the thread file for execution.

class Mainbody(QWidget):
    
    waveforms_generated = pyqtSignal(object, object, list, int)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.chdir('./')# Set directory to current folder.
        self.setFont(QFont("Arial"))
        
        self.setMinimumSize(1000,1200)
        self.setWindowTitle("McDonnell")
        self.layout = QGridLayout(self)
        
        self.WaveformQueueDict = {}
        self.RoundQueueDict = {}
        self.RoundCoordsDict = {}
        self.WaveformQueueDict_GalvoInfor = {}
        self.GeneralSettingDict = {}
        
        self.savedirectory = './'
        #**************************************************************************************************************************************
        #-----------------------------------------------------------GUI for GeneralSettings----------------------------------------------------
        #**************************************************************************************************************************************
        GeneralSettingContainer = QGroupBox("Tanto Tanto")
        GeneralSettingContainerLayout = QGridLayout()
        
        self.saving_prefix = ''
        self.savedirectorytextbox = QtWidgets.QLineEdit(self)
        GeneralSettingContainerLayout.addWidget(self.savedirectorytextbox, 0, 1)
        
        self.prefixtextbox = QtWidgets.QLineEdit(self)
        self.prefixtextbox.setPlaceholderText('Prefix')
        GeneralSettingContainerLayout.addWidget(self.prefixtextbox, 0, 2)
        
        self.toolButtonOpenDialog = QtWidgets.QPushButton('Saving directory')
        self.toolButtonOpenDialog.setStyleSheet("QPushButton {color:teal;background-color: pink; border-style: outset;border-radius: 3px;border-width: 2px;font: bold 14px;padding: 1px}"
                                                "QPushButton:pressed {color:yellow;background-color: pink; border-style: outset;border-radius: 3px;border-width: 2px;font: bold 14px;padding: 1px}")

        self.toolButtonOpenDialog.setObjectName("toolButtonOpenDialog")
        self.toolButtonOpenDialog.clicked.connect(self._open_file_dialog)
        
        GeneralSettingContainerLayout.addWidget(self.toolButtonOpenDialog, 0, 0)
        
        ButtonExePipeline = QPushButton('Execute', self)
        ButtonExePipeline.setStyleSheet("QPushButton {color:white;background-color: teal; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                        "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        ButtonExePipeline.clicked.connect(self.ConfigGeneralSettings)        
        ButtonExePipeline.clicked.connect(self.ExecutePipeline)
        
        GeneralSettingContainerLayout.addWidget(ButtonExePipeline, 0, 3)
        GeneralSettingContainer.setLayout(GeneralSettingContainerLayout)
        
        #**************************************************************************************************************************************
        #-----------------------------------------------------------GUI for PiplineContainer---------------------------------------------------
        #**************************************************************************************************************************************
        ImageProcessingContainer = QGroupBox("Image processing settings")
        IPLayout = QGridLayout()
        
        self.selec_num_box = QSpinBox(self)
        self.selec_num_box.setMaximum(2000)
        self.selec_num_box.setValue(10)
        self.selec_num_box.setSingleStep(1)
        IPLayout.addWidget(self.selec_num_box, 0, 1)
        IPLayout.addWidget(QLabel("Winners number:"), 0, 0)
        
        self.IPsizetextbox = QComboBox()
        self.IPsizetextbox.addItems(['200','100'])
        IPLayout.addWidget(self.IPsizetextbox, 0, 3)
        IPLayout.addWidget(QLabel("Smallest size:"), 0, 2)
        
        self.opening_factorBox = QSpinBox(self)
        self.opening_factorBox.setMaximum(2000)
        self.opening_factorBox.setValue(2)
        self.opening_factorBox.setSingleStep(1)
        IPLayout.addWidget(self.opening_factorBox, 0, 5)
        IPLayout.addWidget(QLabel("Mask opening factor:"), 0, 4)
        
        self.closing_factorBox = QSpinBox(self)
        self.closing_factorBox.setMaximum(2000)
        self.closing_factorBox.setValue(2)
        self.closing_factorBox.setSingleStep(1)
        IPLayout.addWidget(self.closing_factorBox, 0, 7)
        IPLayout.addWidget(QLabel("Mask closing factor:"), 0, 6)   
        
        self.binary_adaptive_block_sizeBox = QSpinBox(self)
        self.binary_adaptive_block_sizeBox.setMaximum(2000)
        self.binary_adaptive_block_sizeBox.setValue(335)
        self.binary_adaptive_block_sizeBox.setSingleStep(50)
        IPLayout.addWidget(self.binary_adaptive_block_sizeBox, 1, 1)
        IPLayout.addWidget(QLabel("Adaptive mask size:"), 1, 0)
        
        self.contour_dilation_box = QSpinBox(self)
        self.contour_dilation_box.setMaximum(2000)
        self.contour_dilation_box.setValue(10)
        self.contour_dilation_box.setSingleStep(1)
        IPLayout.addWidget(self.contour_dilation_box, 1, 3)
        IPLayout.addWidget(QLabel("Contour thickness:"), 1, 2)
        
        IPLayout.addWidget(QLabel("Threshold-contour::"), 1, 4)
        self.find_contour_thres_box = QDoubleSpinBox(self)
        self.find_contour_thres_box.setDecimals(4)
        self.find_contour_thres_box.setMinimum(-10)
        self.find_contour_thres_box.setMaximum(10)
        self.find_contour_thres_box.setValue(0.001)
        self.find_contour_thres_box.setSingleStep(0.0001)  
        IPLayout.addWidget(self.find_contour_thres_box, 1, 5)
        
        self.cellopening_factorBox = QSpinBox(self)
        self.cellopening_factorBox.setMaximum(2000)
        self.cellopening_factorBox.setValue(1)
        self.cellopening_factorBox.setSingleStep(1)
        IPLayout.addWidget(self.cellopening_factorBox, 2, 1)
        IPLayout.addWidget(QLabel("Cell opening factor:"), 2, 0)
        
        self.cellclosing_factorBox = QSpinBox(self)
        self.cellclosing_factorBox.setMaximum(2000)
        self.cellclosing_factorBox.setValue(5)
        self.cellclosing_factorBox.setSingleStep(1)
        IPLayout.addWidget(self.cellclosing_factorBox, 2, 3)
        IPLayout.addWidget(QLabel("Cell closing factor:"), 2, 2)
        
        ImageProcessingContainer.setLayout(IPLayout)
        
        #**************************************************************************************************************************************
        #-----------------------------------------------------------GUI for PiplineContainer---------------------------------------------------
        #**************************************************************************************************************************************
        PipelineContainer = QGroupBox("Pipeline settings")
        PipelineContainerLayout = QGridLayout()
        
        self.RoundOrderBox = QSpinBox(self)
        self.RoundOrderBox.setMinimum(1)
        self.RoundOrderBox.setMaximum(1000)
        self.RoundOrderBox.setValue(1)
        self.RoundOrderBox.setSingleStep(1)
        self.RoundOrderBox.setMaximumWidth(30)
        PipelineContainerLayout.addWidget(self.RoundOrderBox, 0, 1)
        PipelineContainerLayout.addWidget(QLabel("Round sequence:"), 0, 0)
        
#        ButtonAddRound = QPushButton('Add Round', self)
#        ButtonAddRound.setStyleSheet("QPushButton {color:white;background-color: teal; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
#                                        "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        
        ButtonAddRound = QPushButton('Add Round', self)
        ButtonAddRound.setStyleSheet("QPushButton {color:white;background-color: teal; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                        "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        

        ButtonDeleteRound = QPushButton('Delete Round', self)
        ButtonDeleteRound.setStyleSheet("QPushButton {color:white;background-color: crimson; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                        "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        

        ButtonClearRound = QPushButton('Clear Rounds', self)
        ButtonClearRound.setStyleSheet("QPushButton {color:white;background-color: maroon; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                        "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        

        PipelineContainerLayout.addWidget(ButtonAddRound, 0, 2)
        ButtonAddRound.clicked.connect(self.AddFreshRound)
        ButtonAddRound.clicked.connect(self.GenerateScanCoords)
        
        PipelineContainerLayout.addWidget(ButtonDeleteRound, 0, 3)
        ButtonDeleteRound.clicked.connect(self.DeleteFreshRound)
        
        PipelineContainerLayout.addWidget(ButtonClearRound, 0, 4)
        ButtonClearRound.clicked.connect(self.ClearRoundQueue)
        
        self.BefKCLRoundNumBox = QSpinBox(self)
        self.BefKCLRoundNumBox.setMinimum(1)
        self.BefKCLRoundNumBox.setMaximum(1000)
        self.BefKCLRoundNumBox.setValue(1)
        self.BefKCLRoundNumBox.setSingleStep(1)
        self.BefKCLRoundNumBox.setMaximumWidth(30)
        PipelineContainerLayout.addWidget(self.BefKCLRoundNumBox, 0, 7)
        PipelineContainerLayout.addWidget(QLabel("Bef-Round Num:"), 0, 6)

        self.AftKCLRoundNumBox = QSpinBox(self)
        self.AftKCLRoundNumBox.setMinimum(1)
        self.AftKCLRoundNumBox.setMaximum(1000)
        self.AftKCLRoundNumBox.setValue(3)
        self.AftKCLRoundNumBox.setSingleStep(1)
        self.AftKCLRoundNumBox.setMaximumWidth(30)
        PipelineContainerLayout.addWidget(self.AftKCLRoundNumBox, 0, 9)
        PipelineContainerLayout.addWidget(QLabel("Aft-Round Num:"), 0, 8)        
        
        #**************************************************************************************************************************************
        #-----------------------------------------------------------GUI for RoundContainer-----------------------------------------------------
        #**************************************************************************************************************************************
        RoundContainer = QGroupBox("Waveform settings")
        RoundContainerLayout = QGridLayout()
        
        self.WaveformOrderBox = QSpinBox(self)
        self.WaveformOrderBox.setMinimum(1)
        self.WaveformOrderBox.setMaximum(1000)
        self.WaveformOrderBox.setValue(1)
        self.WaveformOrderBox.setSingleStep(1)
        self.WaveformOrderBox.setMaximumWidth(30)
        RoundContainerLayout.addWidget(self.WaveformOrderBox, 0, 1)
        RoundContainerLayout.addWidget(QLabel("Waveform sequence:"), 0, 0)
        
        ButtonAddWaveform = QPushButton('Add Waveform', self)
        ButtonAddWaveform.setStyleSheet("QPushButton {color:white;background-color: teal; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                        "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        

        ButtonDeleteWaveform = QPushButton('Delete Waveform', self)
        ButtonDeleteWaveform.setStyleSheet("QPushButton {color:white;background-color: crimson; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                        "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        ButtonClearWaveform = QPushButton('Clear Waveforms', self)
        ButtonClearWaveform.setStyleSheet("QPushButton {color:white;background-color: maroon; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                        "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        

        RoundContainerLayout.addWidget(ButtonAddWaveform, 0, 3)
        RoundContainerLayout.addWidget(ButtonDeleteWaveform, 0, 4)
        RoundContainerLayout.addWidget(ButtonClearWaveform, 0, 5)
        ButtonAddWaveform.clicked.connect(self.AddFreshWaveform)
        ButtonDeleteWaveform.clicked.connect(self.DeleteFreshWaveform)
        ButtonClearWaveform.clicked.connect(self.ClearWaveformQueue)
        
        self.Waveformer_widget_instance = Waveformer_for_screening.WaveformGenerator()
        self.Waveformer_widget_instance.WaveformPackage.connect(self.UpdateWaveformerSignal)
        self.Waveformer_widget_instance.GalvoScanInfor.connect(self.UpdateWaveformerGalvoInfor)

        RoundContainerLayout.addWidget(self.Waveformer_widget_instance, 2, 0, 2, 6)
        RoundContainer.setLayout(RoundContainerLayout)
        
        PipelineContainerLayout.addWidget(RoundContainer, 3, 0, 4, 10)       
        #--------------------------------------------------------------------------------------------------------------------------------------     
        
        #**************************************************************************************************************************************
        #-----------------------------------------------------------GUI for StageScanContainer-------------------------------------------------
        #**************************************************************************************************************************************        
        ScanContainer = QGroupBox("Scanning settings")        
        ScanSettingLayout = QGridLayout() #Layout manager
        
        self.ScanStartRowIndexTextbox = QSpinBox(self)
        self.ScanStartRowIndexTextbox.setMinimum(-20000)
        self.ScanStartRowIndexTextbox.setMaximum(20000)
        self.ScanStartRowIndexTextbox.setSingleStep(500)
        ScanSettingLayout.addWidget(self.ScanStartRowIndexTextbox, 0, 1)
        ScanSettingLayout.addWidget(QLabel("Start index-row:"), 0, 0)
      
        self.ScanEndRowIndexTextbox = QSpinBox(self)
        self.ScanEndRowIndexTextbox.setMinimum(-20000)
        self.ScanEndRowIndexTextbox.setMaximum(20000)
        self.ScanEndRowIndexTextbox.setSingleStep(500)
        ScanSettingLayout.addWidget(self.ScanEndRowIndexTextbox, 0, 5)
        ScanSettingLayout.addWidget(QLabel("End index-row:"), 0, 4)
        
        self.ScanStartColumnIndexTextbox = QSpinBox(self)
        self.ScanStartColumnIndexTextbox.setMinimum(-20000)
        self.ScanStartColumnIndexTextbox.setMaximum(20000)
        self.ScanStartColumnIndexTextbox.setSingleStep(500)
        ScanSettingLayout.addWidget(self.ScanStartColumnIndexTextbox, 0, 3)
        ScanSettingLayout.addWidget(QLabel("Start index-column:"), 0, 2)   
        
        self.ScanEndColumnIndexTextbox = QSpinBox(self)
        self.ScanEndColumnIndexTextbox.setMinimum(-20000)
        self.ScanEndColumnIndexTextbox.setMaximum(20000)
        self.ScanEndColumnIndexTextbox.setSingleStep(500)
        ScanSettingLayout.addWidget(self.ScanEndColumnIndexTextbox, 0, 7)
        ScanSettingLayout.addWidget(QLabel("End index-column:"), 0, 6)      

        self.ScanstepTextbox = QSpinBox(self)
        self.ScanstepTextbox.setMaximum(20000)
        self.ScanstepTextbox.setValue(1500)
        self.ScanstepTextbox.setSingleStep(500)
        ScanSettingLayout.addWidget(self.ScanstepTextbox, 1, 1)
        ScanSettingLayout.addWidget(QLabel("Step size:"), 1, 0)
        
        ScanContainer.setLayout(ScanSettingLayout)
        
        PipelineContainerLayout.addWidget(ScanContainer, 2, 0, 1, 10)       
        #--------------------------------------------------------------------------------------------------------------------------------------
        
        PipelineContainer.setLayout(PipelineContainerLayout)
        
        self.layout.addWidget(GeneralSettingContainer, 1, 0)
        self.layout.addWidget(ImageProcessingContainer, 2, 0)
        self.layout.addWidget(PipelineContainer, 3, 0)
        self.setLayout(self.layout)
        
        #------------------------------------------------------------Waveform package functions--------------------------------------------------------------------------        
    def UpdateWaveformerSignal(self, WaveformPackage):
        self.FreshWaveformPackage = WaveformPackage # Capture the newest generated waveform tuple signal from Waveformer.
    def UpdateWaveformerGalvoInfor(self, GalvoInfor):
        self.FreshWaveformGalvoInfor = GalvoInfor
    
    def AddFreshWaveform(self): # Add waveform package for single round.
        CurrentWaveformPackageSequence = self.WaveformOrderBox.value()
        self.WaveformQueueDict['WavformPackage_{}'.format(CurrentWaveformPackageSequence)] = self.FreshWaveformPackage
        
        self.WaveformQueueDict_GalvoInfor['GalvoInfor_{}'.format(CurrentWaveformPackageSequence)] = self.FreshWaveformGalvoInfor
        
    def DeleteFreshWaveform(self): # Empty the waveform container to avoid crosstalk between rounds.
        CurrentWaveformPackageSequence = self.WaveformOrderBox.value()
        del self.WaveformQueueDict['WavformPackage_{}'.format(CurrentWaveformPackageSequence)]
        
        del self.WaveformQueueDict_GalvoInfor['GalvoInfor_{}'.format(CurrentWaveformPackageSequence)]
        
    def ClearWaveformQueue(self):
        self.WaveformQueueDict = {}
        self.WaveformQueueDict_GalvoInfor = {}
    
    #--------------------------------------------------------------Round package functions------------------------------------------------------------------------        
    def AddFreshRound(self):
        CurrentRoundSequence = self.RoundOrderBox.value()
        self.RoundQueueDict['RoundPackage_{}'.format(CurrentRoundSequence)] = self.WaveformQueueDict
        self.RoundQueueDict['GalvoInforPackage_{}'.format(CurrentRoundSequence)] = self.WaveformQueueDict_GalvoInfor
             
        print(self.RoundQueueDict.keys())
        
    def GenerateScanCoords(self):
        self.CoordContainer = np.array([])
        # settings for scanning index
        position_index=[]
        row_start = int(self.ScanStartRowIndexTextbox.value()) #row position index start number
        row_end = int(self.ScanEndRowIndexTextbox.value())+1 #row position index end number
        
        column_start = int(self.ScanStartColumnIndexTextbox.value())
        column_end = int(self.ScanEndColumnIndexTextbox.value())+1  # With additional plus one, the range is fully covered by steps.
        
        step = int(self.ScanstepTextbox.value()) #length of each step, 1500 for -5~5V FOV
      
        for i in range(row_start, row_end, step):
            position_index.append(int(i))
            for j in range(column_start, column_end, step):
                position_index.append(int(j))
                
                self.CoordContainer = np.append(self.CoordContainer, (position_index))
#                print('the coords now: '+ str(self.CoordContainer))
                del position_index[-1]
                
            position_index=[]
        
        CurrentRoundSequence = self.RoundOrderBox.value()
        self.RoundCoordsDict['CoordsPackage_{}'.format(CurrentRoundSequence)] = self.CoordContainer
        
    def DeleteFreshRound(self):
        CurrentRoundSequence = self.RoundOrderBox.value()
        del self.RoundQueueDict['RoundPackage_{}'.format(CurrentRoundSequence)]
        del self.RoundCoordsDict['CoordsPackage_{}'.format(CurrentRoundSequence)]
        print(self.RoundQueueDict.keys())        
    
    def ClearRoundQueue(self):
        self.RoundQueueDict = {}
        self.RoundCoordsDict = {}
    #--------------------------------------------------------------Selection functions------------------------------------------------------------------------         
    def ConfigGeneralSettings(self):
        selectnum = int(self.selec_num_box.value())
        BefRoundNum = int(self.BefKCLRoundNumBox.value())        
        AftRoundNum = int(self.AftKCLRoundNumBox.value())        
        smallestsize = int(self.IPsizetextbox.currentText())            
        openingfactor = int(self.opening_factorBox.value())
        closingfactor = int(self.closing_factorBox.value())
        cellopeningfactor = int(self.cellopening_factorBox.value())
        cellclosingfactor = int(self.cellclosing_factorBox.value())
        binary_adaptive_block_size = int(self.binary_adaptive_block_sizeBox.value())
        self_findcontour_thres = float(self.find_contour_thres_box.value())
        contour_dilation = int(self.contour_dilation_box.value())
        savedirectory = self.savedirectory
        
        generalnamelist = ['selectnum', 'BefRoundNum', 'AftRoundNum', 'smallestsize', 'openingfactor', 'closingfactor', 'cellopeningfactor', 
                           'cellclosingfactor', 'binary_adaptive_block_size', 'self_findcontour_thres', 'contour_dilation', 'savedirectory']
        
        generallist = [selectnum, BefRoundNum, AftRoundNum, smallestsize, openingfactor, closingfactor, cellopeningfactor, 
                       cellclosingfactor, binary_adaptive_block_size, self_findcontour_thres, contour_dilation, savedirectory]
        
        for item in range(len(generallist)):
            self.GeneralSettingDict[generalnamelist[item]] = generallist[item]
            
    def _open_file_dialog(self):
        self.savedirectory = str(QtWidgets.QFileDialog.getExistingDirectory())
        self.savedirectorytextbox.setText(self.savedirectory)
        self.saving_prefix = str(self.prefixtextbox.text())
        #**************************************************************************************************************************************
        #-----------------------------------------------------------Functions for Execution----------------------------------------------------
        #**************************************************************************************************************************************   
    def ExecutePipeline(self):
        get_ipython().run_line_magic('matplotlib', 'inline') # before start, set spyder back to inline
        self.ExecuteThreadInstance = ScanningExecutionThread(self.RoundQueueDict, self.RoundCoordsDict, self.GeneralSettingDict)
        self.ExecuteThreadInstance.start()
        
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        pg.setConfigOptions(imageAxisOrder='row-major')
        mainwin = Mainbody()
        mainwin.show()
        app.exec_()
    run_app()