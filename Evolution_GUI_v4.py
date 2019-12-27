# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 10:55:20 2019

@author: xinmeng
"""

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QDoubleSpinBox, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QPlainTextEdit, QGroupBox, QSpinBox, QFileDialog
import numpy as np
from StagescanClass_v1 import Stagescan
from matplotlib import pyplot as plt
#import pyqtgraph as pg
from IPython import get_ipython
from matplotlib.ticker import FormatStrFormatter
import Waveformer
#from adsignalsgenerator_v1 import adgenerator


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
        Layout.addWidget(self.textboxB, 0, 5)
        Layout.addWidget(QLabel("End index-row:"), 0, 4)
        
        self.textboxC = QSpinBox(self)
        self.textboxC.setMinimum(-20000)
        self.textboxC.setMaximum(20000)
        self.textboxC.setSingleStep(500)
        Layout.addWidget(self.textboxC, 0, 3)
        Layout.addWidget(QLabel("Start index-column:"), 0, 2)   
        
        self.textboxD = QSpinBox(self)
        self.textboxD.setMinimum(-20000)
        self.textboxD.setMaximum(20000)
        self.textboxD.setSingleStep(500)
        Layout.addWidget(self.textboxD, 0, 7)
        Layout.addWidget(QLabel("End index-column:"), 0, 6)      

        self.textboxE = QSpinBox(self)
        self.textboxE.setMaximum(20000)
        self.textboxE.setValue(1500)
        self.textboxE.setSingleStep(500)
        Layout.addWidget(self.textboxE, 1, 1)
        Layout.addWidget(QLabel("Step size:"), 1, 0)
        
        ScanContainer.setLayout(Layout)
        
        #----------------------------------------------------------------------
        imageprocessingContainer = QGroupBox("Image processing settings")
        ipLayout = QGridLayout()
        
        self.textboxG = QComboBox()
        self.textboxG.addItems(['200','100'])
        ipLayout.addWidget(self.textboxG, 0, 3)
        ipLayout.addWidget(QLabel("Smallest size:"), 0, 2)   
        
        self.opening_factorBox = QSpinBox(self)
        self.opening_factorBox.setMaximum(2000)
        self.opening_factorBox.setValue(2)
        self.opening_factorBox.setSingleStep(1)
        ipLayout.addWidget(self.opening_factorBox, 0, 5)
        ipLayout.addWidget(QLabel("Mask opening factor:"), 0, 4)
        
        self.closing_factorBox = QSpinBox(self)
        self.closing_factorBox.setMaximum(2000)
        self.closing_factorBox.setValue(2)
        self.closing_factorBox.setSingleStep(1)
        ipLayout.addWidget(self.closing_factorBox, 0, 7)
        ipLayout.addWidget(QLabel("Mask closing factor:"), 0, 6)   
        
        self.binary_adaptive_block_sizeBox = QSpinBox(self)
        self.binary_adaptive_block_sizeBox.setMaximum(2000)
        self.binary_adaptive_block_sizeBox.setValue(335)
        self.binary_adaptive_block_sizeBox.setSingleStep(50)
        ipLayout.addWidget(self.binary_adaptive_block_sizeBox, 1, 1)
        ipLayout.addWidget(QLabel("Adaptive mask size:"), 1, 0)
        
        self.contour_dilation_box = QSpinBox(self)
        self.contour_dilation_box.setMaximum(2000)
        self.contour_dilation_box.setValue(10)
        self.contour_dilation_box.setSingleStep(1)
        ipLayout.addWidget(self.contour_dilation_box, 1, 3)
        ipLayout.addWidget(QLabel("Contour thickness:"), 1, 2)
        
        ipLayout.addWidget(QLabel("Threshold-contour::"), 1, 4)
        self.find_contour_thres_box = QDoubleSpinBox(self)
        self.find_contour_thres_box.setDecimals(4)
        self.find_contour_thres_box.setMinimum(-10)
        self.find_contour_thres_box.setMaximum(10)
        self.find_contour_thres_box.setValue(0.001)
        self.find_contour_thres_box.setSingleStep(0.0001)  
        ipLayout.addWidget(self.find_contour_thres_box, 1, 5)
        
        self.cellopening_factorBox = QSpinBox(self)
        self.cellopening_factorBox.setMaximum(2000)
        self.cellopening_factorBox.setValue(1)
        self.cellopening_factorBox.setSingleStep(1)
        ipLayout.addWidget(self.cellopening_factorBox, 2, 1)
        ipLayout.addWidget(QLabel("Cell opening factor:"), 2, 0)
        
        self.cellclosing_factorBox = QSpinBox(self)
        self.cellclosing_factorBox.setMaximum(2000)
        self.cellclosing_factorBox.setValue(5)
        self.cellclosing_factorBox.setSingleStep(1)
        ipLayout.addWidget(self.cellclosing_factorBox, 2, 3)
        ipLayout.addWidget(QLabel("Cell closing factor:"), 2, 2)   
                
        imageprocessingContainer.setLayout(ipLayout)
        #-----------------------------------------------------------RankingContainer-------------------------------------------------
        RankingContainer = QGroupBox("Selection settings")
        rankingLayout = QGridLayout()
        
        self.selec_num_box = QSpinBox(self)
        self.selec_num_box.setMaximum(2000)
        self.selec_num_box.setValue(10)
        self.selec_num_box.setSingleStep(1)
        rankingLayout.addWidget(self.selec_num_box, 0, 1)
        rankingLayout.addWidget(QLabel("Winners number:"), 0, 0)
        
        
        RankingContainer.setLayout(rankingLayout)
        #----------------------------------------------------------------------
        
        # Create a button in the window
        overallcontainer = QGroupBox("Ready to go")
        finalLayout= QGridLayout()
        
        self.savedirectorytextbox_evolu = QtWidgets.QLineEdit(self)
        finalLayout.addWidget(self.savedirectorytextbox_evolu, 0, 0)
        self.savedirectory_evolution=''
        
        self.toolButtonOpenDialog_evolu = QtWidgets.QPushButton('Set saving dir')
        #self.toolButtonOpenDialog_evolu.setStyleSheet("QPushButton {color:teal;background-color: pink; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                                #"QPushButton:pressed {color:yellow;background-color: pink; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")

        self.toolButtonOpenDialog_evolu.setObjectName("toolButtonOpenDialog")
        self.toolButtonOpenDialog_evolu.clicked.connect(self.open_file_dialog)
        
        finalLayout.addWidget(self.toolButtonOpenDialog_evolu, 0, 1)
        
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
        master.addWidget(RankingContainer)
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
        
        textboxValue5 = int(self.textboxE.value())
        UI_step = int(textboxValue5) 
        
        textboxValue6 = int(self.selec_num_box.value())
        UI_selectnum = int(textboxValue6)

        UI_smallestsize = int(self.textboxG.currentText())    
        
        UI_openingfactor = int(self.opening_factorBox.value())
        UI_closingfactor = int(self.closing_factorBox.value())
        UI_cellopeningfactor = int(self.cellopening_factorBox.value())
        UI_cellclosingfactor = int(self.cellclosing_factorBox.value())
        UI_binary_adaptive_block_size = int(self.binary_adaptive_block_sizeBox.value())
        UI_self_findcontour_thres = float(self.find_contour_thres_box.value())
        UI_contour_dilation = int(self.contour_dilation_box.value())
        
        #------------------------------------before start, set Spyder graphic back to inline-------------------------------
        get_ipython().run_line_magic('matplotlib', 'inline') # before start, set spyder back to inline
        
        #digitalwave1 = self.analogwave # digital wave feed to start()
        #plt.plot(self.analogwave['Waveform'][1])
        #plt.show()
        print(self.readin[0])
        print(self.samplingrate)
        
        self.S = Stagescan(UI_row_start, UI_row_end, UI_column_start, UI_column_end, UI_step, self.samplingrate, self.analogwave, 
                           self.digitalwave, self.PMT_data_index_array, self.readin, UI_selectnum, UI_smallestsize, UI_openingfactor, UI_closingfactor, 
                           UI_binary_adaptive_block_size, UI_self_findcontour_thres, UI_contour_dilation, UI_cellopeningfactor,
                           UI_cellclosingfactor, self.savedirectory_evolution)
        self.S.start()


    def get_login(self):
        self.adgeneratorthread = Waveformer.WaveformGenerator()
        self.adgeneratorthread.measurement.connect(self.get_data)
        self.adgeneratorthread.show()
        # if "Generate & show" is pressed, the generated waves are fed to main program.
 
    def get_data(self, analogwave, digitalwave, PMT_data_index_array, readin, samplingrate):
            self.analogwave = analogwave
            self.digitalwave = digitalwave
            self.PMT_data_index_array = PMT_data_index_array
            self.readin = readin
            self.samplingrate = samplingrate  
            
    def open_file_dialog(self):
        self.savedirectory_evolution = str(QtWidgets.QFileDialog.getExistingDirectory())
        self.savedirectorytextbox_evolu.setText(self.savedirectory_evolution)

if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainwin = MyWindow()
        mainwin.show()
        app.exec_()
    run_app()