# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 19:52:48 2019

@author: Meng
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
        
        self.button1 = QPushButton('Generate!', self)
        self.AnalogLayout.addWidget(self.button1, 2, 8)
        
        self.button1.clicked.connect(self.generate_galvos) 

        label = QLabel(self)
        pixmap = QPixmap('f15e.jpeg')
        label.setPixmap(pixmap)        
        self.AnalogLayout.addWidget(label, 3, 0)
        
        # 640 AO
        self.textbox2A = QComboBox()
        self.textbox2A.addItems(['1','0'])
        self.AnalogLayout.addWidget(self.textbox2A, 5, 0)
        
        self.AnalogLayout.addWidget(QLabel("640 AO : "), 4, 0)
        
        self.textbox2B = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox2B, 4, 2)
        self.AnalogLayout.addWidget(QLabel("Frequency:"), 4, 1)

        self.textbox2C = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox2C, 5, 2)
        self.AnalogLayout.addWidget(QLabel("Offset (ms):"), 5, 1)
        
        self.textbox2D = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox2D, 4, 4)
        self.AnalogLayout.addWidget(QLabel("Period (ms, 1 cycle):"), 4, 3)   
        
        self.textbox2E = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox2E, 5, 4)
        self.AnalogLayout.addWidget(QLabel("Repeat:"), 5, 3) 
        
        self.AnalogLayout.addWidget(QLabel("DC (%):"), 4, 5)
        self.textbox2F = QComboBox()
        self.textbox2F.addItems(['50','10'])
        self.AnalogLayout.addWidget(self.textbox2F, 4, 6)
        
        self.textbox2G = QPlainTextEdit(self)
        self.textbox2G.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox2G, 5, 6)
        self.AnalogLayout.addWidget(QLabel("Gap between repeat (ms):"), 5, 5)
        
        self.AnalogLayout.addWidget(QLabel("Starting amplitude (V)"), 4, 7)
        self.textbox2H = QComboBox()
        self.textbox2H.addItems(['5','1'])
        self.AnalogLayout.addWidget(self.textbox2H, 4, 8)        

        self.textbox2I = QPlainTextEdit(self)
        self.textbox2I.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox2I, 5, 8)
        self.AnalogLayout.addWidget(QLabel("Baseline (V):"), 5, 7)

        self.AnalogLayout.addWidget(QLabel("Step (V)"), 4, 9)
        self.textbox2J = QComboBox()
        self.textbox2J.addItems(['0','1', '2'])
        self.AnalogLayout.addWidget(self.textbox2J, 4, 10)

        self.AnalogLayout.addWidget(QLabel("Cycles"), 5, 9)
        self.textbox2K = QComboBox()
        self.textbox2K.addItems(['1','2', '3'])
        self.AnalogLayout.addWidget(self.textbox2K, 5, 10)
        
        self.button2 = QPushButton('Generate!', self)
        self.AnalogLayout.addWidget(self.button2, 4, 11)
        
        self.button2.clicked.connect(self.generate_640AO)
        
        # --------------------------------------------------------488 AO--------------------------------------------------------
        self.textbox3A = QComboBox()
        self.textbox3A.addItems(['0','1'])
        self.AnalogLayout.addWidget(self.textbox3A, 7, 0)
        
        self.AnalogLayout.addWidget(QLabel("488 AO : "), 6, 0)
        
        self.textbox3B = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox3B, 6, 2)
        self.AnalogLayout.addWidget(QLabel("Frequency:"), 6, 1)

        self.textbox3C = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox3C, 7, 2)
        self.AnalogLayout.addWidget(QLabel("Offset (ms):"), 7, 1)
        
        self.textbox3D = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox3D, 6, 4)
        self.AnalogLayout.addWidget(QLabel("Period (ms):"), 6, 3)   
        
        self.textbox3E = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox3E, 7, 4)
        self.AnalogLayout.addWidget(QLabel("Repeat:"), 7, 3) 
        
        self.AnalogLayout.addWidget(QLabel("DC (%):"), 6, 5)
        self.textbox3F = QComboBox()
        self.textbox3F.addItems(['50','10'])
        self.AnalogLayout.addWidget(self.textbox3F, 6, 6)
        
        # 532 AO
        self.textbox4A = QComboBox()
        self.textbox4A.addItems(['0','1'])
        self.AnalogLayout.addWidget(self.textbox4A, 9, 0)
        
        self.AnalogLayout.addWidget(QLabel("532 AO : "), 8, 0)
        
        self.textbox4B = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox4B, 8, 2)
        self.AnalogLayout.addWidget(QLabel("Frequency:"), 8, 1)

        self.textbox4C = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox4C, 9, 2)
        self.AnalogLayout.addWidget(QLabel("Offset (ms):"), 9, 1)
        
        self.textbox4D = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox4D, 8, 4)
        self.AnalogLayout.addWidget(QLabel("Period (ms):"), 8, 3)   
        
        self.textbox4E = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox4E, 9, 4)
        self.AnalogLayout.addWidget(QLabel("Repeat:"), 9, 3) 
        
        self.AnalogLayout.addWidget(QLabel("DC (%):"), 8, 5)
        self.textbox4F = QComboBox()
        self.textbox4F.addItems(['50','10'])
        self.AnalogLayout.addWidget(self.textbox4F, 8, 6)
        
        AnalogContainer.setLayout(self.AnalogLayout)
        
        #----------------------------------------------------------------------
        #----------------------------------Digital---------------------------------
        #----------------------------------------------------------------------       
        DigitalContainer = QGroupBox("Digital signals")
        self.DigitalLayout = QGridLayout() #self.AnalogLayout manager
        
        # Camera triggering
        self.textbox11A = QComboBox()
        self.textbox11A.addItems(['0','1'])
        self.DigitalLayout.addWidget(self.textbox11A, 1, 0)
        
        self.DigitalLayout.addWidget(QLabel("Camera triggering : "), 0, 0)
        
        self.textbox11B = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox11B, 0, 2)
        self.DigitalLayout.addWidget(QLabel("Frequency:"), 0, 1)

        self.textbox11C = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox11C, 1, 2)
        self.DigitalLayout.addWidget(QLabel("Offset (ms):"), 1, 1)
        
        self.textbox11D = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox11D, 0, 4)
        self.DigitalLayout.addWidget(QLabel("Period (ms):"), 0, 3)   
        
        self.textbox11E = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox11E, 1, 4)
        self.DigitalLayout.addWidget(QLabel("Repeat:"), 1, 3) 
        
        self.DigitalLayout.addWidget(QLabel("DC (%):"), 0, 5)
        self.textbox11F = QComboBox()
        self.textbox11F.addItems(['50','10'])
        self.DigitalLayout.addWidget(self.textbox11F, 0, 6)
        
        # 640 blanking
        self.textbox22A = QComboBox()
        self.textbox22A.addItems(['0','1'])
        self.DigitalLayout.addWidget(self.textbox22A, 3, 0)
        
        self.DigitalLayout.addWidget(QLabel("640 blanking : "), 2, 0)
        
        self.textbox22B = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox22B, 2, 2)
        self.DigitalLayout.addWidget(QLabel("Frequency:"), 2, 1)

        self.textbox22C = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox22C, 3, 2)
        self.DigitalLayout.addWidget(QLabel("Offset (ms):"), 3, 1)
        
        self.textbox22D = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox22D, 2, 4)
        self.DigitalLayout.addWidget(QLabel("Period (ms):"), 2, 3)   
        
        self.textbox22E = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox22E, 3, 4)
        self.DigitalLayout.addWidget(QLabel("Repeat:"), 3, 3) 
        
        self.DigitalLayout.addWidget(QLabel("DC (%):"), 2, 5)
        self.textbox22F = QComboBox()
        self.textbox22F.addItems(['50','10'])
        self.DigitalLayout.addWidget(self.textbox22F, 2, 6)        
        
        # 532 blanking
        self.textbox33A = QComboBox()
        self.textbox33A.addItems(['0','1'])
        self.DigitalLayout.addWidget(self.textbox33A, 5, 0)
        
        self.DigitalLayout.addWidget(QLabel("532 blanking : "), 4, 0)
        
        self.textbox33B = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox33B, 4, 2)
        self.DigitalLayout.addWidget(QLabel("Frequency:"), 4, 1)

        self.textbox33C = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox33C, 5, 2)
        self.DigitalLayout.addWidget(QLabel("Offset (ms):"), 5, 1)
        
        self.textbox33D = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox33D, 4, 4)
        self.DigitalLayout.addWidget(QLabel("Period (ms):"), 4, 3)   
        
        self.textbox33E = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox33E, 5, 4)
        self.DigitalLayout.addWidget(QLabel("Repeat:"), 5, 3) 
        
        self.DigitalLayout.addWidget(QLabel("DC (%):"), 4, 5)
        self.textbox33F = QComboBox()
        self.textbox33F.addItems(['50','10'])
        self.DigitalLayout.addWidget(self.textbox33F, 4, 6) 
        
        # 488 blanking
        self.textbox44A = QComboBox()
        self.textbox44A.addItems(['0','1'])
        self.DigitalLayout.addWidget(self.textbox44A, 7, 0)
        
        self.DigitalLayout.addWidget(QLabel("488 blanking : "), 6, 0)
        
        self.textbox44B = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox44B, 6, 2)
        self.DigitalLayout.addWidget(QLabel("Frequency:"), 6, 1)

        self.textbox44C = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox44C, 7, 2)
        self.DigitalLayout.addWidget(QLabel("Offset (ms):"), 7, 1)
        
        self.textbox44D = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox44D, 6, 4)
        self.DigitalLayout.addWidget(QLabel("Period (ms):"), 6, 3)   
        
        self.textbox44E = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox44E, 7, 4)
        self.DigitalLayout.addWidget(QLabel("Repeat:"), 7, 3) 
        
        self.DigitalLayout.addWidget(QLabel("DC (%):"), 6, 5)
        self.textbox44F = QComboBox()
        self.textbox44F.addItems(['50','10'])
        self.DigitalLayout.addWidget(self.textbox44F, 6, 6)        
        
        
        
        DigitalContainer.setLayout(self.DigitalLayout)


        
        self.configs = Configuration()
        
        #--------------Adding to master----------------------------------------
        master = QVBoxLayout()
        master.addWidget(AnalogContainer)
        master.addWidget(DigitalContainer)
        self.setLayout(master)
        
        if not self.textbox2G.toPlainText(): # if blank then set the value 0
            self.gap2 = 0
        else:
            self.gap2 = self.textbox2G.toPlainText()
            
            
    def generate_galvos(self):
        
        Daq_sample_rate = int(self.textboxAA.currentText())
        
        #Scanning settings
        if int(self.textbox1A.currentText()) == 1:
            Value_voltXMin = int(self.textbox1B.currentText())
            Value_voltXMax = int(self.textbox1C.currentText())
            Value_voltYMin = int(self.textbox1D.currentText())
            Value_voltYMax = int(self.textbox1E.currentText())
            Value_xPixels = int(self.textbox1F.currentText())
            Value_yPixels = int(self.textbox1G.currentText())
            averagenum =int(self.textbox1H.currentText())
            #Generate galvo samples
            
            samples_1, samples_2= wavegenerator.waveRecPic(sampleRate = Daq_sample_rate, imAngle = 0, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, 
                             voltYMin = Value_voltYMin, voltYMax = Value_voltYMax, xPixels = Value_xPixels, yPixels = Value_yPixels, 
                             sawtooth = True)
            #ScanArrayX = wavegenerator.xValuesSingleSawtooth(sampleRate = Daq_sample_rate, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, xPixels = Value_xPixels, sawtooth = True)
            Totalscansamples = len(samples_1)*averagenum # Calculate number of samples to feed to scanner, by default it's one frame 
            ScanArrayXnum = int (len(samples_1)/Value_yPixels) # number of samples of each individual line of x scanning
            Galvo_samples = np.vstack((samples_1,samples_2))
            
    def generate_640AO(self):
        Daq_sample_rate = int(self.textboxAA.currentText())

        if int(self.textbox2A.currentText()) == 1:
            self.wavefrequency_2 = int(self.textbox2B.toPlainText())
            self.waveoffset_2 = int(self.textbox2C.toPlainText()) # in ms
            self.waveperiod_2 = int(self.textbox2D.toPlainText())
            self.waveDC_2 = int(self.textbox2F.currentText())
            self.waverepeat_2 = int(self.textbox2E.toPlainText())
            self.wavegap_2 = int(self.textbox2G.toPlainText())
            self.wavestartamplitude_2 = int(self.textbox2H.currentText())
            self.wavebaseline_2 = int(self.textbox2I.toPlainText())
            self.wavestep_2 = int(self.textbox2J.currentText())
            self.wavecycles_2 = int(self.textbox2K.currentText())
            
            self.offsetsamples_number_2 = int(1 + (self.waveoffset_2/1000)*Daq_sample_rate) # By default one 0 is added so that we have a rising edge at the beginning.
            self.offsetsamples_2 = self.wavebaseline_2 * np.ones(self.offsetsamples_number_2) # Be default offsetsamples_number is an integer.
            
            self.sample_num_singleperiod_2 = round((int((self.waveperiod_2/1000)*Daq_sample_rate))/self.wavefrequency_2)
            self.true_sample_num_singleperiod_2 = round((self.waveDC_2/100)*self.sample_num_singleperiod_2)
            self.false_sample_num_singleperiod_2 = self.sample_num_singleperiod_2 - self.true_sample_num_singleperiod_2
            
            self.sample_singleperiod_2 = np.append(self.wavestartamplitude_2 * np.ones(self.true_sample_num_singleperiod_2), self.wavebaseline_2 * np.ones(self.false_sample_num_singleperiod_2))
            self.repeatnumberintotal_2 = self.wavefrequency_2*(self.waveperiod_2/1000)
            # In default, pulses * sample_singleperiod_2 = period
            self.sample_singlecycle_2 = np.tile(self.sample_singleperiod_2, int(self.repeatnumberintotal_2))
            
            self.waveallcycle_2 = []
            # Adding steps to cycles
            for i in range(self.wavecycles_2):
                cycle_roof_value = self.wavestep_2 * i
                self.cycleappend = np.where(self.sample_singlecycle_2 < self.wavestartamplitude_2, self.wavebaseline_2, self.wavestartamplitude_2 + cycle_roof_value)
                self.waveallcycle_2 = np.append(self.waveallcycle_2, self.cycleappend)
            
            
            
            plt.plot(self.waveallcycle_2)
            plt.show()
            
        
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainwin = adgenerator()
        mainwin.show()
        app.exec_()
    run_app()