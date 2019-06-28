# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 10:55:20 2019

@author: xinmeng
"""

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QPlainTextEdit, QGroupBox
import numpy as np
from StagescanClass import Stagescan
from matplotlib import pyplot as plt
import pyqtgraph as pg

class setADsamples(QtWidgets.QDialog):

    def __init__(self):
        super(setADsamples, self).__init__()

        #----------------------------------------------------------------------
        #----------------------------------GUI---------------------------------
        #----------------------------------------------------------------------
        self.setMinimumSize(300,120)
        self.setWindowTitle("A/D signals")
        
        #self.waveContainer = QGroupBox("Signals")
        Layout = QGridLayout() #Layout manager
        self.setLayout(Layout)
        
        self.textboxA = QComboBox()
        self.textboxA.addItems(['1','0'])
        Layout.addWidget(self.textboxA, 0, 0)
        
        self.textboxB = QPlainTextEdit(self)
        Layout.addWidget(self.textboxB, 1, 1)
        Layout.addWidget(QLabel("Frequency:"), 0, 1)

        self.textboxE = QPlainTextEdit(self)
        Layout.addWidget(self.textboxE, 1, 2)
        Layout.addWidget(QLabel("Offset (ms):"), 0, 2)
        
        self.textboxG = QPlainTextEdit(self)
        Layout.addWidget(self.textboxG, 1, 3)
        Layout.addWidget(QLabel("Period (ms):"), 0, 3)   
        
        self.textboxH = QPlainTextEdit(self)
        Layout.addWidget(self.textboxH, 1, 4)
        Layout.addWidget(QLabel("Repeat:"), 0, 4) 
        
        Layout.addWidget(QLabel("DC (%):"), 0, 5)
        self.textboxD = QComboBox()
        self.textboxD.addItems(['50','10'])
        Layout.addWidget(self.textboxD, 1, 5)
        
        
        Layout.addWidget(QLabel("Digital used line:"), 0, 6)
        self.textboxF = QComboBox()
        self.textboxF.addItems(['/Dev1/port0/line25','10'])
        Layout.addWidget(self.textboxF, 1, 6)
        
        Layout.addWidget(QLabel("Sampling rate:"), 0, 8)
        self.textboxI = QComboBox()
        self.textboxI.addItems(['500000','100000', '10'])
        Layout.addWidget(self.textboxI, 1, 8)        
        
        self.button1 = QPushButton('Generate!', self)
        Layout.addWidget(self.button1, 0, 9)
        
        self.button1.clicked.connect(self.on_click1)
        self.show()
        
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        Layout.addWidget(self.button_box, 1, 9)
        
        # 2nd digital line
        self.textboxJ = QComboBox()
        self.textboxJ.addItems(['1','0'])
        Layout.addWidget(self.textboxJ, 2, 0)
        
        self.textboxK = QPlainTextEdit(self)
        Layout.addWidget(self.textboxK, 3, 1)
        Layout.addWidget(QLabel("Frequency:"), 2, 1)

        self.textboxL = QPlainTextEdit(self)
        Layout.addWidget(self.textboxL, 3, 2)
        Layout.addWidget(QLabel("Offset (ms):"), 2, 2)
        
        self.textboxM = QPlainTextEdit(self)
        Layout.addWidget(self.textboxM, 3, 3)
        Layout.addWidget(QLabel("Period (ms):"), 2, 3)   
        
        self.textboxN = QPlainTextEdit(self)
        Layout.addWidget(self.textboxN, 3, 4)
        Layout.addWidget(QLabel("Repeat times:"), 2, 4) 
        
        Layout.addWidget(QLabel("DC (%):"), 2, 5)
        self.textboxO = QComboBox()
        self.textboxO.addItems(['50','10'])
        Layout.addWidget(self.textboxO, 3, 5)
        
        Layout.addWidget(QLabel("Digital used line:"), 2, 6)
        self.textboxP = QComboBox()
        self.textboxP.addItems(['/Dev1/port0/line24','10'])
        Layout.addWidget(self.textboxP, 3, 6)
        
        # 3rd digital line
        self.textbox3A = QComboBox()
        self.textbox3A.addItems(['1','0'])
        Layout.addWidget(self.textbox3A, 4, 0)
        
        self.textbox3B = QPlainTextEdit(self)
        Layout.addWidget(self.textbox3B, 5, 1)
        Layout.addWidget(QLabel("Frequency:"), 4, 1)

        self.textbox3C = QPlainTextEdit(self)
        Layout.addWidget(self.textbox3C, 5, 2)
        Layout.addWidget(QLabel("Offset (ms):"), 4, 2)
        
        self.textbox3D = QPlainTextEdit(self)
        Layout.addWidget(self.textbox3D, 5, 3)
        Layout.addWidget(QLabel("Period (ms):"), 4, 3)   
        
        self.textbox3E = QPlainTextEdit(self)
        Layout.addWidget(self.textbox3E, 5, 4)
        Layout.addWidget(QLabel("Repeat times:"), 4, 4) 
        
        Layout.addWidget(QLabel("DC (%):"), 4, 5)
        self.textbox3F = QComboBox()
        self.textbox3F.addItems(['50','10'])
        Layout.addWidget(self.textbox3F, 5, 5)
        
        Layout.addWidget(QLabel("Digital used line:"), 4, 6)
        self.textbox3G = QComboBox()
        self.textbox3G.addItems(['/Dev1/port0/line24','10'])
        Layout.addWidget(self.textbox3G, 5, 6)
        
        # 4th digital line
        self.textbox4A = QComboBox()
        self.textbox4A.addItems(['1','0'])
        Layout.addWidget(self.textbox4A, 6, 0)
        
        self.textbox4B = QPlainTextEdit(self)
        Layout.addWidget(self.textbox4B, 7, 1)
        Layout.addWidget(QLabel("Frequency:"), 6, 1)

        self.textbox4C = QPlainTextEdit(self)
        Layout.addWidget(self.textbox4C, 7, 2)
        Layout.addWidget(QLabel("Offset (ms):"), 6, 2)
        
        self.textbox4D = QPlainTextEdit(self)
        Layout.addWidget(self.textbox4D, 7, 3)
        Layout.addWidget(QLabel("Period (ms):"), 6, 3)   
        
        self.textbox4E = QPlainTextEdit(self)
        Layout.addWidget(self.textbox4E, 7, 4)
        Layout.addWidget(QLabel("Repeat times:"), 6, 4) 
        
        Layout.addWidget(QLabel("DC (%):"), 6, 5)
        self.textbox4F = QComboBox()
        self.textbox4F.addItems(['50','10'])
        Layout.addWidget(self.textbox4F, 7, 5)
        
        Layout.addWidget(QLabel("Digital used line:"), 6, 6)
        self.textbox4G = QComboBox()
        self.textbox4G.addItems(['/Dev1/port0/line24','10'])
        Layout.addWidget(self.textbox4G, 7, 6)        
        
        #self.waveContainer.setLayout(Layout)
        
        #----------------------------Plot window-----------------------------------
        
        #plotContainer = QGroupBox("Output")
        #self.plotLayout = QVBoxLayout()
        
        #self.my_plot = pg.PlotWidget()
        #self.my_plot.setYRange(0, 1)
        #self.my_plot.setWindowTitle('Digital signal plots')
        #self.plotLayout.addWidget(self.my_plot)
        
        #self.setLayout(self.plotLayout)
        #my_plot.plot(x, y)
        #Layout.addWidget(self.plotWidget, 8, 0)
        
        
    def on_click1(self):
        
        # generate wave
        self.samplingrate_1 = int(self.textboxI.currentText()) # samples per second
        
        #textboxValue1 = self.textboxA.currentText()
        
        self.wavefrequency_1 = int(self.textboxB.toPlainText())
        self.waveoffset_1 = int(self.textboxE.toPlainText()) # in ms
        self.waveperiod_1 = int(self.textboxG.toPlainText())
        self.waveDC_1 = int(self.textboxD.currentText())
        self.waverepeat_1 = int(self.textboxH.toPlainText())
        
        #self.wave = np.array([textboxValue1])
        
        self.offsetsamples_number_1 = int(1 + (self.waveoffset_1/1000)*self.samplingrate_1) # By default one 0 is added so that we have a rising edge at the beginning.
        self.offsetsamples_1 = np.zeros(self.offsetsamples_number_1, dtype=bool) # Be default offsetsamples_number is an integer.
        
        self.sample_num_singleperiod_1 = round((int((self.waveperiod_1/1000)*self.samplingrate_1))/self.wavefrequency_1)
        self.true_sample_num_singleperiod_1 = round((self.waveDC_1/100)*self.sample_num_singleperiod_1)
        self.false_sample_num_singleperiod_1 = self.sample_num_singleperiod_1 - self.true_sample_num_singleperiod_1
        
        self.sample_singleperiod_1 = np.append(np.ones(self.true_sample_num_singleperiod_1,dtype=bool), np.zeros(self.false_sample_num_singleperiod_1,dtype=bool))
        
        self.repeatnumberintotal_1 = self.wavefrequency_1*(self.waveperiod_1/1000)*self.waverepeat_1
        
        if self.repeatnumberintotal_1 >= 1:
            self.wave_1 = np.tile(self.sample_singleperiod_1, int(self.repeatnumberintotal_1))
        else:
            self.partial_numb_1 = int(self.repeatnumberintotal_1*self.sample_num_singleperiod_1)
            self.wave_1 = self.sample_singleperiod_1[0:self.partial_numb_1]
            
        self.final_wave_1 = np.append(self.offsetsamples_1, self.wave_1)
        
        #self.my_plot.plot(range(len(self.final_wave_1)), self.final_wave_1)
        pg.plot(range(len(self.final_wave_1)), self.final_wave_1, pen=None, symbol='o')
        
class MyWindow(QtWidgets.QWidget):

    def __init__(self):
        super(MyWindow, self).__init__()

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
        self.textboxF.addItems(['500000', '50000'])
        Layout.addWidget(self.textboxF, 2, 3)
        Layout.addWidget(QLabel("DAQ sampling rate:"), 2, 2)         

        self.textboxG = QComboBox()
        self.textboxG.addItems(['-5','-3','-1'])
        Layout.addWidget(self.textboxG, 3, 1)
        Layout.addWidget(QLabel("voltXMin"), 3, 0)

        self.textboxH = QComboBox()
        self.textboxH.addItems(['5','3','1'])
        Layout.addWidget(self.textboxH, 3, 3)
        Layout.addWidget(QLabel("voltXMax"), 3, 2)

        self.textboxI = QComboBox()
        self.textboxI.addItems(['-5','-3','-1'])
        Layout.addWidget(self.textboxI, 4, 1)
        Layout.addWidget(QLabel("voltYMin"), 4, 0)

        self.textboxJ = QComboBox()
        self.textboxJ.addItems(['5','3','1'])
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
        
        self.textboxM = QComboBox()
        self.textboxM.addItems(['5','2','3','8','1'])
        Layout.addWidget(self.textboxM, 6, 1)
        Layout.addWidget(QLabel("average over:"), 6, 0)

        # Create a button in the window
        self.button1 = QPushButton('Feed AD signals', self)
        Layout.addWidget(self.button1, 8, 0)
        
        self.button2 = QPushButton('Start', self)
        Layout.addWidget(self.button2, 8, 1)
        
         
        # connect button to function on_click
        self.button1.clicked.connect(self.get_login)
        self.show()
        
        self.button2.clicked.connect(self.on_click2)
        self.show()
                
        self.wave = []
     
    #@pyqtSlot()
               
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
        
        textboxValue13 = self.textboxM.currentText()
        UI_averagenum = int(textboxValue13)
        
        digitalwave1 = self.wave1 # digital wave feed to start()
        plt.plot(digitalwave1)
        plt.show()
        
        #self.S = Stagescan(UI_row_start, UI_row_end, UI_column_start, UI_column_end, UI_step, UI_Daq_sample_rate, UI_voltXMin, UI_voltXMax, UI_voltYMin, UI_voltYMax, UI_Value_xPixels, UI_Value_yPixels, UI_averagenum)
        #self.S.start()


    def get_login(self):
        login = setADsamples()
        if login.exec_():
            self.wave1 = login.final_wave_1
            #self.edit.setText(login.password.text())
            plt.plot(self.wave1)
            plt.show()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())