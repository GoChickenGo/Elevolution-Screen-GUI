# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 20:54:40 2019

@author: xinmeng
"""
from __future__ import division
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPen, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QSpinBox, QGridLayout, QPushButton, QGroupBox, QLineEdit, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QTabWidget, QCheckBox, QFileDialog

import pyqtgraph as pg

import sys
import numpy as np

from pmt_thread import pmtimagingTest
from constants import MeasurementConstants
from generalDaqer import execute_constant_vpatch
import wavegenerator
from generalDaqer import execute_analog_readin_optional_digital, execute_digital
from generalDaqerThread import execute_analog_readin_optional_digital_thread
from PIL import Image
from adfunctiongenerator import generate_AO_for640, generate_AO_for488, generate_DO_forcameratrigger, generate_DO_for640blanking, generate_AO_for532, generate_AO_forpatch, generate_DO_forblankingall, generate_DO_for532blanking, generate_DO_for488blanking, generate_DO_forPerfusion
from pyqtgraph import PlotDataItem, TextItem
from matlabAnalysis import readbinaryfile, extractV
import os
import scipy.signal as sg

from skimage.io import imread
#Setting graph settings
"""
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOption('useOpenGL', True)
pg.setConfigOption('leftButtonPan', False)
"""
pg.setConfigOptions(imageAxisOrder='row-major')
'''
class pmtwindow(pg.GraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.l = pg.GraphicsLayout(border=(100,100,100))
        self.setCentralItem(self.l)
        self.show()
        self.setWindowTitle('pyqtgraph example: GraphicsLayout')
        self.resize(800,600)
        #self.win = pg.GraphicsLayoutWidget()
        
        #block 1 containing pmt image
        self.w0 = self.l.addLayout(row=0, col=0)        
        self.w0.addLabel('PMT image', row=0, col=0) 
        self.vb = self.w0.addViewBox(row=1, col=0, lockAspect=True, colspan=2)       
        ## lock the aspect ratio so pixels are always square
        self.setAspectLocked(True)
        
        ## Create image item
        self.pmt_img = pg.ImageItem(border='w')
        self.vb.addItem(self.pmt_img)
        # Add histogram
        #self.w1 = self.l.addLayout(row=0, col=1)
        self.hiswidget = pg.HistogramLUTItem()
        self.l.addItem(self.hiswidget)
        self.hiswidget.setImageItem(self.pmt_img)
        self.hiswidget.autoHistogramRange()
        
        # create ROI
        self.w2 = self.l.addLayout()
        self.w2.addLabel('ROI', row=0, col=0)        
        self.vb2 = self.w2.addViewBox(row=1, col=0, lockAspect=True, colspan=1)
        self.vb2.name = 'ROI'
        
        self.imgroi = pg.ImageItem()
        self.vb2.addItem(self.imgroi)        
        self.roi = pg.RectROI([20, 20], [20, 20], pen=(0,9))
        self.roi.addRotateFreeHandle([1,0], [0.5, 0.5])
        
        #for self.roi in self.rois:
            #roi.sigRegionChanged.connect(update)
        self.vb.addItem(self.roi)# add ROIs to main image
        
    def update_pmt_Window(self, data):
        """Get a window of the most recent 'windowSize' samples (or less if not available)."""
        self.pmt_img.setImage(data)
        self.imgroi.setImage(self.roi.getArrayRegion(data, self.pmt_img), levels=(0, data.max()))

class weightedimagewindow(pg.GraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.l_weightedimgwindow = pg.GraphicsLayout(border=(10,10,10))
        self.setCentralItem(self.l_weightedimgwindow)
        self.show()
        self.setWindowTitle('weightedimgwindow')
        self.resize(300,250)
        #self.win = pg.GraphicsLayoutWidget()
        
        #block 1 containing pmt image
        self.w0_weightedimgwindow = self.l_weightedimgwindow.addLayout(row=0, col=0)        
        #self.w0_weightedimgwindow.addLabel('Average image', row=0, col=0) 
        self.vb_weightedimgwindow = self.w0_weightedimgwindow.addViewBox(row=0, col=0, lockAspect=True, colspan=1, invertY=True)# ImageItem issue! invertY : https://github.com/pyqtgraph/pyqtgraph/issues/315
        ## lock the aspect ratio so pixels are always square
        self.setAspectLocked(True)
        
        ## Create image item
        self.weightedimgItem = pg.ImageItem(border='w')
        self.vb_weightedimgwindow.addItem(self.weightedimgItem)
        # Add histogram
        #self.w1 = self.l.addLayout(row=0, col=1)
        self.hiswidget_weight = pg.HistogramLUTItem()
        self.hiswidget_weight.autoHistogramRange()
        self.l_weightedimgwindow.addItem(self.hiswidget_weight)
        self.hiswidget_weight.setImageItem(self.weightedimgItem)
        

        # create ROI
        self.w2 = self.l_averageimagewindow.addLayout()
        self.w2.addLabel('ROI', row=0, col=0)        
        self.vb2 = self.w2.addViewBox(row=1, col=0, lockAspect=True, colspan=1)
        self.vb2.name = 'ROI'
        
        self.imgroi = pg.ImageItem()
        self.vb2.addItem(self.imgroi)        
        
        # create ROI
        self.rois = []
        self.rois.append(pg.RectROI([20, 20], [20, 20], pen=(0,9)))
        self.rois[-1].addRotateHandle([1,0], [0.5, 0.5])
        
        self.roi_weighted = pg.RectROI([20, 20], [20, 20], pen=(0,9))
        self.roi_weighted.addRotateFreeHandle([1,0], [0.5, 0.5])
        
        #for self.roi in self.rois:
            #roi.sigRegionChanged.connect(update)
        self.vb_weightedimgwindow.addItem(self.roi_weighted)# add ROIs to main image

'''        
        
class Mainbody(QWidget):
    
    waveforms_generated = pyqtSignal(object, object, list, int)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #------------------------Initiating patchclamp class-------------------
        self.pmtTest = pmtimagingTest()
        self.OC = 0.1
        #----------------------------------------------------------------------
        #----------------------------------GUI---------------------------------
        #----------------------------------------------------------------------
        self.setMinimumSize(1200,950)
        self.setWindowTitle("Tupolev v1.0")
        self.layout = QGridLayout(self)
        # Setting tabs
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()        
        # Add tabs
        self.tabs.addTab(self.tab1,"PMT imaging")
        self.tabs.addTab(self.tab2,"Waveform")
        self.tabs.addTab(self.tab3,"Patch clamp")
        self.tabs.addTab(self.tab4,"Image analysis")
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------GUI for PMT tab------------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------  
        #**************************************************************************************************************************************        
        pmtimageContainer = QGroupBox("PMT image")
        self.pmtimageLayout = QGridLayout()
        
        self.pmtvideoWidget = pg.ImageView()
        self.pmtvideoWidget.ui.roiBtn.hide()
        self.pmtvideoWidget.ui.menuBtn.hide()  
        self.pmtvideoWidget.resize(500,500)
        self.pmtimageLayout.addWidget(self.pmtvideoWidget, 0, 0)
        
        pmtroiContainer = QGroupBox("PMT ROI")
        self.pmtimageroiLayout = QGridLayout()
        
        self.pmt_roiwidget = pg.GraphicsLayoutWidget()
        self.pmtvideoWidget.resize(200,200)
        self.pmt_roiwidget.addLabel('ROI', row=0, col=0) 
        # create ROI
        self.vb_2 = self.pmt_roiwidget.addViewBox(row=1, col=0, lockAspect=True, colspan=1)
        self.vb_2.name = 'ROI'
        
        self.pmtimgroi = pg.ImageItem()
        self.vb_2.addItem(self.pmtimgroi)        
        self.roi = pg.RectROI([20, 20], [20, 20], pen=(0,9))
        self.roi.addRotateFreeHandle([1,0], [0.5, 0.5])
        
        self.pmtvb = self.pmtvideoWidget.getView()
        self.pmtimageitem = self.pmtvideoWidget.getImageItem()
        self.pmtvb.addItem(self.roi)# add ROIs to main image
        
        self.pmtimageroiLayout.addWidget(self.pmt_roiwidget, 0, 0)
        
        pmtimageContainer.setMinimumWidth(800)
        
        pmtimageContainer.setLayout(self.pmtimageLayout)
        pmtroiContainer.setLayout(self.pmtimageroiLayout)
        #----------------------------Control-----------------------------------
        controlContainer = QGroupBox("Galvo Scanning Panel")
        self.controlLayout = QGridLayout()
    
        self.saveButton_pmt = QPushButton("Save image")
        self.saveButton_pmt.clicked.connect(lambda: self.saveimage_pmt())
        self.controlLayout.addWidget(self.saveButton_pmt, 3, 6)
    
        self.startButton_pmt = QPushButton("Start")
        self.startButton_pmt.clicked.connect(lambda: self.measure_pmt())

        self.controlLayout.addWidget(self.startButton_pmt, 3, 7)
        
        self.stopButton = QPushButton("Stop")
        self.stopButton.clicked.connect(lambda: self.stopMeasurement_pmt())
        self.controlLayout.addWidget(self.stopButton, 3, 8)
        
        #-----------------------------------Galvo scanning------------------------------------------------------------------------
        self.textboxAA_pmt = QComboBox()
        self.textboxAA_pmt.addItems(['500000', '50000'])
        self.controlLayout.addWidget(self.textboxAA_pmt, 2, 0)
        self.controlLayout.addWidget(QLabel("Sampling rate:"), 1, 0)
        
        #self.controlLayout.addWidget(QLabel("Galvo raster scanning : "), 1, 0)
        
        self.textbox1B_pmt = QComboBox()
        self.textbox1B_pmt.addItems(['-5','-3','-1'])
        self.controlLayout.addWidget(self.textbox1B_pmt, 1, 2)
        self.controlLayout.addWidget(QLabel("voltXMin"), 1, 1)

        self.textbox1C_pmt = QComboBox()
        self.textbox1C_pmt.addItems(['5','3','1'])
        self.controlLayout.addWidget(self.textbox1C_pmt, 2, 2)
        self.controlLayout.addWidget(QLabel("voltXMax"), 2, 1)

        self.textbox1D_pmt = QComboBox()
        self.textbox1D_pmt.addItems(['-5','-3','-1'])
        self.controlLayout.addWidget(self.textbox1D_pmt, 1, 4)
        self.controlLayout.addWidget(QLabel("voltYMin"), 1, 3)

        self.textbox1E_pmt = QComboBox()
        self.textbox1E_pmt.addItems(['5','3','1'])
        self.controlLayout.addWidget(self.textbox1E_pmt, 2, 4)
        self.controlLayout.addWidget(QLabel("voltYMax"), 2, 3)

        self.textbox1F_pmt = QComboBox()
        self.textbox1F_pmt.addItems(['500','256'])
        self.controlLayout.addWidget(self.textbox1F_pmt, 1, 6)
        self.controlLayout.addWidget(QLabel("X pixel number"), 1, 5)

        self.textbox1G_pmt = QComboBox()
        self.textbox1G_pmt.addItems(['500','256'])
        self.controlLayout.addWidget(self.textbox1G_pmt, 2, 6)
        self.controlLayout.addWidget(QLabel("Y pixel number"), 2, 5)
        
        self.textbox1H_pmt = QComboBox()
        self.textbox1H_pmt.addItems(['5','2','3','8','1'])
        self.controlLayout.addWidget(self.textbox1H_pmt, 1, 8)
        self.controlLayout.addWidget(QLabel("average over:"), 1, 7)
        
        controlContainer.setLayout(self.controlLayout)
        
        #---------------------------Set tab1 layout---------------------------
        pmtmaster = QGridLayout()
        pmtmaster.addWidget(pmtimageContainer, 0,0)
        pmtmaster.addWidget(pmtroiContainer,0,1)        
        pmtmaster.addWidget(controlContainer,1,0,1,2)
        
        self.tab1.setLayout(pmtmaster)
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------GUI for Waveform tab-------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #**************************************************************************************************************************************
        self.Galvo_samples = self.finalwave_640 = self.finalwave_488 = self.finalwave_532=self.finalwave_patch =None
        self.finalwave_cameratrigger=self.final_galvotrigger=self.finalwave_blankingall=self.finalwave_640blanking=self.finalwave_532blanking=self.finalwave_488blanking=self.finalwave_Perfusion_1 = None
        
        AnalogContainer = QGroupBox("Analog signals")
        self.AnalogLayout = QGridLayout() #self.AnalogLayout manager
        
        
        self.button_execute = QPushButton('EXECUTE AD', self)
        self.AnalogLayout.addWidget(self.button_execute, 3, 3)
        
        self.button_execute.clicked.connect(self.execute_tread)    
        
        self.textbox2A = QComboBox()
        self.textbox2A.addItems(['galvos', '640 AO','532 AO', '488 AO', 'V-patch'])
        self.AnalogLayout.addWidget(self.textbox2A, 3, 0)
        
        self.button2 = QPushButton('Add', self)
        self.AnalogLayout.addWidget(self.button2, 3, 1)
        
        self.button_del_analog = QPushButton('Delete', self)
        self.AnalogLayout.addWidget(self.button_del_analog, 3, 2)        
        
        
        self.dictionary_switch_list = []

        self.button2.clicked.connect(self.chosen_wave)
        self.button_del_analog.clicked.connect(self.del_chosen_wave)
        #self.textbox2A.currentIndexChanged.connect(self.chosen_wave)
        self.wavetablayout= QGridLayout()
        
        self.wavetabs = QTabWidget()
        self.wavetab1 = QWidget()
        self.wavetab2 = QWidget()
        self.wavetab3 = QWidget()
        self.wavetab4 = QWidget()
        # Add tabs
        self.wavetabs.addTab(self.wavetab1,"Block")
        self.wavetabs.addTab(self.wavetab2,"Ramp")
        self.wavetabs.addTab(self.wavetab3,"Matlab")
        self.wavetabs.addTab(self.wavetab4,"Galvo")
        
        #------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------General settings-------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------       
        ReadContainer = QGroupBox("General settings")
        self.ReadLayout = QGridLayout() #self.AnalogLayout manager

        self.textboxBB = QComboBox()
        self.textboxBB.addItems(['galvos', '640AO', '488AO', '532AO', 'patchAO','cameratrigger', 'blankingall', '640blanking','532blanking','488blanking', 'Perfusion_1'])
        self.ReadLayout.addWidget(self.textboxBB, 0, 1)
        self.ReadLayout.addWidget(QLabel("Reference waveform:"), 0, 0)

        self.button_all = QPushButton('Show waveforms', self)
        self.ReadLayout.addWidget(self.button_all, 0, 4)
        self.button_all.clicked.connect(self.show_all)

        self.button_stop_waveforms = QPushButton('Stop', self)
        self.ReadLayout.addWidget(self.button_stop_waveforms, 0, 5)
        self.button_stop_waveforms.clicked.connect(self.stopMeasurement_daqer)        
                
        self.button_clear_canvas = QPushButton('Clear canvas', self)
        self.ReadLayout.addWidget(self.button_clear_canvas, 1, 5)
        
        self.button_clear_canvas.clicked.connect(self.clear_canvas)  
        
        self.textboxAA = QComboBox()
        self.textboxAA.addItems(['500000', '50000'])
        self.ReadLayout.addWidget(self.textboxAA, 0, 3)
        self.ReadLayout.addWidget(QLabel("Sampling rate for all:"), 0, 2)
        
        # Read-in channels
        self.textbox111A = QCheckBox("PMT")
        self.ReadLayout.addWidget(self.textbox111A, 1, 1)     

        self.textbox222A = QCheckBox("Vp")
        self.ReadLayout.addWidget(self.textbox222A, 1, 2)   
        
        self.textbox333A = QCheckBox("Ip")
        self.ReadLayout.addWidget(self.textbox333A, 1, 3)
        
        self.ReadLayout.addWidget(QLabel("Recording channels: "), 1, 0)
        
        ReadContainer.setLayout(self.ReadLayout)

        # ------------------------------------------------------ANALOG-----------------------------------------------------------        

        
        # Tab for general block wave
        self.textbox2B = QLineEdit(self)
        self.wavetablayout.addWidget(self.textbox2B, 0, 1)
        self.wavetablayout.addWidget(QLabel("Frequency in period:"), 0, 0)

        self.textbox2C = QLineEdit(self)
        self.textbox2C.setPlaceholderText('0')
        self.wavetablayout.addWidget(self.textbox2C, 1, 1)
        self.wavetablayout.addWidget(QLabel("Offset (ms):"), 1, 0)
        
        self.textbox2D = QLineEdit(self)
        self.wavetablayout.addWidget(self.textbox2D, 0, 3)
        self.wavetablayout.addWidget(QLabel("Period (ms, 1 cycle):"), 0, 2)   
        
        self.textbox2E = QLineEdit(self)
        self.textbox2E.setPlaceholderText('1')
        self.wavetablayout.addWidget(self.textbox2E, 1, 3)
        self.wavetablayout.addWidget(QLabel("Repeat:"), 1, 2) 
        
        self.wavetablayout.addWidget(QLabel("DC (%):"), 0, 4)
        self.textbox2F = QComboBox()
        self.textbox2F.addItems(['50','10'])
        self.wavetablayout.addWidget(self.textbox2F, 0, 5)
        
        self.textbox2G = QLineEdit(self)
        self.textbox2G.setPlaceholderText('0')
        self.wavetablayout.addWidget(self.textbox2G, 1, 5)
        self.wavetablayout.addWidget(QLabel("Gap between repeat (samples):"), 1, 4)
        
        self.wavetablayout.addWidget(QLabel("Starting amplitude (V):"), 2, 0)
        self.textbox2H = QComboBox()
        self.textbox2H.addItems(['5','1'])
        self.wavetablayout.addWidget(self.textbox2H, 2, 1)        

        self.textbox2I = QLineEdit(self)
        self.textbox2I.setPlaceholderText('0')
        self.wavetablayout.addWidget(self.textbox2I, 3, 1)
        self.wavetablayout.addWidget(QLabel("Baseline (V):"), 3, 0)

        self.wavetablayout.addWidget(QLabel("Step (V):"), 2, 2)
        self.textbox2J = QComboBox()
        self.textbox2J.addItems(['0','1', '2'])
        self.wavetablayout.addWidget(self.textbox2J, 2, 3)

        self.wavetablayout.addWidget(QLabel("Cycles:"), 3, 2)
        self.textbox2K = QComboBox()
        self.textbox2K.addItems(['1','2', '3'])
        self.wavetablayout.addWidget(self.textbox2K, 3, 3)
                
        self.wavetab1.setLayout(self.wavetablayout)
        
        #----------------------------------------------Tab for galvo------------------------------------------------
        #----------------------------------------------Galvo scanning----------------------------------------------
        
        self.galvotablayout= QGridLayout()
        
        self.textbox1B = QComboBox()
        self.textbox1B.addItems(['-5','-3','-1'])
        self.galvotablayout.addWidget(self.textbox1B, 0, 1)
        self.galvotablayout.addWidget(QLabel("voltXMin"), 0, 0)

        self.textbox1C = QComboBox()
        self.textbox1C.addItems(['5','3','1'])
        self.galvotablayout.addWidget(self.textbox1C, 1, 1)
        self.galvotablayout.addWidget(QLabel("voltXMax"), 1, 0)

        self.textbox1D = QComboBox()
        self.textbox1D.addItems(['-5','-3','-1'])
        self.galvotablayout.addWidget(self.textbox1D, 0, 3)
        self.galvotablayout.addWidget(QLabel("voltYMin"), 0, 2)

        self.textbox1E = QComboBox()
        self.textbox1E.addItems(['5','3','1'])
        self.galvotablayout.addWidget(self.textbox1E, 1, 3)
        self.galvotablayout.addWidget(QLabel("voltYMax"), 1, 2)

        self.textbox1F = QComboBox()
        self.textbox1F.addItems(['500','256'])
        self.galvotablayout.addWidget(self.textbox1F, 0, 5)
        self.galvotablayout.addWidget(QLabel("X pixel number"), 0, 4)

        self.textbox1G = QComboBox()
        self.textbox1G.addItems(['500','256'])
        self.galvotablayout.addWidget(self.textbox1G, 1, 5)
        self.galvotablayout.addWidget(QLabel("Y pixel number"), 1, 4)
        
        self.textbox1I = QLineEdit(self)
        self.textbox1I.setPlaceholderText('0')
        self.galvotablayout.addWidget(self.textbox1I, 2, 1)
        self.galvotablayout.addWidget(QLabel("Offset (ms):"), 2, 0)
        
        self.textbox1J = QLineEdit(self)
        self.textbox1J.setPlaceholderText('0')
        self.galvotablayout.addWidget(self.textbox1J, 2, 3)
        self.galvotablayout.addWidget(QLabel("Gap between scans:"), 2, 2)       
        
        self.textbox1H = QComboBox()
        self.textbox1H.addItems(['5','2','3','8','1'])
        self.galvotablayout.addWidget(self.textbox1H, 2, 5)
        self.galvotablayout.addWidget(QLabel("average over:"), 2, 4)
        '''
        self.button1 = QPushButton('SHOW WAVE', self)
        self.galvotablayout.addWidget(self.button1, 1, 11)
        
        self.button1.clicked.connect(self.generate_galvos)
        self.button1.clicked.connect(self.generate_galvos_graphy)
        
        self.button_triggerforcam = QPushButton('With trigger!', self)
        self.galvotablayout.addWidget(self.button_triggerforcam, 2, 9)
        
        self.textbox1K = QComboBox()
        self.textbox1K.addItems(['0','1'])
        self.galvotablayout.addWidget(self.textbox1K, 2, 10)
        
        self.button_triggerforcam.clicked.connect(self.generate_galvotrigger)        
        self.button_triggerforcam.clicked.connect(self.generate_galvotrigger_graphy)
        '''
        self.wavetab4.setLayout(self.galvotablayout)
        
        self.AnalogLayout.addWidget(self.wavetabs, 4, 0, 2, 6) 
        
        AnalogContainer.setLayout(self.AnalogLayout)
        
        #------------------------------------------------------------------------------------------------------------------@@@@@
        #----------------------------------------------------------Digital-------------------------------------------------@@@@@
        #------------------------------------------------------------------------------------------------------------------@@@@@       
        DigitalContainer = QGroupBox("Digital signals")
        self.DigitalLayout = QGridLayout() #self.AnalogLayout manager
        
        self.textbox3A = QComboBox()
        self.textbox3A.addItems(['cameratrigger',
                                  'galvotrigger', 
                                  'blankingall',
                                  '640blanking',
                                  '532blanking',
                                  '488blanking',
                                  'Perfusion_1'])
        self.DigitalLayout.addWidget(self.textbox3A, 0, 0)
        
        self.button3 = QPushButton('Add', self)
        self.DigitalLayout.addWidget(self.button3, 0, 1)
        self.button3.clicked.connect(self.chosen_wave_digital)
        #---------------------------------------------------------------------------------------------------------------------------        
        self.button_execute_digital = QPushButton('EXECUTE DIGITAL', self)
        self.DigitalLayout.addWidget(self.button_execute_digital, 0, 3)
        
        self.button_del_digital = QPushButton('Delete', self)
        self.DigitalLayout.addWidget(self.button_del_digital, 0, 2)
        
        self.button_execute_digital.clicked.connect(self.execute_digital)
        self.button_del_digital.clicked.connect(self.del_chosen_wave_digital)
        # ------------------------------------------------------Wave settings------------------------------------------
        self.digitalwavetablayout= QGridLayout()
        
        self.digitalwavetabs = QTabWidget()
        self.digitalwavetab1 = QWidget()
        self.digitalwavetab2 = QWidget()
        self.digitalwavetab3 = QWidget()

        # Add tabs
        self.digitalwavetabs.addTab(self.digitalwavetab1,"Block")
        self.digitalwavetabs.addTab(self.digitalwavetab2,"Ramp")
        self.digitalwavetabs.addTab(self.digitalwavetab3,"Matlab")

        
        self.textbox11B = QLineEdit(self)
        self.digitalwavetablayout.addWidget(self.textbox11B, 0, 1)
        self.digitalwavetablayout.addWidget(QLabel("Frequency in period:"), 0, 0)

        self.textbox11C = QLineEdit(self)
        self.textbox11C.setPlaceholderText('0')
        self.digitalwavetablayout.addWidget(self.textbox11C, 1, 1)
        self.digitalwavetablayout.addWidget(QLabel("Offset (ms):"), 1, 0)
        
        self.textbox11D = QLineEdit(self)
        self.digitalwavetablayout.addWidget(self.textbox11D, 0, 3)
        self.digitalwavetablayout.addWidget(QLabel("Period (ms):"), 0, 2)   
        
        self.textbox11E = QLineEdit(self)
        self.textbox11E.setPlaceholderText('1')
        self.digitalwavetablayout.addWidget(self.textbox11E, 1, 3)
        self.digitalwavetablayout.addWidget(QLabel("Repeat:"), 1, 2) 
        
        self.digitalwavetablayout.addWidget(QLabel("DC (%):"), 0, 4)
        self.textbox11F = QComboBox()
        self.textbox11F.addItems(['50','10','0','100'])
        self.digitalwavetablayout.addWidget(self.textbox11F, 0, 5)

        self.textbox11G = QLineEdit(self)
        self.textbox11G.setPlaceholderText('0')
        self.digitalwavetablayout.addWidget(self.textbox11G, 1, 5)
        self.digitalwavetablayout.addWidget(QLabel("Gap between repeat (samples):"), 1, 4)
        
        self.digitalwavetab1.setLayout(self.digitalwavetablayout)      
        self.DigitalLayout.addWidget(self.digitalwavetabs, 2, 0, 3, 6) 

        DigitalContainer.setLayout(self.DigitalLayout)

        
        #------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------Display win-------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------  
        self.pw = pg.PlotWidget(title='Waveform plot')
        self.pw.setLabel('bottom', 'Time', units='s')
        self.pw.setLabel('left', 'Value', units='V')
        self.pw.addLine(x=0)
        self.pw.addLine(y=0)
        self.pw.setMinimumHeight(180)
        #------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------Data win-------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------  
        self.pw_data = pg.PlotWidget(title='Data')
        self.pw_data.setLabel('bottom', 'Time', units='s')
        self.pw_data.setMinimumHeight(180)
        #self.pw_data.setLabel('left', 'Value', units='V')
        #-------------------------------------------------------------Adding to master----------------------------------------
        master_waveform = QGridLayout()
        master_waveform.addWidget(AnalogContainer, 1, 0)
        master_waveform.addWidget(DigitalContainer, 2, 0)
        master_waveform.addWidget(ReadContainer, 0, 0)
        master_waveform.addWidget(self.pw, 3, 0)
        master_waveform.addWidget(self.pw_data, 4, 0)
        self.tab2.setLayout(master_waveform)        
        #**************************************************************************************************************************************        
        #self.setLayout(pmtmaster)
        self.layout.addWidget(self.tabs, 0, 1, 5, 5)
        self.setLayout(self.layout)
        
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------GUI for Data analysis tab--------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #**************************************************************************************************************************************
        readimageContainer = QGroupBox("Readin images")
        self.readimageLayout = QGridLayout()
        
        self.readimageLayout.addWidget(QLabel('File Name'), 0, 0)
       
        self.textbox_filename = QLineEdit(self)        
        self.readimageLayout.addWidget(self.textbox_filename, 0, 1)
        
        self.button_browse = QPushButton('Browse', self)
        self.readimageLayout.addWidget(self.button_browse, 0, 2) 
        
        self.button_browse.clicked.connect(self.getfile)

        self.button_load = QPushButton('Load', self)
        self.readimageLayout.addWidget(self.button_load, 0, 3) 
        
        self.Spincamsamplingrate = QSpinBox(self)
        self.Spincamsamplingrate.setMaximum(2000)
        self.Spincamsamplingrate.setValue(250)
        self.Spincamsamplingrate.setSingleStep(250)
        self.readimageLayout.addWidget(self.Spincamsamplingrate, 0, 7)
        self.readimageLayout.addWidget(QLabel("Camera FPS:"), 0, 6)
        
        self.button_load.clicked.connect(self.loadtiffile)
        self.button_load.clicked.connect(lambda: self.loadcurve(self.fileName))
        self.button_load.clicked.connect(lambda: self.displayElectricalsignal())
        self.button_load.clicked.connect(lambda: self.displaycamtrace())
        
        readimageContainer.setLayout(self.readimageLayout)

        #------------------------------------------------------V, I curve display window-------------------------------------------------------
        Curvedisplay_Container = QGroupBox("Electrical signal window")
        self.Curvedisplay_Layout = QGridLayout()
        
        #Voltage window
        self.pw_patch_voltage = pg.PlotWidget(title='Voltage plot')
        self.pw_patch_voltage.setLabel('bottom', 'Time', units='s')
        self.pw_patch_voltage.setLabel('left', 'Voltage', units='mV')        
        
        self.Curvedisplay_Layout.addWidget(self.pw_patch_voltage, 0,0)
        
        #Current window
        self.pw_patch_current = pg.PlotWidget(title='Current plot')
        self.pw_patch_current.setLabel('bottom', 'Time', units='s')
        self.pw_patch_current.setLabel('left', 'Current', units='pA')
        self.Curvedisplay_Layout.addWidget(self.pw_patch_current, 1,0) 
        
        '''        
        self.datadislay_label = pg.LabelItem(justify='right')
        self.pw_patch_current.addItem(self.datadislay_label)
        '''
        #cross hair
        self.vLine = pg.InfiniteLine(pos=0.4, angle=90, movable=True)
        self.pw_patch_current.addItem(self.vLine, ignoreBounds=True)
        
        #Camera trace window
        self.pw_patch_camtrace = pg.PlotWidget(title='Trace plot')
        self.pw_patch_camtrace.setLabel('bottom', 'Time', units='s')
        self.pw_patch_camtrace.setLabel('left', 'signal', units=' counts/ms')
        
        
        #self.pw_patch_camtrace.addLegend(offset=(20,5)) # Add legend here, Plotitem with name will be automated displayed.
        self.Curvedisplay_Layout.addWidget(self.pw_patch_camtrace, 2,0) 

        self.vLine_cam = pg.InfiniteLine(pos=0.4, angle=90, movable=True)
        self.pw_patch_camtrace.addItem(self.vLine_cam, ignoreBounds=True)

        Curvedisplay_Container.setLayout(self.Curvedisplay_Layout)
        Curvedisplay_Container.setMaximumHeight(550)
        
        self.vLine.sigPositionChangeFinished.connect(self.showpointdata)
        self.vLine_cam.sigPositionChangeFinished.connect(self.showpointdata_camtrace)
        #------------------------------------------------------Image Analysis-Average window-------------------------------------------------------
        imageanalysis_average_Container = QGroupBox("Image Analysis-Average window")
        self.imageanalysisLayout_average = QGridLayout()
                
        #self.pw_averageimage = averageimagewindow()
        self.pw_averageimage = pg.ImageView()
        self.pw_averageimage.ui.roiBtn.hide()
        self.pw_averageimage.ui.menuBtn.hide()        
    
        self.imageanalysisLayout_average.addWidget(self.pw_averageimage, 0, 0, 3, 3)
        
        self.button_average = QPushButton('Cal. average', self)
        self.button_average.setMaximumWidth(70)
        self.imageanalysisLayout_average.addWidget(self.button_average, 0, 3) 
        self.button_average.clicked.connect(self.calculateaverage)
        
        imageanalysis_average_Container.setLayout(self.imageanalysisLayout_average)
        imageanalysis_average_Container.setMinimumHeight(200)
        #------------------------------------------------------Image Analysis-weighV window-------------------------------------------------------
        imageanalysis_weight_Container = QGroupBox("Image Analysis-Weight window")
        self.imageanalysisLayout_weight = QGridLayout()
                
        #self.pw_averageimage = averageimagewindow()
        self.pw_weightimage = pg.ImageView()
        self.pw_weightimage.ui.roiBtn.hide()
        self.pw_weightimage.ui.menuBtn.hide()
        
        self.roi_weighted = pg.PolyLineROI([[0,0], [10,10], [10,30], [30,10]], closed=True)
        self.pw_weightimage.view.addItem(self.roi_weighted)
        #self.pw_weightimage = weightedimagewindow()
        self.imageanalysisLayout_weight.addWidget(self.pw_weightimage, 0, 0, 3, 3)
        
        self.button_weight = QPushButton('Cal. weight', self)
        self.button_weight.setMaximumWidth(83)
        self.imageanalysisLayout_weight.addWidget(self.button_weight, 0, 3) 
        self.button_weight.clicked.connect(self.calculateweight)
        
        self.button_weighttrace = QPushButton('Weighted Trace', self)
        self.button_weighttrace.setMaximumWidth(83)
        self.imageanalysisLayout_weight.addWidget(self.button_weighttrace, 1, 3) 
        self.button_weighttrace.clicked.connect(self.displayweighttrace)
        
        imageanalysis_weight_Container.setLayout(self.imageanalysisLayout_weight)
        imageanalysis_weight_Container.setMinimumHeight(200)
        
        master_data_analysis = QGridLayout()
        master_data_analysis.addWidget(readimageContainer, 0, 0, 1, 2)
        master_data_analysis.addWidget(Curvedisplay_Container, 1, 0, 1, 2)
        master_data_analysis.addWidget(imageanalysis_average_Container, 2, 0, 1,1)
        master_data_analysis.addWidget(imageanalysis_weight_Container, 2, 1, 1,1)
        self.tab4.setLayout(master_data_analysis)         
       
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #------------------------------------------------Functions for Data analysis Tab------------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------  
        #**************************************************************************************************************************************        
    def getfile(self):
        self.fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', 'M:/tnw/ist/do/projects/Neurophotonics/Brinkslab/Data',"Image files (*.jpg *.tif)")
        self.textbox_filename.setText(self.fileName)
        
    def loadtiffile(self):
        print('Loading...')
        self.videostack = imread(self.fileName)
        print(self.videostack.shape)
        print('Loading complete, ready to fire')
        
    def loadcurve(self, filepath):
        for file in os.listdir(os.path.dirname(self.fileName)):
            if file.endswith(".Ip"):
                self.Ipfilename = os.path.dirname(self.fileName) + '/'+file
            elif file.endswith(".Vp"):
                self.Vpfilename = os.path.dirname(self.fileName) + '/'+file
                
        curvereadingobjective_i =  readbinaryfile(self.Ipfilename)               
        self.Ip, self.samplingrate_curve = curvereadingobjective_i.readbinarycurve()
        
        curvereadingobjective_V =  readbinaryfile(self.Vpfilename)               
        self.Vp, self.samplingrate_curve = curvereadingobjective_V.readbinarycurve()
        
    def displayElectricalsignal(self):
        
        self.patchcurrentlabel = np.arange(len(self.Ip))/self.samplingrate_curve
        
        self.PlotDataItem_patchcurrent = PlotDataItem(self.patchcurrentlabel, self.Ip*1000/self.OC)
        self.PlotDataItem_patchcurrent.setPen('b')
        self.pw_patch_current.addItem(self.PlotDataItem_patchcurrent)
        
        self.patchvoltagelabel = np.arange(len(self.Vp))/self.samplingrate_curve
        
        self.PlotDataItem_patchvoltage = PlotDataItem(self.patchvoltagelabel, self.Vp*1000/10)
        self.PlotDataItem_patchvoltage.setPen('w')
        self.pw_patch_voltage.addItem(self.PlotDataItem_patchvoltage)
        
    def showpointdata(self):
        try:
            self.pw_patch_current.removeItem(self.currenttextitem)
        except:
            self.currenttextitem=pg.TextItem(text='0',color=(255,204,255), anchor=(0, 1))
            self.currenttextitem.setPos(round(self.vLine.value(), 2), 0)
            self.pw_patch_current.addItem(self.currenttextitem)
            
            index = (np.abs(np.arange(len(self.Ip))-self.vLine.value()*self.samplingrate_curve)).argmin()
            
            self.currenttextitem.setText(str(round(self.vLine.value(), 2))+' s,I='+str(round(self.Ip[int(index)]*1000/self.OC, 2))+' pA')
        else:
            self.currenttextitem=pg.TextItem(text='0',color=(255,204,255), anchor=(0, 1))
            self.currenttextitem.setPos(round(self.vLine.value(), 2), 0)
            self.pw_patch_current.addItem(self.currenttextitem)
            
            index = (np.abs(np.arange(len(self.Ip))-self.vLine.value()*self.samplingrate_curve)).argmin()
            
            self.currenttextitem.setText(str(round(self.vLine.value(), 2))+' s,I='+str(round(self.Ip[int(index)]*1000/self.OC, 2))+' pA')    

    def showpointdata_camtrace(self):
        if self.line_cam_trace_selection == 1:
            try:
                self.pw_patch_camtrace.removeItem(self.camtracetextitem)
            except:
                self.camtracetextitem=pg.TextItem(text='0',color=(255,204,255), anchor=(0, 1))
                self.camtracetextitem.setPos(round(self.vLine_cam.value(), 2), 0)
                self.pw_patch_camtrace.addItem(self.camtracetextitem)
                
                index = (np.abs(np.arange(len(self.camsignalsum))-self.vLine_cam.value()*self.samplingrate_cam)).argmin()
                
                self.camtracetextitem.setText('Sum of pixel values:'+str(self.camsignalsum[int(index)]))
            else:
                self.camtracetextitem=pg.TextItem(text='0',color=(255,204,255), anchor=(0, 1))
                self.camtracetextitem.setPos(round(self.vLine_cam.value(), 2), 0)
                self.pw_patch_camtrace.addItem(self.camtracetextitem)
                
                index = (np.abs(np.arange(len(self.camsignalsum))-self.vLine_cam.value()*self.samplingrate_cam)).argmin()
                
                self.camtracetextitem.setText('Sum of pixel values:'+str(self.camsignalsum[int(index)]))
        else:
            try:
                self.pw_patch_camtrace.removeItem(self.camtracetextitem)
            except:
                self.camtracetextitem=pg.TextItem(text='0',color=(255,204,255), anchor=(0, 1))
                self.camtracetextitem.setPos(round(self.vLine_cam.value(), 2), 0)
                self.pw_patch_camtrace.addItem(self.camtracetextitem)
                
                index = (np.abs(np.arange(len(self.weighttrace_data))-self.vLine_cam.value()*self.samplingrate_cam)).argmin()
                
                self.camtracetextitem.setText('Weighted trace:'+str(self.weighttrace_data[int(index)]))
            else:
                self.camtracetextitem=pg.TextItem(text='0',color=(255,204,255), anchor=(0, 1))
                self.camtracetextitem.setPos(round(self.vLine_cam.value(), 2), 0)
                self.pw_patch_camtrace.addItem(self.camtracetextitem)
                
                index = (np.abs(np.arange(len(self.weighttrace_data))-self.vLine_cam.value()*self.samplingrate_cam)).argmin()
                
                self.camtracetextitem.setText('Weighted trace:'+str(self.weighttrace_data[int(index)]))
    def displaycamtrace(self):
        self.line_cam_trace_selection = 1
        self.line_cam_weightedtrace_selection = 0
        
        self.samplingrate_cam = self.Spincamsamplingrate.value()
        
        self.camsignalsum = np.zeros(len(self.videostack))
        for i in range(len(self.videostack)):
            self.camsignalsum[i] = np.sum(self.videostack[i])
            
        self.patchcamtracelabel = np.arange(len(self.camsignalsum))/self.samplingrate_cam
        
        self.PlotDataItem_patchcam = PlotDataItem(self.patchcamtracelabel, self.camsignalsum, name = 'Pixel sum trace')
        self.PlotDataItem_patchcam.setPen('w')
        self.pw_patch_camtrace.addItem(self.PlotDataItem_patchcam)        
        
    def calculateaverage(self):
        self.imganalysis_averageimage = np.mean(self.videostack, axis = 0)
        self.pw_averageimage.setImage(self.imganalysis_averageimage)
        #self.pw_averageimage.average_imgItem.setImage(self.imganalysis_averageimage)
        
    def calculateweight(self):
        self.samplingrate_cam = self.Spincamsamplingrate.value()
        self.downsample_ratio = int(self.samplingrate_curve/self.samplingrate_cam)
        self.Vp_downsample = self.Vp.reshape(-1, self.downsample_ratio).mean(axis=1)

        weight_ins = extractV(self.videostack, self.Vp_downsample*1000/10)
        self.corrimage, self.weightimage, self.sigmaimage= weight_ins.cal()

        self.pw_weightimage.setImage(self.weightimage)
        #print(self.pw_weightimage.levelMax)
        #print(self.pw_weightimage.levelMin)
        #self.pw_weightimage.weightedimgItem.setImage(self.weightimage)
        #k=self.pw_weightimage.hiswidget_weight.getLevels()
        #print(k)
        
    def displayweighttrace(self):     
        try:
            self.pw_patch_camtrace.removeItem(self.camtracetextitem) # try to remove text besides line, not a good way to do so.
            
            self.line_cam_trace_selection = 0
            self.line_cam_weightedtrace_selection = 1
            
            self.samplingrate_cam = self.Spincamsamplingrate.value()
            self.videolength = len(self.videostack)
            self.pw_patch_camtrace.removeItem(self.PlotDataItem_patchcam)      
    
            k=np.tile(self.weightimage/np.sum(self.weightimage)*self.videostack.shape[1]*self.videostack.shape[2], (self.videolength,1,1))
            self.weighttrace_tobetime = self.videostack*k
            
            self.weighttrace_data = np.zeros(self.videolength)
            for i in range(self.videolength):
                self.weighttrace_data[i] = np.mean(self.weighttrace_tobetime[i])
                
            self.patchcamtracelabel_weighted = np.arange(self.videolength)/self.samplingrate_cam
            
            self.PlotDataItem_patchcam_weighted = PlotDataItem(self.patchcamtracelabel_weighted, self.weighttrace_data, name = 'Weighted signal trace')
            self.PlotDataItem_patchcam_weighted.setPen('c')
            self.pw_patch_camtrace.addItem(self.PlotDataItem_patchcam_weighted)       
        except:
            self.line_cam_trace_selection = 0
            self.line_cam_weightedtrace_selection = 1
            
            self.samplingrate_cam = self.Spincamsamplingrate.value()
            self.videolength = len(self.videostack)
            self.pw_patch_camtrace.removeItem(self.PlotDataItem_patchcam)      
    
            k=np.tile(self.weightimage/np.sum(self.weightimage)*self.videostack.shape[1]*self.videostack.shape[2], (self.videolength,1,1))
            self.weighttrace_tobetime = self.videostack*k
            
            self.weighttrace_data = np.zeros(self.videolength)
            for i in range(self.videolength):
                self.weighttrace_data[i] = np.mean(self.weighttrace_tobetime[i])
                
            self.patchcamtracelabel_weighted = np.arange(self.videolength)/self.samplingrate_cam
            
            self.PlotDataItem_patchcam_weighted = PlotDataItem(self.patchcamtracelabel_weighted, self.weighttrace_data, name = 'Weighted signal trace')
            self.PlotDataItem_patchcam_weighted.setPen('c')
            self.pw_patch_camtrace.addItem(self.PlotDataItem_patchcam_weighted)
        
        #self.pw_averageimage.average_imgItem.setImage(self.imganalysis_averageimage)
        #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        #--------------------------------------------------------------------------------------------------------------------------------------
        #------------------------------------------------------Functions for TAB 'PMT'---------------------------------------------------------
        #-------------------------------------------------------------------------------------------------------------------------------------- 
        #**************************************************************************************************************************************
    def measure_pmt(self):
        self.Daq_sample_rate_pmt = int(self.textboxAA_pmt.currentText())
        
        #Scanning settings
        Value_voltXMin = int(self.textbox1B_pmt.currentText())
        Value_voltXMax = int(self.textbox1C_pmt.currentText())
        Value_voltYMin = int(self.textbox1D_pmt.currentText())
        Value_voltYMax = int(self.textbox1E_pmt.currentText())
        Value_xPixels = int(self.textbox1F_pmt.currentText())
        Value_yPixels = int(self.textbox1G_pmt.currentText())
        self.averagenum =int(self.textbox1H_pmt.currentText())
        
        self.pmtTest.setWave(self.Daq_sample_rate_pmt, Value_voltXMin, Value_voltXMax, Value_voltYMin, Value_voltYMax, Value_xPixels, Value_yPixels, self.averagenum)
        self.pmtTest.pmtimagingThread.measurement.connect(self.update_pmt_Graphs) #Connecting to the measurement signal 
        self.pmtTest.start()
        
    def saveimage_pmt(self):
        Localimg = Image.fromarray(self.data_pmtcontineous) #generate an image object
        Localimg.save('pmtimage.tif') #save as tif
        
        
    def update_pmt_Graphs(self, data):
        """Update graphs."""
        
        self.data_pmtcontineous = data
        self.pmtvideoWidget.setImage(data)
        self.pmtimgroi.setImage(self.roi.getArrayRegion(data, self.pmtimageitem), levels=(0, data.max()))
        #

        #self.pmtvideoWidget.update_pmt_Window(self.data_pmtcontineous)
    
        
    def stopMeasurement_pmt(self):
        """Stop the seal test."""
        self.pmtTest.aboutToQuitHandler()
    '''    
    def closeEvent(self, event):
        """On closing the application we have to make sure that the measuremnt
        stops and the device gets freed."""
        self.stopMeasurement()
    '''

        #--------------------------------------------------------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #------------------------------------------------Functions for Waveform Tab------------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------  
        #**************************************************************************************************************************************
    def chosen_wave(self):
        # make sure that the square wave tab is active now
        if self.wavetabs.currentIndex() == 0:
            if self.textbox2A.currentText() == '640 AO':
                if self.finalwave_640 is not None:
                    self.pw.removeItem(self.PlotDataItem_640AO) 
                    self.pw.removeItem(self.textitem_640AO)
                self.generate_640AO()
                self.generate_640AO_graphy()            
                self.set_switch('640AO')            
                    
            elif self.textbox2A.currentText() == '532 AO':
                if self.finalwave_532 is not None:
                    self.pw.removeItem(self.PlotDataItem_532AO) 
                    self.pw.removeItem(self.textitem_532AO)
                self.generate_532AO()
                self.generate_532AO_graphy()
                self.set_switch('532AO')
            elif self.textbox2A.currentText() == '488 AO':
                if self.finalwave_488 is not None:
                    self.pw.removeItem(self.PlotDataItem_488AO) 
                    self.pw.removeItem(self.textitem_488AO)
                self.generate_488AO()
                self.generate_488AO_graphy()
                self.set_switch('488AO')
            elif self.textbox2A.currentText() == 'V-patch':
                if self.finalwave_patch is not None:
                    self.pw.removeItem(self.PlotDataItem_patch) 
                    self.pw.removeItem(self.textitem_patch)
                self.generate_patchAO()
                self.generate_patchAO_graphy()
                self.set_switch('patchAO')
            elif self.textbox2A.currentText() == 'galvos':
                if self.Galvo_samples is not None:
                    self.pw.removeItem(self.PlotDataItem_galvos) 
                    self.pw.removeItem(self.textitem_galvos)
                self.generate_galvos()
                self.generate_galvos_graphy()
                self.set_switch('galvos')
            
    def del_chosen_wave(self):
        if self.textbox2A.currentText() == '640 AO':
            #button2.disconnect()
            self.pw.removeItem(self.PlotDataItem_640AO) 
            self.pw.removeItem(self.textitem_640AO)
            self.finalwave_640 = None
            self.del_set_switch('640AO')
            
        elif self.textbox2A.currentText() == '532 AO':
            self.pw.removeItem(self.PlotDataItem_532AO) 
            self.pw.removeItem(self.textitem_532AO)
            self.finalwave_532 = None
            self.del_set_switch('532AO')
        elif self.textbox2A.currentText() == '488 AO':
            self.pw.removeItem(self.PlotDataItem_488AO)   
            self.pw.removeItem(self.textitem_488AO)
            self.finalwave_488 = None
            self.del_set_switch('488AO')
        elif self.textbox2A.currentText() == 'V-patch':
            self.pw.removeItem(self.PlotDataItem_patch) 
            self.pw.removeItem(self.textitem_patch)
            self.finalwave_patch = None
            self.del_set_switch('patchAO')
        elif self.textbox2A.currentText() == 'galvos':
            self.pw.removeItem(self.PlotDataItem_galvos)  
            self.pw.removeItem(self.textitem_galvos)
            self.finalwave_galvos = None
            self.del_set_switch('galvos')
            
    def chosen_wave_digital(self):        
        if self.textbox3A.currentText() == 'cameratrigger':
            if self.finalwave_cameratrigger is not None:
                self.pw.removeItem(self.PlotDataItem_cameratrigger) 
                self.pw.removeItem(self.textitem_cameratrigger)
            self.generate_cameratrigger()
            self.generate_cameratrigger_graphy()
            self.set_switch('cameratrigger')           
        elif self.textbox3A.currentText() == 'galvotrigger':
            if self.final_galvotrigger is not None:
                self.pw.removeItem(self.PlotDataItem_galvotrigger) 
                self.pw.removeItem(self.textitem_galvotrigger)
            self.generate_galvotrigger()
            self.generate_galvotrigger_graphy()
            self.set_switch('galvotrigger')
        elif self.textbox3A.currentText() == 'blankingall':
            if self.finalwave_blankingall is not None:
                self.pw.removeItem(self.PlotDataItem_blankingall) 
                self.pw.removeItem(self.textitem_blankingall)
            self.generate_blankingall()
            self.generate_blankingall_graphy()
            self.set_switch('blankingall')                                   
        elif self.textbox3A.currentText() == '640blanking':
            if self.finalwave_640blanking is not None:
                self.pw.removeItem(self.PlotDataItem_640blanking) 
                self.pw.removeItem(self.textitem_640blanking)
            self.generate_640blanking()
            self.generate_640blanking_graphy()
            self.set_switch('640blanking')                                 
        elif self.textbox3A.currentText() == '532blanking':
            if self.finalwave_532blanking is not None:
                self.pw.removeItem(self.PlotDataItem_532blanking) 
                self.pw.removeItem(self.textitem_532blanking)
            self.generate_532blanking()
            self.generate_532blanking_graphy()
            self.set_switch('532blanking')    
        elif self.textbox3A.currentText() == '488blanking':
            if self.finalwave_488blanking is not None:
                self.pw.removeItem(self.PlotDataItem_488blanking) 
                self.pw.removeItem(self.textitem_488blanking)
            self.generate_488blanking()
            self.generate_488blanking_graphy()
            self.set_switch('488blanking')
        elif self.textbox3A.currentText() == 'Perfusion_1':
            if self.finalwave_Perfusion_1 is not None:
                self.pw.removeItem(self.PlotDataItem_Perfusion_1) 
                self.pw.removeItem(self.textitem_Perfusion_1)
            self.generate_Perfusion_1()
            self.generate_Perfusion_1_graphy()
            self.set_switch('Perfusion_1')     

    def del_chosen_wave_digital(self):        
        if self.textbox3A.currentText() == 'cameratrigger':
            self.pw.removeItem(self.PlotDataItem_cameratrigger)   
            self.pw.removeItem(self.textitem_cameratrigger)
            self.finalwave_cameratrigger = None
            self.del_set_switch('cameratrigger')
          
        elif self.textbox3A.currentText() == 'galvotrigger':
            self.pw.removeItem(self.PlotDataItem_galvotrigger) 
            self.pw.removeItem(self.textitem_galvotrigger)
            self.final_galvotrigger = None
            self.del_set_switch('galvotrigger')
        elif self.textbox3A.currentText() == 'blankingall':
            self.pw.removeItem(self.PlotDataItem_blankingall) 
            self.pw.removeItem(self.textitem_blankingall)
            self.finalwave_blankingall = None
            self.del_set_switch('blankingall')
                                   
        elif self.textbox3A.currentText() == '640blanking':
            self.pw.removeItem(self.PlotDataItem_640blanking)    
            self.pw.removeItem(self.textitem_640blanking)
            self.finalwave_640blanking = None
            self.del_set_switch('640blanking')
                                 
        elif self.textbox3A.currentText() == '532blanking':
            self.pw.removeItem(self.PlotDataItem_532blanking)
            self.pw.removeItem(self.textitem_532blanking)
            self.finalwave_532blanking = None
            self.del_set_switch('532blanking')   
        elif self.textbox3A.currentText() == '488blanking':
            self.pw.removeItem(self.PlotDataItem_488blanking)   
            self.pw.removeItem(self.textitem_488blanking)
            self.finalwave_488blanking = None
            self.del_set_switch('488blanking')
        elif self.textbox3A.currentText() == 'Perfusion_1':
            self.pw.removeItem(self.PlotDataItem_Perfusion_1)   
            self.pw.removeItem(self.textitem_Perfusion_1)
            self.finalwave_Perfusion_1 = None
            self.del_set_switch('Perfusion_1')                           
                                     
    def generate_galvos(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        
        #Scanning settings
        #if int(self.textbox1A.currentText()) == 1:
        Value_voltXMin = int(self.textbox1B.currentText())
        Value_voltXMax = int(self.textbox1C.currentText())
        Value_voltYMin = int(self.textbox1D.currentText())
        Value_voltYMax = int(self.textbox1E.currentText())
        Value_xPixels = int(self.textbox1F.currentText())
        Value_yPixels = int(self.textbox1G.currentText())
        self.averagenum =int(self.textbox1H.currentText())
        
        if not self.textbox1I.text():
            self.Galvo_samples_offset = 1
            self.offsetsamples_galvo = []

        else:
            self.Galvo_samples_offset = int(self.textbox1I.text())
            
            self.offsetsamples_number_galvo = int((self.Galvo_samples_offset/1000)*self.uiDaq_sample_rate) # By default one 0 is added so that we have a rising edge at the beginning.
            self.offsetsamples_galvo = np.zeros(self.offsetsamples_number_galvo) # Be default offsetsamples_number is an integer.    
        #Generate galvo samples            
        self.samples_1, self.samples_2= wavegenerator.waveRecPic(sampleRate = self.uiDaq_sample_rate, imAngle = 0, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, 
                         voltYMin = Value_voltYMin, voltYMax = Value_voltYMax, xPixels = Value_xPixels, yPixels = Value_yPixels, 
                         sawtooth = True)
        #ScanArrayX = wavegenerator.xValuesSingleSawtooth(sampleRate = Daq_sample_rate, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, xPixels = Value_xPixels, sawtooth = True)
        #Totalscansamples = len(self.samples_1)*self.averagenum # Calculate number of samples to feed to scanner, by default it's one frame 
        self.ScanArrayXnum = int (len(self.samples_1)/Value_yPixels) # number of samples of each individual line of x scanning
        
        #print(self.Digital_container_feeder[:, 0])
        
        self.repeated_samples_1 = np.tile(self.samples_1, self.averagenum)
        self.repeated_samples_2_yaxis = np.tile(self.samples_2, self.averagenum)

        self.repeated_samples_1 = np.append(self.offsetsamples_galvo, self.repeated_samples_1)
        self.repeated_samples_2_yaxis = np.append(self.offsetsamples_galvo, self.repeated_samples_2_yaxis)
        
        self.Galvo_samples = np.vstack((self.repeated_samples_1,self.repeated_samples_2_yaxis))
        
        return self.Galvo_samples
            
    def generate_galvos_graphy(self):

        self.xlabelhere_galvos = np.arange(len(self.repeated_samples_2_yaxis))/self.uiDaq_sample_rate
        self.PlotDataItem_galvos = PlotDataItem(self.xlabelhere_galvos, self.repeated_samples_2_yaxis)
        self.PlotDataItem_galvos.setPen('w')
        self.pw.addItem(self.PlotDataItem_galvos)
        self.textitem_galvos = pg.TextItem(text='galvos', color=('w'), anchor=(1, 1))
        self.textitem_galvos.setPos(0, 5)
        self.pw.addItem(self.textitem_galvos)

            
    def generate_galvotrigger(self):
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        #Scanning settings
        #if int(self.textbox1A.currentText()) == 1:
        Value_voltXMin = int(self.textbox1B.currentText())
        Value_voltXMax = int(self.textbox1C.currentText())
        Value_voltYMin = int(self.textbox1D.currentText())
        Value_voltYMax = int(self.textbox1E.currentText())
        Value_xPixels = int(self.textbox1F.currentText())
        Value_yPixels = int(self.textbox1G.currentText())
        self.averagenum =int(self.textbox1H.currentText())
        
        if not self.textbox1I.text():
            self.Galvo_samples_offset = 1
            self.offsetsamples_galvo = []

        else:
            self.Galvo_samples_offset = int(self.textbox1I.text())
            
            self.offsetsamples_number_galvo = int((self.Galvo_samples_offset/1000)*self.uiDaq_sample_rate) # By default one 0 is added so that we have a rising edge at the beginning.
            self.offsetsamples_galvo = np.zeros(self.offsetsamples_number_galvo) # Be default offsetsamples_number is an integer.    
        #Generate galvo samples            
        self.samples_1, self.samples_2= wavegenerator.waveRecPic(sampleRate = self.uiDaq_sample_rate, imAngle = 0, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, 
                         voltYMin = Value_voltYMin, voltYMax = Value_voltYMax, xPixels = Value_xPixels, yPixels = Value_yPixels, 
                         sawtooth = True)
        self.ScanArrayXnum = int (len(self.samples_1)/Value_yPixels) # number of samples of each individual line of x scanning
        
        #print(self.Digital_container_feeder[:, 0])
        
        self.repeated_samples_1 = np.tile(self.samples_1, self.averagenum)
        self.repeated_samples_2_yaxis = np.tile(self.samples_2, self.averagenum)

        self.repeated_samples_1 = np.append(self.offsetsamples_galvo, self.repeated_samples_1)
        self.repeated_samples_2_yaxis = np.append(self.offsetsamples_galvo, self.repeated_samples_2_yaxis)
   
        samplenumber_oneframe = len(self.samples_1)
        
        self.true_sample_num_singleperiod_galvotrigger = round((20/1000)*self.uiDaq_sample_rate) # Default the trigger lasts for 20 ms.
        self.false_sample_num_singleperiod_galvotrigger = samplenumber_oneframe - self.true_sample_num_singleperiod_galvotrigger
        
        self.true_sample_singleperiod_galvotrigger = np.ones(self.true_sample_num_singleperiod_galvotrigger, dtype=bool)
        self.true_sample_singleperiod_galvotrigger[0] = False  # first one False to give a rise.
        
        self.sample_singleperiod_galvotrigger = np.append(self.true_sample_singleperiod_galvotrigger, np.zeros(self.false_sample_num_singleperiod_galvotrigger, dtype=bool))
        
        self.sample_repeatedperiod_galvotrigger = np.tile(self.sample_singleperiod_galvotrigger, self.averagenum)
        
        self.offset_galvotrigger = np.array(self.offsetsamples_galvo, dtype=bool)
        
        self.final_galvotrigger = np.append(self.offset_galvotrigger, self.sample_repeatedperiod_galvotrigger)
        return self.final_galvotrigger
        
    def generate_galvotrigger_graphy(self):
        self.xlabelhere_galvos = np.arange(len(self.repeated_samples_2_yaxis))/self.uiDaq_sample_rate
        self.final_galvotrigger_forgraphy = self.final_galvotrigger.astype(int)
        self.PlotDataItem_galvotrigger = PlotDataItem(self.xlabelhere_galvos, self.final_galvotrigger_forgraphy)
        self.PlotDataItem_galvotrigger.setPen(100,100,200)
        self.pw.addItem(self.PlotDataItem_galvotrigger)
        
        self.textitem_galvotrigger = pg.TextItem(text='galvotrigger', color=(100,100,200), anchor=(1, 1))
        self.textitem_galvotrigger.setPos(0, -5)
        self.pw.addItem(self.textitem_galvotrigger)

        
    def generate_640AO(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_2 = float(self.textbox2B.text())
        if not self.textbox2C.text():
            self.uiwaveoffset_2 = 0
        else:
            self.uiwaveoffset_2 = int(self.textbox2C.text()) # in ms
        self.uiwaveperiod_2 = int(self.textbox2D.text())
        self.uiwaveDC_2 = int(self.textbox2F.currentText())
        if not self.textbox2E.text():
            self.uiwaverepeat_2 = 1
        else:
            self.uiwaverepeat_2 = int(self.textbox2E.text())
        if not self.textbox2G.text():
            self.uiwavegap_2 = 0
        else:
            self.uiwavegap_2 = int(self.textbox2G.text())
        self.uiwavestartamplitude_2 = float(self.textbox2H.currentText())
        if not self.textbox2I.text():
            self.uiwavebaseline_2 = 0
        else:
            self.uiwavebaseline_2 = float(self.textbox2I.text())
        self.uiwavestep_2 = int(self.textbox2J.currentText())
        self.uiwavecycles_2 = int(self.textbox2K.currentText())   
        
            
        s = generate_AO_for640(self.uiDaq_sample_rate, self.uiwavefrequency_2, self.uiwaveoffset_2, self.uiwaveperiod_2, self.uiwaveDC_2
                               , self.uiwaverepeat_2, self.uiwavegap_2, self.uiwavestartamplitude_2, self.uiwavebaseline_2, self.uiwavestep_2, self.uiwavecycles_2)
        self.finalwave_640 = s.generate()
        return self.finalwave_640
            
    def generate_640AO_graphy(self):            
        xlabelhere_640 = np.arange(len(self.finalwave_640))/self.uiDaq_sample_rate
        #plt.plot(xlabelhere_galvo, samples_1)
        self.PlotDataItem_640AO = PlotDataItem(xlabelhere_640, self.finalwave_640)
        self.PlotDataItem_640AO.setPen('r')
        self.pw.addItem(self.PlotDataItem_640AO)
        
        self.textitem_640AO = pg.TextItem(text='640 AO', color=('r'), anchor=(1, 1))
        self.textitem_640AO.setPos(0, 4)
        self.pw.addItem(self.textitem_640AO)
           

    def generate_488AO(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_488AO = float(self.textbox2B.text())
        if not self.textbox2C.text():
            self.uiwaveoffset_488AO = 0
        else:
            self.uiwaveoffset_488AO = int(self.textbox2C.text()) # in ms
        self.uiwaveperiod_488AO = int(self.textbox2D.text())
        self.uiwaveDC_488AO = int(self.textbox2F.currentText())
        if not self.textbox2E.text():
            self.uiwaverepeat_488AO = 1
        else:
            self.uiwaverepeat_488AO = int(self.textbox2E.text())
        if not self.textbox2G.text():
            self.uiwavegap_488AO = 0
        else:
            self.uiwavegap_488AO = int(self.textbox2G.text())
        self.uiwavestartamplitude_488AO = float(self.textbox2H.currentText())
        if not self.textbox2I.text():
            self.uiwavebaseline_488AO = 0
        else:
            self.uiwavebaseline_488AO = float(self.textbox2I.text())
        self.uiwavestep_488AO = int(self.textbox2J.currentText())
        self.uiwavecycles_488AO = int(self.textbox2K.currentText())   
                    
        s = generate_AO_for488(self.uiDaq_sample_rate, self.uiwavefrequency_488AO, self.uiwaveoffset_488AO, self.uiwaveperiod_488AO, self.uiwaveDC_488AO
                               , self.uiwaverepeat_488AO, self.uiwavegap_488AO, self.uiwavestartamplitude_488AO, self.uiwavebaseline_488AO, self.uiwavestep_488AO, self.uiwavecycles_488AO)
        self.finalwave_488 = s.generate()
        return self.finalwave_488
            
    def generate_488AO_graphy(self):
        xlabelhere_488 = np.arange(len(self.finalwave_488))/self.uiDaq_sample_rate
        #plt.plot(xlabelhere_galvo, samples_1)
        self.PlotDataItem_488AO = PlotDataItem(xlabelhere_488, self.finalwave_488)
        self.PlotDataItem_488AO.setPen('b')
        self.pw.addItem(self.PlotDataItem_488AO)
        
        self.textitem_488AO = pg.TextItem(text='488 AO', color=('b'), anchor=(1, 1))
        self.textitem_488AO.setPos(0, 2)
        self.pw.addItem(self.textitem_488AO)

        
    def generate_532AO(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_532AO = float(self.textbox2B.text())
        if not self.textbox2C.text():
            self.uiwaveoffset_532AO = 0
        else:
            self.uiwaveoffset_532AO = int(self.textbox2C.text()) # in ms
        self.uiwaveperiod_532AO = int(self.textbox2D.text())
        self.uiwaveDC_532AO = int(self.textbox2F.currentText())
        if not self.textbox2E.text():
            self.uiwaverepeat_532AO = 1
        else:
            self.uiwaverepeat_532AO = int(self.textbox2E.text())
        if not self.textbox2G.text():
            self.uiwavegap_532AO = 0
        else:
            self.uiwavegap_532AO = int(self.textbox2G.text())
        self.uiwavestartamplitude_532AO = float(self.textbox2H.currentText())
        if not self.textbox2I.text():
            self.uiwavebaseline_532AO = 0
        else:
            self.uiwavebaseline_532AO = float(self.textbox2I.text())
        self.uiwavestep_532AO = int(self.textbox2J.currentText())
        self.uiwavecycles_532AO = int(self.textbox2K.currentText())   
        
        #if int(self.textbox4A.currentText()) == 1:
            
        s = generate_AO_for532(self.uiDaq_sample_rate, self.uiwavefrequency_532AO, self.uiwaveoffset_532AO, self.uiwaveperiod_532AO, self.uiwaveDC_532AO
                               , self.uiwaverepeat_532AO, self.uiwavegap_532AO, self.uiwavestartamplitude_532AO, self.uiwavebaseline_532AO, self.uiwavestep_532AO, self.uiwavecycles_532AO)
        self.finalwave_532 = s.generate()
        return self.finalwave_532
            
    def generate_532AO_graphy(self):
        xlabelhere_532 = np.arange(len(self.finalwave_532))/self.uiDaq_sample_rate
        self.PlotDataItem_532AO = PlotDataItem(xlabelhere_532, self.finalwave_532)
        self.PlotDataItem_532AO.setPen('g')
        self.pw.addItem(self.PlotDataItem_532AO)
        
        self.textitem_532AO = pg.TextItem(text='532 AO', color=('g'), anchor=(1, 1))
        self.textitem_532AO.setPos(0, 3)
        self.pw.addItem(self.textitem_532AO)
        
    def generate_patchAO(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_patchAO = float(self.textbox2B.text())
        if not self.textbox2C.text():
            self.uiwaveoffset_patchAO = 0
        else:
            self.uiwaveoffset_patchAO = int(self.textbox2C.text()) # in ms
        self.uiwaveperiod_patchAO = int(self.textbox2D.text())
        self.uiwaveDC_patchAO = int(self.textbox2F.currentText())
        if not self.textbox2E.text():
            self.uiwaverepeat_patchAO = 1
        else:
            self.uiwaverepeat_patchAO = int(self.textbox2E.text())
        if not self.textbox2G.text():
            self.uiwavegap_patchAO = 0
        else:
            self.uiwavegap_patchAO = int(self.textbox2G.text())
        self.uiwavestartamplitude_patchAO = float(self.textbox2H.currentText())
        if not self.textbox2I.text():
            self.uiwavebaseline_patchAO = 0
        else:
            self.uiwavebaseline_patchAO = float(self.textbox2I.text())
        self.uiwavestep_patchAO = int(self.textbox2J.currentText())
        self.uiwavecycles_patchAO = int(self.textbox2K.currentText())   
        
        #if int(self.textbox5A.currentText()) == 1:
            
        s = generate_AO_forpatch(self.uiDaq_sample_rate, self.uiwavefrequency_patchAO, self.uiwaveoffset_patchAO, self.uiwaveperiod_patchAO, self.uiwaveDC_patchAO
                               , self.uiwaverepeat_patchAO, self.uiwavegap_patchAO, self.uiwavestartamplitude_patchAO, self.uiwavebaseline_patchAO, self.uiwavestep_patchAO, self.uiwavecycles_patchAO)
        self.finalwave_patch = s.generate()
        return self.finalwave_patch
            
    def generate_patchAO_graphy(self):
        xlabelhere_patch = np.arange(len(self.finalwave_patch))/self.uiDaq_sample_rate
        self.PlotDataItem_patch = PlotDataItem(xlabelhere_patch, self.finalwave_patch)
        self.PlotDataItem_patch.setPen(100, 100, 0)
        self.pw.addItem(self.PlotDataItem_patch)
        
        self.textitem_patch = pg.TextItem(text='patch '+str(self.uiwavefrequency_patchAO)+'hz', color=(100, 100, 0), anchor=(1, 1))
        self.textitem_patch.setPos(0, 1)
        self.pw.addItem(self.textitem_patch)


    def generate_cameratrigger(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_cameratrigger = float(self.textbox11B.text())
        if not self.textbox11C.text():
            self.uiwaveoffset_cameratrigger = 0
        else:
            self.uiwaveoffset_cameratrigger = int(self.textbox11C.text())
        self.uiwaveperiod_cameratrigger = int(self.textbox11D.text())
        self.uiwaveDC_cameratrigger = int(self.textbox11F.currentText())
        if not self.textbox11E.text():
            self.uiwaverepeat_cameratrigger_number = 1
        else:
            self.uiwaverepeat_cameratrigger_number = int(self.textbox11E.text())
        if not self.textbox11G.text():
            self.uiwavegap_cameratrigger = 0
        else:
            self.uiwavegap_cameratrigger = int(self.textbox11G.text())
        
        #if int(self.textbox11A.currentText()) == 1:
            
        cameratrigger = generate_DO_forcameratrigger(self.uiDaq_sample_rate, self.uiwavefrequency_cameratrigger, self.uiwaveoffset_cameratrigger,
                                                     self.uiwaveperiod_cameratrigger, self.uiwaveDC_cameratrigger, self.uiwaverepeat_cameratrigger_number, self.uiwavegap_cameratrigger)
        self.finalwave_cameratrigger = cameratrigger.generate()
        return self.finalwave_cameratrigger
            
    def generate_cameratrigger_graphy(self):

        xlabelhere_cameratrigger = np.arange(len(self.finalwave_cameratrigger))/self.uiDaq_sample_rate
        self.finalwave_cameratrigger_forgraphy = self.finalwave_cameratrigger.astype(int)
        self.PlotDataItem_cameratrigger = PlotDataItem(xlabelhere_cameratrigger, self.finalwave_cameratrigger_forgraphy)
        self.PlotDataItem_cameratrigger.setPen('c')
        self.pw.addItem(self.PlotDataItem_cameratrigger)
        
        self.textitem_cameratrigger = pg.TextItem(text='cameratrigger '+str(self.uiwavefrequency_cameratrigger)+'hz', color=('c'), anchor=(1, 1))
        self.textitem_cameratrigger.setPos(0, 0)
        self.pw.addItem(self.textitem_cameratrigger)
    
            
    def generate_640blanking(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_640blanking = float(self.textbox11B.text())
        if not self.textbox11C.text():
            self.uiwaveoffset_640blanking = 0
        else:
            self.uiwaveoffset_640blanking = int(self.textbox11C.text())
        self.uiwaveperiod_640blanking = int(self.textbox11D.text())
        self.uiwaveDC_640blanking = int(self.textbox11F.currentText())
        if not self.textbox11E.text():
            self.uiwaverepeat_640blanking_number = 1
        else:
            self.uiwaverepeat_640blanking_number = int(self.textbox11E.text())
        if not self.textbox11G.text():
            self.uiwavegap_640blanking = 0
        else:
            self.uiwavegap_640blanking = int(self.textbox11G.text())
        
        #if int(self.textbox22A.currentText()) == 1:
            
        blanking640 = generate_DO_for640blanking(self.uiDaq_sample_rate, self.uiwavefrequency_640blanking, self.uiwaveoffset_640blanking,
                                                     self.uiwaveperiod_640blanking, self.uiwaveDC_640blanking, self.uiwaverepeat_640blanking_number, self.uiwavegap_640blanking)
        self.finalwave_640blanking = blanking640.generate()
        return self.finalwave_640blanking
            
    def generate_640blanking_graphy(self):    

        xlabelhere_640blanking = np.arange(len(self.finalwave_640blanking))/self.uiDaq_sample_rate
        self.final_640blanking_forgraphy = self.finalwave_640blanking.astype(int)
        self.PlotDataItem_640blanking = PlotDataItem(xlabelhere_640blanking, self.final_640blanking_forgraphy)
        self.PlotDataItem_640blanking.setPen(255,204,255)
        self.pw.addItem(self.PlotDataItem_640blanking)
        
        self.textitem_640blanking = pg.TextItem(text='640blanking', color=(255,204,255), anchor=(1, 1))
        self.textitem_640blanking.setPos(0, -2)
        self.pw.addItem(self.textitem_640blanking)

        
    def generate_532blanking(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_532blanking = float(self.textbox11B.text())
        if not self.textbox11C.text():
            self.uiwaveoffset_532blanking = 0
        else:
            self.uiwaveoffset_532blanking = int(self.textbox11C.text())
        self.uiwaveperiod_532blanking = int(self.textbox11D.text())
        self.uiwaveDC_532blanking = int(self.textbox11F.currentText())
        if not self.textbox11E.text():
            self.uiwaverepeat_532blanking_number = 1
        else:
            self.uiwaverepeat_532blanking_number = int(self.textbox11E.text())
        if not self.textbox11G.text():
            self.uiwavegap_532blanking = 0
        else:
            self.uiwavegap_532blanking = int(self.textbox11G.text())
        
        #if int(self.textbox33A.currentText()) == 1:
            
        blanking532 = generate_DO_for532blanking(self.uiDaq_sample_rate, self.uiwavefrequency_532blanking, self.uiwaveoffset_532blanking,
                                                     self.uiwaveperiod_532blanking, self.uiwaveDC_532blanking, self.uiwaverepeat_532blanking_number, self.uiwavegap_532blanking)
        self.finalwave_532blanking = blanking532.generate()
        return self.finalwave_532blanking
            
    def generate_532blanking_graphy(self):    

        xlabelhere_532blanking = np.arange(len(self.finalwave_532blanking))/self.uiDaq_sample_rate
        self.final_532blanking_forgraphy = self.finalwave_532blanking.astype(int)
        self.PlotDataItem_532blanking = PlotDataItem(xlabelhere_532blanking, self.final_532blanking_forgraphy)
        self.PlotDataItem_532blanking.setPen('y')
        self.pw.addItem(self.PlotDataItem_532blanking)
        
        self.textitem_532blanking = pg.TextItem(text='532blanking', color=('y'), anchor=(1, 1))
        self.textitem_532blanking.setPos(0, -3)
        self.pw.addItem(self.textitem_532blanking)

        
    def generate_488blanking(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_488blanking = float(self.textbox11B.text())
        if not self.textbox11C.text():
            self.uiwaveoffset_488blanking = 0
        else:
            self.uiwaveoffset_488blanking = int(self.textbox11C.text())
        self.uiwaveperiod_488blanking = int(self.textbox11D.text())
        self.uiwaveDC_488blanking = int(self.textbox11F.currentText())
        if not self.textbox11E.text():
            self.uiwaverepeat_488blanking_number = 1
        else:
            self.uiwaverepeat_488blanking_number = int(self.textbox11E.text())
        if not self.textbox11G.text():
            self.uiwavegap_488blanking = 0
        else:
            self.uiwavegap_488blanking = int(self.textbox11G.text())
        
        #if int(self.textbox44A.currentText()) == 1:
            
        blanking488 = generate_DO_for488blanking(self.uiDaq_sample_rate, self.uiwavefrequency_488blanking, self.uiwaveoffset_488blanking,
                                                     self.uiwaveperiod_488blanking, self.uiwaveDC_488blanking, self.uiwaverepeat_488blanking_number, self.uiwavegap_488blanking)
        self.finalwave_488blanking = blanking488.generate()
        return self.finalwave_488blanking
            
    def generate_488blanking_graphy(self):    

        xlabelhere_488blanking = np.arange(len(self.finalwave_488blanking))/self.uiDaq_sample_rate
        self.final_488blanking_forgraphy = self.finalwave_488blanking.astype(int)
        self.PlotDataItem_488blanking = PlotDataItem(xlabelhere_488blanking, self.final_488blanking_forgraphy)
        self.PlotDataItem_488blanking.setPen(255,51,153)
        self.pw.addItem(self.PlotDataItem_488blanking)
        
        self.textitem_488blanking = pg.TextItem(text='488blanking', color=(255,51,153), anchor=(1, 1))
        self.textitem_488blanking.setPos(0, -4)
        self.pw.addItem(self.textitem_488blanking)

        
    def generate_blankingall(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_blankingall = float(self.textbox11B.text())
        if not self.textbox11C.text():
            self.uiwaveoffset_blankingall = 0
        else:
            self.uiwaveoffset_blankingall = int(self.textbox11C.text())
        self.uiwaveperiod_blankingall = int(self.textbox11D.text())
        self.uiwaveDC_blankingall = int(self.textbox11F.currentText())
        if not self.textbox11E.text():
            self.uiwaverepeat_blankingall_number = 1
        else:
            self.uiwaverepeat_blankingall_number = int(self.textbox11E.text())
        if not self.textbox11G.text():
            self.uiwavegap_blankingall = 0
        else:
            self.uiwavegap_blankingall = int(self.textbox11G.text())
        
        #if int(self.textbox55A.currentText()) == 1:
            
        blankingall = generate_DO_forblankingall(self.uiDaq_sample_rate, self.uiwavefrequency_blankingall, self.uiwaveoffset_blankingall,
                                                     self.uiwaveperiod_blankingall, self.uiwaveDC_blankingall, self.uiwaverepeat_blankingall_number, self.uiwavegap_blankingall)
        self.finalwave_blankingall = blankingall.generate()
        return self.finalwave_blankingall
            
    def generate_blankingall_graphy(self):    

        xlabelhere_blankingall = np.arange(len(self.finalwave_blankingall))/self.uiDaq_sample_rate
        self.final_blankingall_forgraphy = self.finalwave_blankingall.astype(int)
        self.PlotDataItem_blankingall = PlotDataItem(xlabelhere_blankingall, self.final_blankingall_forgraphy)
        self.PlotDataItem_blankingall.setPen(255,229,204)
        self.pw.addItem(self.PlotDataItem_blankingall)
        
        self.textitem_blankingall = pg.TextItem(text='blankingall', color=(255,229,204), anchor=(1, 1))
        self.textitem_blankingall.setPos(0, -1)
        self.pw.addItem(self.textitem_blankingall)
        
    def generate_Perfusion_1(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_Perfusion_1 = float(self.textbox11B.text())
        if not self.textbox11C.text():
            self.uiwaveoffset_Perfusion_1 = 0
        else:
            self.uiwaveoffset_Perfusion_1 = int(self.textbox11C.text())
        self.uiwaveperiod_Perfusion_1 = int(self.textbox11D.text())
        self.uiwaveDC_Perfusion_1 = int(self.textbox11F.currentText())
        if not self.textbox11E.text():
            self.uiwaverepeat_Perfusion_1_number = 1
        else:
            self.uiwaverepeat_Perfusion_1_number = int(self.textbox11E.text())
        if not self.textbox11G.text():
            self.uiwavegap_Perfusion_1 = 0
        else:
            self.uiwavegap_Perfusion_1 = int(self.textbox11G.toPlainText())
        
        #if int(self.textbox66A.currentText()) == 1:
            
        Perfusion_1 = generate_DO_forPerfusion(self.uiDaq_sample_rate, self.uiwavefrequency_Perfusion_1, self.uiwaveoffset_Perfusion_1,
                                                     self.uiwaveperiod_Perfusion_1, self.uiwaveDC_Perfusion_1, self.uiwaverepeat_Perfusion_1_number, self.uiwavegap_Perfusion_1)
        self.finalwave_Perfusion_1 = Perfusion_1.generate()
        return self.finalwave_Perfusion_1
            
    def generate_Perfusion_1_graphy(self):    

        xlabelhere_Perfusion_1 = np.arange(len(self.finalwave_Perfusion_1))/self.uiDaq_sample_rate
        self.final_Perfusion_1_forgraphy = self.finalwave_Perfusion_1.astype(int)
        self.PlotDataItem_Perfusion_1 = PlotDataItem(xlabelhere_Perfusion_1, self.final_Perfusion_1_forgraphy)
        self.PlotDataItem_Perfusion_1.setPen(102,0,51)
        self.pw.addItem(self.PlotDataItem_Perfusion_1)
        
        self.textitem_Perfusion_1 = pg.TextItem(text='Perfusion_1', color=(102,0,51), anchor=(1, 1))
        self.textitem_Perfusion_1.setPos(0, -6)
        self.pw.addItem(self.textitem_Perfusion_1)
        
    def set_switch(self, name):
        #self.generate_dictionary_switch_instance[name] = 1
        if name not in self.dictionary_switch_list:
            self.dictionary_switch_list.append(name)
            print(self.dictionary_switch_list)
    def del_set_switch(self, name):
        #self.generate_dictionary_switch_instance[name] = 1
        if name in self.dictionary_switch_list:
            self.dictionary_switch_list.remove(name)
            print(self.dictionary_switch_list)
    def clear_canvas(self):
        #Back to initial state
        self.pw.clear()
        self.dictionary_switch_list =[]
        #self.Galvo_samples = self.finalwave_640 = self.finalwave_488 = self.finalwave_532=self.finalwave_patch =None
        #self.finalwave_cameratrigger=self.final_galvotrigger=self.finalwave_blankingall=self.finalwave_640blanking=self.finalwave_532blanking=self.finalwave_488blanking=self.finalwave_Perfusion_1 = None
        #self.switch_galvos=self.switch_640AO=self.switch_488AO=self.switch_532AO=self.switch_patchAO=self.switch_cameratrigger=self.switch_galvotrigger=self.switch_blankingall=self.switch_640blanking=self.switch_532blanking=self.switch_488blanking=self.switch_Perfusion_1=0        
        
    def show_all(self):

        self.switch_galvos=self.switch_640AO=self.switch_488AO=self.switch_532AO=self.switch_patchAO=self.switch_cameratrigger=self.switch_galvotrigger=self.switch_blankingall=self.switch_640blanking=self.switch_532blanking=self.switch_488blanking=self.switch_Perfusion_1=0
        color_dictionary = {'galvos':[255,255,255],
                              '640AO':[255,0,0],
                              '488AO':[0,0,255],
                              '532AO':[0,255,0],
                              'patchAO':[100, 100, 0],
                              'cameratrigger':[0,255,255],
                              'galvotrigger':[100,100,200], 
                              'blankingall':[255,229,204],
                              '640blanking':[255,204,255],
                              '532blanking':[255,255,0],
                              '488blanking':[255,51,153],
                              'Perfusion_1':[102,0,51]
                            }
        # Use dictionary to execute functions: https://stackoverflow.com/questions/9168340/using-a-dictionary-to-select-function-to-execute/9168387#9168387
        dictionary_analog = {'galvos':[self.switch_galvos,self.Galvo_samples],
                              '640AO':[self.switch_640AO,self.finalwave_640],
                              '488AO':[self.switch_488AO,self.finalwave_488],
                              '532AO':[self.switch_532AO,self.finalwave_532],
                              'patchAO':[self.switch_patchAO,self.finalwave_patch]
                             }
                              
                              
        dictionary_digital = {'cameratrigger':[self.switch_cameratrigger,self.finalwave_cameratrigger],
                              'galvotrigger':[self.switch_galvotrigger,self.final_galvotrigger], 
                              'blankingall':[self.switch_blankingall, self.finalwave_blankingall],
                              '640blanking':[self.switch_640blanking, self.finalwave_640blanking],
                              '532blanking':[self.switch_532blanking, self.finalwave_532blanking],
                              '488blanking':[self.switch_488blanking, self.finalwave_488blanking],
                              'Perfusion_1':[self.switch_Perfusion_1, self.finalwave_Perfusion_1]
                              }
        # set switch of selected waves to 1
        for i in range(len(self.dictionary_switch_list)):
            if self.dictionary_switch_list[i] in dictionary_analog:
                dictionary_analog[self.dictionary_switch_list[i]][0] = 1
                #print('switch = '+str(dictionary_analog[self.dictionary_switch_list[i]][0]))
            elif self.dictionary_switch_list[i] in dictionary_digital:
                dictionary_digital[self.dictionary_switch_list[i]][0] = 1
        # Calculate the length of reference wave
        # tags in the dictionary above should be the same as that in reference combox, then the dictionary below can work
       
        if self.textboxBB.currentText() in dictionary_analog.keys():
            reference_wave = dictionary_analog[self.textboxBB.currentText()][1]
        else:
            reference_wave = dictionary_digital[self.textboxBB.currentText()][1]
        
        if self.textboxBB.currentText() == 'galvos': # in case of using galvos as reference wave
            self.reference_length = len(reference_wave[0, :])
        else:
            self.reference_length = len(reference_wave)
        print('reference_length: '+str(self.reference_length))

        # Structured array to contain 
        # https://stackoverflow.com/questions/39622533/numpy-array-as-datatype-in-a-structured-array
        tp_analog = np.dtype([('Waveform', float, (self.reference_length,)), ('Sepcification', 'U20')])
        tp_digital = np.dtype([('Waveform', bool, (self.reference_length,)), ('Sepcification', 'U20')])
        
        self.analog_data_container = {}

        for key in dictionary_analog:
            if dictionary_analog[key][0] == 1: # if the signal line is added
                self.analog_data_container[key] = dictionary_analog[key][1]
        
        # set galvos sampele stack apart
        if 'galvos' in self.analog_data_container:
            self.analog_data_container['galvosx'+'avgnum_'+str(int(self.textbox1H.currentText()))] = self.generate_galvos()[0, :]
            self.analog_data_container['galvosy'+'ypixels_'+str(int(self.textbox1G.currentText()))] = self.generate_galvos()[1, :]
            del self.analog_data_container['galvos']
        
        # reform all waves according to the length of reference wave
        for key in self.analog_data_container:
            if len(self.analog_data_container[key]) >= self.reference_length:
                self.analog_data_container[key] = self.analog_data_container[key][0:self.reference_length]
            else:
                append_zeros = np.zeros(self.reference_length-len(self.analog_data_container[key]))
                self.analog_data_container[key] = np.append(self.analog_data_container[key], append_zeros)
            #print(len(self.analog_data_container[key]))
        self.analogcontainer_array = np.zeros(len(self.analog_data_container), dtype =tp_analog)
        analogloopnum = 0
        for key in self.analog_data_container:
            self.analogcontainer_array[analogloopnum] = np.array([(self.analog_data_container[key], key)], dtype =tp_analog)
            analogloopnum = analogloopnum+ 1
            
        #num_rows, num_cols = self.analogcontainer_array['Waveform'].shape
        print(self.analogcontainer_array['Sepcification'])
        
        # digital lines
        self.digital_data_container = {}
        
        for key in dictionary_digital:
            if dictionary_digital[key][0] == 1: # if the signal line is added
                self.digital_data_container[key] = dictionary_digital[key][1]
        
        # reform all waves according to the length of reference wave
        for key in self.digital_data_container:
            if len(self.digital_data_container[key]) >= self.reference_length:
                self.digital_data_container[key] = self.digital_data_container[key][0:self.reference_length]
            else:
                append_zeros = np.zeros(self.reference_length-len(self.digital_data_container[key]))
                self.digital_data_container[key] = np.append(self.digital_data_container[key], append_zeros)
            #print(len(self.digital_data_container[key]))
        self.digitalcontainer_array = np.zeros(len(self.digital_data_container), dtype =tp_digital)
        digitalloopnum = 0
        for key in self.digital_data_container:
            self.digitalcontainer_array[digitalloopnum] = np.array([(self.digital_data_container[key], key)], dtype =tp_digital)
            digitalloopnum = digitalloopnum+ 1
        print(self.digitalcontainer_array['Sepcification'])
                
        self.xlabelhere_all = np.arange(self.reference_length)/int(self.textboxAA.currentText())
        
        self.pw.clear()
        for i in range(analogloopnum):
                                        
            if self.analogcontainer_array['Sepcification'][i] != 'galvosx'+'avgnum_'+str(int(self.textbox1H.currentText())): #skip the galvoX, as it is too intense
                if self.analogcontainer_array['Sepcification'][i] == 'galvosy'+'ypixels_'+str(int(self.textbox1G.currentText())):
                    self.PlotDataItem_final = PlotDataItem(self.xlabelhere_all, self.analogcontainer_array['Waveform'][i])
                    #use the same color as before, taking advantages of employing same keys in dictionary
                    self.PlotDataItem_final.setPen('w')
                    self.pw.addItem(self.PlotDataItem_final)
                
                    self.textitem_final = pg.TextItem(text=str(self.analogcontainer_array['Sepcification'][i]), color=('w'), anchor=(1, 1))
                    self.textitem_final.setPos(0, i+1)
                    self.pw.addItem(self.textitem_final)
                else:
                    self.PlotDataItem_final = PlotDataItem(self.xlabelhere_all, self.analogcontainer_array['Waveform'][i])
                    #use the same color as before, taking advantages of employing same keys in dictionary
                    self.PlotDataItem_final.setPen(color_dictionary[self.analogcontainer_array['Sepcification'][i]][0],color_dictionary[self.analogcontainer_array['Sepcification'][i]][1],color_dictionary[self.analogcontainer_array['Sepcification'][i]][2])
                    self.pw.addItem(self.PlotDataItem_final)
                    
                    self.textitem_final = pg.TextItem(text=str(self.analogcontainer_array['Sepcification'][i]), color=(color_dictionary[self.analogcontainer_array['Sepcification'][i]][0],color_dictionary[self.analogcontainer_array['Sepcification'][i]][1],color_dictionary[self.analogcontainer_array['Sepcification'][i]][2]), anchor=(1, 1))
                    self.textitem_final.setPos(0, i+1)
                    self.pw.addItem(self.textitem_final)
                i += 1
        for i in range(digitalloopnum):
            digitalwaveforgraphy = self.digitalcontainer_array['Waveform'][i].astype(int)
            self.PlotDataItem_final = PlotDataItem(self.xlabelhere_all, digitalwaveforgraphy)
            self.PlotDataItem_final.setPen(color_dictionary[self.digitalcontainer_array['Sepcification'][i]][0],color_dictionary[self.digitalcontainer_array['Sepcification'][i]][1],color_dictionary[self.digitalcontainer_array['Sepcification'][i]][2])
            self.pw.addItem(self.PlotDataItem_final)
            
            self.textitem_final = pg.TextItem(text=str(self.digitalcontainer_array['Sepcification'][i]), color=(color_dictionary[self.digitalcontainer_array['Sepcification'][i]][0],color_dictionary[self.digitalcontainer_array['Sepcification'][i]][1],color_dictionary[self.digitalcontainer_array['Sepcification'][i]][2]), anchor=(1, 1))
            self.textitem_final.setPos(0, -1*i)
            self.pw.addItem(self.textitem_final)
            i += 1
        '''
        plt.figure()
        for i in range(analogloopnum):
            if self.analogcontainer_array['Sepcification'][i] != 'galvosx'+'avgnum_'+str(int(self.textbox1H.currentText())): #skip the galvoX, as it is too intense
                plt.plot(xlabelhere_all, self.analogcontainer_array['Waveform'][i])
        for i in range(digitalloopnum):
            plt.plot(xlabelhere_all, self.digitalcontainer_array['Waveform'][i])
        plt.text(0.1, 1.1, 'Time lasted:'+str(xlabelhere_all[-1])+'s', fontsize=12)
        plt.show()
        '''
        self.readinchan = []
        
        if self.textbox111A.isChecked():
            self.readinchan.append('PMT')
        if self.textbox222A.isChecked():
            self.readinchan.append('Vp')
        if self.textbox333A.isChecked():
            self.readinchan.append('Ip')       
        
        print(self.readinchan)
        self.waveforms_generated.emit(self.analogcontainer_array, self.digitalcontainer_array, self.readinchan, int(self.textboxAA.currentText()))
        #execute(int(self.textboxAA.currentText()), self.analogcontainer_array, self.digitalcontainer_array, self.readinchan)
        return self.analogcontainer_array, self.digitalcontainer_array, self.readinchan
    
    def execute_tread(self):
        self.adcollector = execute_analog_readin_optional_digital_thread()
        self.adcollector.set_waves(int(self.textboxAA.currentText()), self.analogcontainer_array, self.digitalcontainer_array, self.readinchan)
        self.adcollector.collected_data.connect(self.recive_data)
        self.adcollector.start()
        
    def execute(self):
        
        execute_analog_readin_optional_digital(int(self.textboxAA.currentText()), self.analogcontainer_array, self.digitalcontainer_array, self.readinchan)

    def execute_digital(self):
        
        execute_digital(int(self.textboxAA.currentText()), self.digitalcontainer_array)
        
    def recive_data(self, data_waveformreceived):
        
        self.channel_number = len(data_waveformreceived)
        if self.channel_number == 1:            
            self.data_collected_0 = data_waveformreceived[0]
        
        self.PlotDataItem_patch_voltage = PlotDataItem(self.xlabelhere_all, self.data_collected_0)
        #use the same color as before, taking advantages of employing same keys in dictionary
        self.PlotDataItem_patch_voltage.setPen('w')
        self.pw_data.addItem(self.PlotDataItem_patch_voltage)
    
        self.textitem_patch_voltage = pg.TextItem(('Vp'), color=('w'), anchor=(1, 1))
        self.textitem_patch_voltage.setPos(0, 1)
        self.pw_data.addItem(self.textitem_patch_voltage)
        
    def stopMeasurement_daqer(self):
        """Stop """
        self.adcollector.aboutToQuitHandler()
        #**************************************************************************************************************************************        
        #**************************************************************************************************************************************

if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainwin = Mainbody()
        mainwin.show()
        app.exec_()
    run_app()