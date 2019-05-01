# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 22:29:17 2019

@author: Meng
"""

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QPlainTextEdit, QGridLayout, QLabel, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
#from stagescan_v3_UIclass import Stagescan
import time
from Stage import Stage
import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType, TaskMode
from nidaqmx.stream_writers import AnalogMultiChannelWriter, DigitalMultiChannelWriter
from nidaqmx.stream_readers import AnalogSingleChannelReader
import wavegenerator
import matplotlib.pyplot as plt
 
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        #self.setMinimumSize(480,640)
        self.setWindowTitle("Revolution")
        
        #SettingsContainer = QGroupBox("Settings for scanning index") #Containter containing Non-DAQ ports
        #self.setGeometry(self.left, self.top, self.width, self.height)
        
        # Create label
        Layout = QGridLayout() #Layout manager
        self.setLayout(Layout)
        #SettingsContainer.setLayout(self.Layout)
        
        self.textboxA = QPlainTextEdit(self)
        Layout.addWidget(self.textboxA, 0, 1)
        Layout.addWidget(QLabel("Start index-row:"), 0, 0)
      
        self.textboxB = QPlainTextEdit(self)
        Layout.addWidget(self.textboxB, 0, 3)
        Layout.addWidget(QLabel("End index-row:"), 0, 2)
        
        self.textboxC = QPlainTextEdit(self)
        Layout.addWidget(self.textboxC, 1, 1)
        Layout.addWidget(QLabel("Start index-column:"), 1, 0)   
        
        self.textboxD = QPlainTextEdit(self)
        Layout.addWidget(self.textboxD, 1, 3)
        Layout.addWidget(QLabel("Start index-column:"), 1, 2)      
        
        self.textboxE = QComboBox()
        self.textboxE.addItems(['1500','2000'])
        Layout.addWidget(self.textboxE, 2, 1)
        Layout.addWidget(QLabel("Step:"), 2, 0)          

        self.textboxF = QComboBox()
        self.textboxF.addItems(['50000', '500000'])
        Layout.addWidget(self.textboxF, 2, 3)
        Layout.addWidget(QLabel("DAQ sampling rate:"), 2, 2)         

        self.textboxG = QComboBox()
        self.textboxG.addItems(['-3','-2','-1'])
        Layout.addWidget(self.textboxG, 3, 1)
        Layout.addWidget(QLabel("voltXMin"), 3, 0)

        self.textboxH = QComboBox()
        self.textboxH.addItems(['3','2','1'])
        Layout.addWidget(self.textboxH, 3, 3)
        Layout.addWidget(QLabel("voltXMax"), 3, 2)

        self.textboxI = QComboBox()
        self.textboxI.addItems(['-3','-2','-1'])
        Layout.addWidget(self.textboxI, 4, 1)
        Layout.addWidget(QLabel("voltYMin"), 4, 0)

        self.textboxJ = QComboBox()
        self.textboxJ.addItems(['3','2','1'])
        Layout.addWidget(self.textboxJ, 4, 3)
        Layout.addWidget(QLabel("voltYMax"), 4, 2)

        self.textboxK = QComboBox()
        self.textboxK.addItems(['500','256'])
        Layout.addWidget(self.textboxK, 5, 1)
        Layout.addWidget(QLabel("X pixel number"), 5, 0)

        self.textboxL = QComboBox()
        self.textboxL.addItems(['500','256'])
        Layout.addWidget(self.textboxL, 5, 3)
        Layout.addWidget(QLabel("Y pixel number"), 5, 2)

        # Create a button in the window
        self.button1 = QPushButton('Show text', self)
        Layout.addWidget(self.button1, 6, 0)
        
        self.button2 = QPushButton('Start', self)
        Layout.addWidget(self.button2, 6, 1)
        
         
        # connect button to function on_click
        self.button1.clicked.connect(self.on_click1)
        self.show()
        
        self.button2.clicked.connect(self.on_click2)
        self.show()
     
    #@pyqtSlot()
    def on_click1(self):
        textboxValue1 = self.textboxA.toPlainText()
        QMessageBox.question(self, 'Message - pythonspot.com', "You typed: " + textboxValue1, QMessageBox.Ok, QMessageBox.Ok)
        self.textboxA.setPlainText("")
               
    #@pyqtSlot()
    def on_click2(self):

        textboxValue1 = self.textboxA.toPlainText()
        UI_row_start = int(textboxValue1)

        textboxValue2 = self.textboxB.toPlainText()
        UI_row_end = int(textboxValue2)

        textboxValue3 = self.textboxC.toPlainText()
        UI_column_start = int(textboxValue3)

        textboxValue4 = self.textboxD.toPlainText()
        UI_column_end = int(textboxValue4)
        
        textboxValue5 = self.textboxE.currentText()
        UI_step = int(textboxValue5) 

        textboxValue6 = self.textboxF.currentText()
        UI_Daq_sample_rate = int(textboxValue6)

        textboxValue7 = self.textboxG.currentText()
        UI_voltXMin = int(textboxValue7)

        textboxValue8 = self.textboxH.currentText()
        UI_voltXMax = int(textboxValue8)

        textboxValue9 = self.textboxI.currentText()
        UI_voltYMin = int(textboxValue9)

        textboxValue10 = self.textboxJ.currentText()
        UI_voltYMax = int(textboxValue10)

        textboxValue11 = self.textboxK.currentText()
        UI_Value_xPixels = int(textboxValue11)

        textboxValue12 = self.textboxL.currentText()
        UI_Value_yPixels = int(textboxValue12)
        
        self.S = Stagescan(UI_row_start, UI_row_end, UI_column_start, UI_column_end, UI_step, UI_Daq_sample_rate, UI_voltXMin, UI_voltXMax, UI_voltYMin, UI_voltYMax, UI_Value_xPixels, UI_Value_yPixels)
        self.S.start()
        
class Stagescan():
    def __init__(self, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11, value12):
        # Settings for stage scan
        self.ludlStage = Stage("COM7")
        self.UI_row_start_stagescan = value1
        self.UI_row_end_stagescan = value2
        self.UI_column_start_stagescan = value3
        self.UI_column_end_stagescan = value4
        self.UI_step_stagescan = value5
        self.UI_Daq_sample_rate_stagescan = value6
        self.UI_voltXMin_stagescan = value7
        self.UI_voltXMax_stagescan = value8
        self.UI_voltYMin_stagescan = value9
        self.UI_voltYMax_stagescan = value10
        self.UI_Value_xPixels_stagescan = value11
        self.UI_Value_yPixels_stagescan = value12
        
    def start(self):
        # settings for scanning index
        position_index=[]
        row_start = self.UI_row_start_stagescan #position index start number
        row_end = self.UI_row_end_stagescan #end number
        
        column_start = self.UI_column_start_stagescan
        column_end = self.UI_column_end_stagescan
        
        step = self.UI_step_stagescan #length of each step, 1500 for -5~5V FOV
        
        #Settings for A/D output
        Daq_sample_rate = self.UI_Daq_sample_rate_stagescan
        
        #Scanning settings
        Value_voltXMin = self.UI_voltXMin_stagescan
        Value_voltXMax = self.UI_voltXMax_stagescan
        Value_voltYMin = self.UI_voltYMin_stagescan
        Value_voltYMax = self.UI_voltYMax_stagescan
        Value_xPixels = self.UI_Value_xPixels_stagescan
        Value_yPixels = self.UI_Value_yPixels_stagescan
        #Generate galvo samples
        samples_1, samples_2= wavegenerator.waveRecPic(sampleRate = Daq_sample_rate, imAngle = 0, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, 
                         voltYMin = Value_voltYMin, voltYMax = Value_voltYMax, xPixels = Value_xPixels, yPixels = Value_yPixels, 
                         sawtooth = True)
        #ScanArrayX = wavegenerator.xValuesSingleSawtooth(sampleRate = Daq_sample_rate, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, xPixels = Value_xPixels, sawtooth = True)
        Totalscansamples = len(samples_1) # Calculate number of samples to feed to scanner, by default it's one frame 
        ScanArrayXnum = int (len(samples_1)/Value_yPixels)
        Galvo_samples = np.vstack((samples_1,samples_2))
        
            
            
        #generate dig samples
        One_Dig_samples = np.append(np.ones(25000,dtype=bool), np.zeros(25000,dtype=bool))
        Dig_repeat_times = int(Totalscansamples/len(One_Dig_samples))
        Dig_samples = []
        for i in range(Dig_repeat_times):
            Dig_samples = np.append(Dig_samples, One_Dig_samples)
            
        Dataholder = np.zeros(Totalscansamples)
        
        
        
        with nidaqmx.Task() as slave_Task3, nidaqmx.Task() as master_Task, nidaqmx.Task() as slave_Task2:
            #slave_Task3 = nidaqmx.Task()
            slave_Task3.ao_channels.add_ao_voltage_chan("/Dev1/ao0:1")
            master_Task.ai_channels.add_ai_voltage_chan("/Dev1/ai0")
            slave_Task2.do_channels.add_do_chan("/Dev1/port0/line25")
            
            #slave_Task3.ao_channels.add_ao_voltage_chan("/Dev1/ao1")
            # MultiAnalogchannels
            slave_Task3.timing.cfg_samp_clk_timing(Daq_sample_rate, source='ai/SampleClock', sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamples)
            slave_Task3.triggers.sync_type.SLAVE = True
            
            # Analoginput
            master_Task.timing.cfg_samp_clk_timing(Daq_sample_rate, sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamples)
            master_Task.triggers.sync_type.MASTER = True
            
            # Digital output
            slave_Task2.timing.cfg_samp_clk_timing(Daq_sample_rate, source='ai/SampleClock', sample_mode= AcquisitionType.FINITE, samps_per_chan=Totalscansamples)
            slave_Task2.triggers.sync_type.SLAVE = True
            
            AnalogWriter = nidaqmx.stream_writers.AnalogMultiChannelWriter(slave_Task3.out_stream, auto_start= False)
            AnalogWriter.auto_start = False
            DigitalWriter = nidaqmx.stream_writers.DigitalSingleChannelWriter(slave_Task2.out_stream, auto_start= False)
            DigitalWriter.auto_start = False
            reader = AnalogSingleChannelReader(master_Task.in_stream)
                
            time.sleep(2)
            
            loopnum = 0
        
            for i in range(row_start, row_end, step):
                position_index.append(i)
                for j in range(column_start, column_end, step):
                    position_index.append(j)
                    print ('-----------------------------------')
                    print (position_index)
                    
                    #stage movement
                    self.ludlStage.MoveAbs(i,j)
                    time.sleep(1)
                    
                    AnalogWriter .write_many_sample(Galvo_samples, timeout=16.0)
                    DigitalWriter.write_one_sample_one_line(Dig_samples, timeout=16.0)
                    
                    slave_Task3.start()
                    slave_Task2.start()
                    reader.read_many_sample(Dataholder, number_of_samples_per_channel =  Totalscansamples, timeout=16.0)
                    data1 = np.reshape(Dataholder, (Value_yPixels, ScanArrayXnum))
                    
                    slave_Task3.wait_until_done()
                    slave_Task2.wait_until_done()
                    master_Task.wait_until_done()
                    
                    data2 = data1[:,:Value_yPixels]*-1
                    plt.figure(loopnum)
                    plt.imshow(data2, cmap = plt.cm.gray)
                    plt.show()
                    
                    
                    slave_Task3.stop()
                    master_Task.stop()
                    slave_Task2.stop()
                    
                    time.sleep(1)
                   
                    self.ludlStage.GetPos()
                    loopnum = loopnum+1
                    
                    
                    del position_index[-1]
                    print ('---------------^^^^---------------')
                position_index=[]
            print ('Finish')
    
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainWin = MainWindow()
        mainWin.show()
        app.exec_()
    run_app()