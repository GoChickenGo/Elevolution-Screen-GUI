# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 10:55:20 2019

@author: xinmeng
"""

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QPlainTextEdit, QGroupBox, QSpinBox
import numpy as np
from StagescanClass_v1 import Stagescan
from matplotlib import pyplot as plt
#import pyqtgraph as pg
from IPython import get_ipython
from matplotlib.ticker import FormatStrFormatter
from adsignalsgenerator_v1 import adgenerator


class MyWindow(QtWidgets.QWidget):

    def __init__(self):
        super(MyWindow, self).__init__()

        self.setWindowTitle("Evolution")

        ScanContainer = QGroupBox("Scanning settings")        
        Layout = QGridLayout() #Layout manager
        
        self.textboxA = QSpinBox(self)
        self.textboxA.setMinimum(-20000)
        self.textboxA.setMaximum(20000)
        self.textboxA.setSingleStep(500)
        Layout.addWidget(self.textboxA, 0, 1)
        Layout.addWidget(QLabel("Start index-row:"), 0, 0)
      
        self.textboxB = QSpinBox(self)
        self.textboxB.setMinimum(-20000)
        self.textboxB.setMaximum(20000)
        self.textboxB.setSingleStep(500)
        Layout.addWidget(self.textboxB, 0, 3)
        Layout.addWidget(QLabel("End index-row:"), 0, 2)
        
        self.textboxC = QSpinBox(self)
        self.textboxC.setMinimum(-20000)
        self.textboxC.setMaximum(20000)
        self.textboxC.setSingleStep(500)
        Layout.addWidget(self.textboxC, 0, 5)
        Layout.addWidget(QLabel("Start index-column:"), 0, 4)   
        
        self.textboxD = QSpinBox(self)
        self.textboxD.setMinimum(-20000)
        self.textboxD.setMaximum(20000)
        self.textboxD.setSingleStep(500)
        Layout.addWidget(self.textboxD, 0, 7)
        Layout.addWidget(QLabel("End index-column:"), 0, 6)      
        
        self.textboxE = QComboBox()
        self.textboxE.addItems(['1500','2000'])
        Layout.addWidget(self.textboxE, 1, 1)
        Layout.addWidget(QLabel("Step:"), 1, 0)
        
        ScanContainer.setLayout(Layout)
        
        #----------------------------------------------------------------------
        imageprocessingContainer = QGroupBox("Image processing settings")
        ipLayout = QGridLayout()
        
        self.textboxF = QComboBox()
        self.textboxF.addItems(['10','100'])
        ipLayout.addWidget(self.textboxF, 0, 1)
        ipLayout.addWidget(QLabel("Select number:"), 0, 0)
        
        self.textboxG = QComboBox()
        self.textboxG.addItems(['200','100'])
        ipLayout.addWidget(self.textboxG, 0, 3)
        ipLayout.addWidget(QLabel("Smallest size:"), 0, 2)        
        
        imageprocessingContainer.setLayout(ipLayout)
        
        #----------------------------------------------------------------------
        
        # Create a button in the window
        overallcontainer = QGroupBox("Ready to go")
        finalLayout= QGridLayout()
        
        self.button1 = QPushButton('Configure waveforms', self)
        finalLayout.addWidget(self.button1, 8, 0)
        
        self.button2 = QPushButton('Start', self)
        finalLayout.addWidget(self.button2, 8, 1)
        
         
        # connect button to function on_click
        self.button1.clicked.connect(self.get_login)
        self.show()
        
        self.button2.clicked.connect(self.on_click2)
        self.show()
                
        overallcontainer.setLayout(finalLayout)
        
        #--------------Adding to master----------------------------------------
        master = QVBoxLayout()
        master.addWidget(ScanContainer)
        master.addWidget(imageprocessingContainer)
        master.addWidget(overallcontainer)
        self.setLayout(master)
     
    #@pyqtSlot()
               
    #@pyqtSlot()
    def on_click2(self):

        textboxValue1 = self.textboxA.value()
        UI_row_start = int(textboxValue1)

        textboxValue2 = self.textboxB.value()
        UI_row_end = int(textboxValue2)

        textboxValue3 = self.textboxC.value()
        UI_column_start = int(textboxValue3)

        textboxValue4 = self.textboxD.value()
        UI_column_end = int(textboxValue4)
        
        textboxValue5 = self.textboxE.currentText()
        UI_step = int(textboxValue5) 
        
        textboxValue6 = self.textboxF.currentText()
        UI_selectnum = int(textboxValue6)

        UI_smallestsize = int(self.textboxG.currentText())        
        
        #------------------------------------before start, set Spyder graphic back to inline-------------------------------
        get_ipython().run_line_magic('matplotlib', 'inline') # before start, set spyder back to inline
        
        #digitalwave1 = self.analogwave # digital wave feed to start()
        #plt.plot(self.analogwave['Waveform'][1])
        #plt.show()
        print(self.readin[0])
        print(self.samplingrate)
        
        self.S = Stagescan(UI_row_start, UI_row_end, UI_column_start, UI_column_end, UI_step, self.samplingrate, self.analogwave, self.digitalwave, self.readin, UI_selectnum, UI_smallestsize)
        #self.S.start()


    def get_login(self):
        adgeneratorthread = adgenerator()
        adgeneratorthread.measurement.connect(self.get_data)
        adgeneratorthread.exec_()
        # if "OK" is pressed, the generated waves are fed to main program.
        '''
        if adgeneratorthread.exec_():
            self.analogwave = adgeneratorthread.analogcontainer_array
            self.digitalwave = adgeneratorthread.digitalcontainer_array
            self.readin = adgeneratorthread.readinchan
            self.samplingrate = int(adgeneratorthread.textboxAA.currentText())
        ''' 
    def get_data(self, analogwave, digitalwave, readin, samplingrate):
            self.analogwave = analogwave
            self.digitalwave = digitalwave
            self.readin = readin
            self.samplingrate = samplingrate  

if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainwin = MyWindow()
        mainwin.show()
        app.exec_()
    run_app()