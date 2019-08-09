# -*- coding: utf-8 -*-

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

#Setting graph settings
"""
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOption('useOpenGL', True)
pg.setConfigOption('leftButtonPan', False)
"""

class pmtwindow(pg.GraphicsLayoutWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        #self.win = pg.GraphicsLayoutWidget()
        self.view = self.addViewBox()
        ## lock the aspect ratio so pixels are always square
        self.view.setAspectLocked(True)
        
        ## Create image item
        self.pmt_img = pg.ImageItem(border='w')
        self.view.addItem(self.pmt_img)
        
    def updateWindow(self, data):
        """Get a window of the most recent 'windowSize' samples (or less if not available)."""
        self.pmt_img.setImage(data)
        
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
        self.pmtimageLayout = QVBoxLayout()
        
        self.pmtvideoWidget = pmtwindow()
        self.pmtimageLayout.addWidget(self.pmtvideoWidget)
        
        pmtimageContainer.setLayout(self.pmtimageLayout)
        #----------------------------Control-----------------------------------
        controlContainer = QGroupBox("Control")
        self.controlLayout = QGridLayout()
    
        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(lambda: self.measure())

        self.controlLayout.addWidget(self.startButton, 3, 0)
        
        self.stopButton = QPushButton("Stop")
        self.stopButton.clicked.connect(lambda: self.stopMeasurement())
        self.controlLayout.addWidget(self.stopButton, 3, 1)
        
        #-----------------------------------Galvo scanning
        self.textboxAA = QComboBox()
        self.textboxAA.addItems(['500000', '50000'])
        self.controlLayout.addWidget(self.textboxAA, 0, 2)
        self.controlLayout.addWidget(QLabel("Sampling rate for all:"), 0, 1)
        
        self.controlLayout.addWidget(QLabel("Galvo raster scanning : "), 1, 0)
        
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
        self.controlLayout.addWidget(self.textbox1H, 1, 10)
        self.controlLayout.addWidget(QLabel("average over:"), 1, 9)
        
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
                            
    def updateGraphs(self, data):
        """Update graphs."""

        self.pmtvideoWidget.updateWindow(data)
    
        
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