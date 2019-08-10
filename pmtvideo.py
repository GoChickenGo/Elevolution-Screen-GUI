# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 20:54:40 2019

@author: xinmeng
"""
from __future__ import division
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPen, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox

import pyqtgraph as pg

import sys
import numpy as np

from pmt_thread import pmtimagingTest
from constants import MeasurementConstants
from generalDaqer import execute_constant_vpatch
from PIL import Image

#Setting graph settings
"""
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOption('useOpenGL', True)
pg.setConfigOption('leftButtonPan', False)
"""

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
        '''
        # create ROI
        self.rois = []
        self.rois.append(pg.RectROI([20, 20], [20, 20], pen=(0,9)))
        self.rois[-1].addRotateHandle([1,0], [0.5, 0.5])
        '''
        self.roi = pg.RectROI([20, 20], [20, 20], pen=(0,9))
        self.roi.addRotateFreeHandle([1,0], [0.5, 0.5])
        
        #for self.roi in self.rois:
            #roi.sigRegionChanged.connect(update)
        self.vb.addItem(self.roi)# add ROIs to main image
        
    def updateWindow(self, data):
        """Get a window of the most recent 'windowSize' samples (or less if not available)."""
        self.pmt_img.setImage(data)
        self.imgroi.setImage(self.roi.getArrayRegion(data, self.pmt_img), levels=(0, data.max()))
        
class pmt_video(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #------------------------Initiating patchclamp class-------------------
        self.pmtTest = pmtimagingTest()
    
        #----------------------------------------------------------------------
        #----------------------------------GUI---------------------------------
        #----------------------------------------------------------------------
        self.setMinimumSize(300,120)
        self.setWindowTitle("PMT imaging")
        #-----------------------------Plots------------------------------------
        pmtimageContainer = QGroupBox("Output")
        self.pmtimageLayout = QGridLayout()
        
        self.pmtvideoWidget = pmtwindow()
        self.pmtimageLayout.addWidget(self.pmtvideoWidget, 0, 0)
        
        pmtimageContainer.setLayout(self.pmtimageLayout)
        #----------------------------Control-----------------------------------
        controlContainer = QGroupBox("Galvo Scanning Panel")
        self.controlLayout = QGridLayout()
    
        self.saveButton = QPushButton("Save image")
        self.saveButton.clicked.connect(lambda: self.saveimage())
        self.controlLayout.addWidget(self.saveButton, 3, 6)
    
        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(lambda: self.measure())

        self.controlLayout.addWidget(self.startButton, 3, 7)
        
        self.stopButton = QPushButton("Stop")
        self.stopButton.clicked.connect(lambda: self.stopMeasurement())
        self.controlLayout.addWidget(self.stopButton, 3, 8)
        
        #-----------------------------------Galvo scanning
        self.textboxAA = QComboBox()
        self.textboxAA.addItems(['500000', '50000'])
        self.controlLayout.addWidget(self.textboxAA, 2, 0)
        self.controlLayout.addWidget(QLabel("Sampling rate:"), 1, 0)
        
        #self.controlLayout.addWidget(QLabel("Galvo raster scanning : "), 1, 0)
        
        self.textbox1B = QComboBox()
        self.textbox1B.addItems(['-5','-3','-1'])
        self.controlLayout.addWidget(self.textbox1B, 1, 2)
        self.controlLayout.addWidget(QLabel("voltXMin"), 1, 1)

        self.textbox1C = QComboBox()
        self.textbox1C.addItems(['5','3','1'])
        self.controlLayout.addWidget(self.textbox1C, 2, 2)
        self.controlLayout.addWidget(QLabel("voltXMax"), 2, 1)

        self.textbox1D = QComboBox()
        self.textbox1D.addItems(['-5','-3','-1'])
        self.controlLayout.addWidget(self.textbox1D, 1, 4)
        self.controlLayout.addWidget(QLabel("voltYMin"), 1, 3)

        self.textbox1E = QComboBox()
        self.textbox1E.addItems(['5','3','1'])
        self.controlLayout.addWidget(self.textbox1E, 2, 4)
        self.controlLayout.addWidget(QLabel("voltYMax"), 2, 3)

        self.textbox1F = QComboBox()
        self.textbox1F.addItems(['500','256'])
        self.controlLayout.addWidget(self.textbox1F, 1, 6)
        self.controlLayout.addWidget(QLabel("X pixel number"), 1, 5)

        self.textbox1G = QComboBox()
        self.textbox1G.addItems(['500','256'])
        self.controlLayout.addWidget(self.textbox1G, 2, 6)
        self.controlLayout.addWidget(QLabel("Y pixel number"), 2, 5)
        
        self.textbox1H = QComboBox()
        self.textbox1H.addItems(['5','2','3','8','1'])
        self.controlLayout.addWidget(self.textbox1H, 1, 8)
        self.controlLayout.addWidget(QLabel("average over:"), 1, 7)
        
        controlContainer.setLayout(self.controlLayout)
        
        #---------------------------Adding to master---------------------------
        master = QVBoxLayout()
        master.addWidget(pmtimageContainer)
        master.addWidget(controlContainer)
        self.setLayout(master)
        
        #--------------------------Setting variables---------------------------
        
    def measure(self):
        self.Daq_sample_rate = int(self.textboxAA.currentText())
        
        #Scanning settings
        Value_voltXMin = int(self.textbox1B.currentText())
        Value_voltXMax = int(self.textbox1C.currentText())
        Value_voltYMin = int(self.textbox1D.currentText())
        Value_voltYMax = int(self.textbox1E.currentText())
        Value_xPixels = int(self.textbox1F.currentText())
        Value_yPixels = int(self.textbox1G.currentText())
        self.averagenum =int(self.textbox1H.currentText())
        
        self.pmtTest.setWave(self.Daq_sample_rate, Value_voltXMin, Value_voltXMax, Value_voltYMin, Value_voltYMax, Value_xPixels, Value_yPixels, self.averagenum)
        self.pmtTest.pmtimagingThread.measurement.connect(self.updateGraphs) #Connecting to the measurement signal 
        self.pmtTest.start()
        
    def saveimage(self):
        Localimg = Image.fromarray(self.data) #generate an image object
        Localimg.save('pmtimage.tif') #save as tif
        
        
    def updateGraphs(self, data):
        """Update graphs."""
        self.data = data

        self.pmtvideoWidget.updateWindow(self.data)
    
        
    def stopMeasurement(self):
        """Stop the seal test."""
        self.pmtTest.aboutToQuitHandler()
        
    def closeEvent(self, event):
        """On closing the application we have to make sure that the measuremnt
        stops and the device gets freed."""
        self.stopMeasurement()
    
        
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainwin = pmt_video()
        mainwin.show()
        app.exec_()
    run_app()