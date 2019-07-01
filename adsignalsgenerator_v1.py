# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:56:49 2019

@author: xinmeng
"""
import sys
import numpy as np
from matplotlib import pyplot as plt
from IPython import get_ipython
from matplotlib.ticker import FormatStrFormatter
import wavegenerator
from configuration import Configuration
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QPlainTextEdit, QGroupBox

class adgenerator(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(adgenerator, self).__init__(*args, **kwargs)

        #----------------------------------------------------------------------
        #----------------------------------GUI---------------------------------
        #----------------------------------------------------------------------
        self.setMinimumSize(300,120)
        self.setWindowTitle("Buon appetito!")
        
        AnalogContainer = QGroupBox("Analog signals")
        self.AnalogLayout = QGridLayout() #self.AnalogLayout manager
               
        self.textboxBB = QComboBox()
        self.textboxBB.addItems(['Galvo raster scanning', '640 AO', '488 AO', '532 AO'])
        self.AnalogLayout.addWidget(self.textboxBB, 0, 8)
        self.AnalogLayout.addWidget(QLabel("Reference waveform:"), 0, 7)        
        
        # Galvo scanning
        self.textboxAA = QComboBox()
        self.textboxAA.addItems(['500000', '50000'])
        self.AnalogLayout.addWidget(self.textboxAA, 0, 2)
        self.AnalogLayout.addWidget(QLabel("Sampling rate for all:"), 0, 1)
        
        self.textbox1A = QComboBox()
        self.textbox1A.addItems(['1','0'])
        self.AnalogLayout.addWidget(self.textbox1A, 2, 0)
        
        self.AnalogLayout.addWidget(QLabel("Galvo raster scanning : "), 1, 0)
        
        self.textbox1B = QComboBox()
        self.textbox1B.addItems(['-5','-3','-1'])
        self.AnalogLayout.addWidget(self.textbox1B, 1, 2)
        self.AnalogLayout.addWidget(QLabel("voltXMin"), 1, 1)

        self.textbox1C = QComboBox()
        self.textbox1C.addItems(['5','3','1'])
        self.AnalogLayout.addWidget(self.textbox1C, 2, 2)
        self.AnalogLayout.addWidget(QLabel("voltXMax"), 2, 1)

        self.textbox1D = QComboBox()
        self.textbox1D.addItems(['-5','-3','-1'])
        self.AnalogLayout.addWidget(self.textbox1D, 1, 4)
        self.AnalogLayout.addWidget(QLabel("voltYMin"), 1, 3)

        self.textbox1E = QComboBox()
        self.textbox1E.addItems(['5','3','1'])
        self.AnalogLayout.addWidget(self.textbox1E, 2, 4)
        self.AnalogLayout.addWidget(QLabel("voltYMax"), 2, 3)

        self.textbox1F = QComboBox()
        self.textbox1F.addItems(['500','256'])
        self.AnalogLayout.addWidget(self.textbox1F, 1, 6)
        self.AnalogLayout.addWidget(QLabel("X pixel number"), 1, 5)

        self.textbox1G = QComboBox()
        self.textbox1G.addItems(['500','256'])
        self.AnalogLayout.addWidget(self.textbox1G, 2, 6)
        self.AnalogLayout.addWidget(QLabel("Y pixel number"), 2, 5)
        
        self.textbox1H = QComboBox()
        self.textbox1H.addItems(['5','2','3','8','1'])
        self.AnalogLayout.addWidget(self.textbox1H, 1, 8)
        self.AnalogLayout.addWidget(QLabel("average over:"), 1, 7)

        label = QLabel(self)
        pixmap = QPixmap('f15e1.jpeg')
        label.setPixmap(pixmap)        
        self.AnalogLayout.addWidget(label, 3, 0)
        
        # 640 AO
        self.textbox2A = QComboBox()
        self.textbox2A.addItems(['0','1'])
        self.AnalogLayout.addWidget(self.textbox2A, 5, 0)
        
        self.AnalogLayout.addWidget(QLabel("640 AO : "), 4, 0)
        '''
        self.UI_Daq_sample_rate = value6
        self.UI_voltXMin_stagescan = value7
        self.UI_voltXMax_stagescan = value8
        self.UI_voltYMin_stagescan = value9
        self.UI_voltYMax_stagescan = value10
        self.UI_Value_xPixels_stagescan = value11
        self.UI_Value_yPixels_stagescan = value12
        self.UI_Value_averagenum_stagescan = value13
        self.digital_samples = value14
        '''
        AnalogContainer.setLayout(self.AnalogLayout)
        
        self.configs = Configuration()
        
        #--------------Adding to master----------------------------------------
        master = QVBoxLayout()
        master.addWidget(AnalogContainer)
        self.setLayout(master)
'''        
    def         
        Daq_sample_rate = self.UI_Daq_sample_rate
        
        #Scanning settings
        Value_voltXMin = self.UI_voltXMin_stagescan
        Value_voltXMax = self.UI_voltXMax_stagescan
        Value_voltYMin = self.UI_voltYMin_stagescan
        Value_voltYMax = self.UI_voltYMax_stagescan
        Value_xPixels = self.UI_Value_xPixels_stagescan
        Value_yPixels = self.UI_Value_yPixels_stagescan
        averagenum =self.UI_Value_averagenum_stagescan
        #Generate galvo samples
        
        samples_1, samples_2= wavegenerator.waveRecPic(sampleRate = Daq_sample_rate, imAngle = 0, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, 
                         voltYMin = Value_voltYMin, voltYMax = Value_voltYMax, xPixels = Value_xPixels, yPixels = Value_yPixels, 
                         sawtooth = True)
        #ScanArrayX = wavegenerator.xValuesSingleSawtooth(sampleRate = Daq_sample_rate, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, xPixels = Value_xPixels, sawtooth = True)
        Totalscansamples = len(samples_1)*averagenum # Calculate number of samples to feed to scanner, by default it's one frame 
        ScanArrayXnum = int (len(samples_1)/Value_yPixels) # number of samples of each individual line of x scanning
        Galvo_samples = np.vstack((samples_1,samples_2)) #
'''        
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainwin = adgenerator()
        mainwin.show()
        app.exec_()
    run_app()