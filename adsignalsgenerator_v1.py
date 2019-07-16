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
from generalDaqer import execute
from configuration import Configuration
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QPlainTextEdit, QGroupBox
from adfunctiongenerator import generate_AO_for640, generate_AO_for488, generate_DO_forcameratrigger, generate_DO_for640blanking, generate_AO_for532, generate_AO_forpatch, generate_DO_forblankingall, generate_DO_for532blanking, generate_DO_for488blanking

class adgenerator(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(adgenerator, self).__init__(*args, **kwargs)
        get_ipython().run_line_magic('matplotlib', 'qt') # before start, set spyder back to inline
        #----------------------------------------------------------------------
        #----------------------------------GUI---------------------------------
        #----------------------------------------------------------------------
        self.setMinimumSize(300,120)
        self.setWindowTitle("Buon appetito!")
        
        AnalogContainer = QGroupBox("Analog signals")
        self.AnalogLayout = QGridLayout() #self.AnalogLayout manager
               
        self.textboxBB = QComboBox()
        self.textboxBB.addItems(['galvos', '640AO', '488AO', '532AO', 'patchAO'])
        self.AnalogLayout.addWidget(self.textboxBB, 0, 8)
        self.AnalogLayout.addWidget(QLabel("Reference waveform:"), 0, 7)

        self.button_all = QPushButton('SHOW ALL', self)
        self.AnalogLayout.addWidget(self.button_all, 0, 11)
        
        self.button_all.clicked.connect(self.show_all)
        
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
        
        self.textbox1I = QPlainTextEdit(self)
        self.textbox1I.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox1I, 1, 8)
        self.AnalogLayout.addWidget(QLabel("Offset (ms):"), 1, 7)
        
        self.textbox1J = QPlainTextEdit(self)
        self.textbox1J.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox1J, 2, 8)
        self.AnalogLayout.addWidget(QLabel("Gap between scans:"), 2, 7)       
        
        self.textbox1H = QComboBox()
        self.textbox1H.addItems(['5','2','3','8','1'])
        self.AnalogLayout.addWidget(self.textbox1H, 1, 10)
        self.AnalogLayout.addWidget(QLabel("average over:"), 1, 9)
        
        self.button1 = QPushButton('SHOW WAVE', self)
        self.AnalogLayout.addWidget(self.button1, 2, 9)
        
        self.button1.clicked.connect(self.generate_galvos)
        self.button1.clicked.connect(self.generate_galvos_graphy)
        
        self.button_triggerforcam = QPushButton('With trigger!', self)
        self.AnalogLayout.addWidget(self.button_triggerforcam, 2, 10)
        
        self.textbox1K = QComboBox()
        self.textbox1K.addItems(['0','1'])
        self.AnalogLayout.addWidget(self.textbox1K, 2, 11)
        
        self.button_triggerforcam.clicked.connect(self.generate_galvotrigger)        
        self.button_triggerforcam.clicked.connect(self.generate_galvotrigger_graphy)
        
        label = QLabel(self)
        pixmap = QPixmap('f15e.jpeg')
        label.setPixmap(pixmap)        
        self.AnalogLayout.addWidget(label, 3, 0)
        
        # ------------------------------------------------------640 AO-----------------------------------------------------------
        self.textbox2A = QComboBox()
        self.textbox2A.addItems(['1','0'])
        self.AnalogLayout.addWidget(self.textbox2A, 5, 0)
        
        self.AnalogLayout.addWidget(QLabel("640 AO : "), 4, 0)
        
        self.textbox2B = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox2B, 4, 2)
        self.AnalogLayout.addWidget(QLabel("Frequency in period:"), 4, 1)

        self.textbox2C = QPlainTextEdit(self)
        self.textbox2C.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox2C, 5, 2)
        self.AnalogLayout.addWidget(QLabel("Offset (ms):"), 5, 1)
        
        self.textbox2D = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox2D, 4, 4)
        self.AnalogLayout.addWidget(QLabel("Period (ms, 1 cycle):"), 4, 3)   
        
        self.textbox2E = QPlainTextEdit(self)
        self.textbox2E.setPlaceholderText('1')
        self.AnalogLayout.addWidget(self.textbox2E, 5, 4)
        self.AnalogLayout.addWidget(QLabel("Repeat:"), 5, 3) 
        
        self.AnalogLayout.addWidget(QLabel("DC (%):"), 4, 5)
        self.textbox2F = QComboBox()
        self.textbox2F.addItems(['50','10'])
        self.AnalogLayout.addWidget(self.textbox2F, 4, 6)
        
        self.textbox2G = QPlainTextEdit(self)
        self.textbox2G.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox2G, 5, 6)
        self.AnalogLayout.addWidget(QLabel("Gap between repeat (samples):"), 5, 5)
        
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
        
        self.button2 = QPushButton('SHOW WAVE', self)
        self.AnalogLayout.addWidget(self.button2, 4, 11)
        
        self.button2.clicked.connect(self.generate_640AO)
        self.button2.clicked.connect(self.generate_640AO_graphy)
        
        # --------------------------------------------------------488 AO--------------------------------------------------------
        self.textbox3A = QComboBox()
        self.textbox3A.addItems(['0','1'])
        self.AnalogLayout.addWidget(self.textbox3A, 7, 0)
        
        self.AnalogLayout.addWidget(QLabel("488 AO : "), 6, 0)
        
        self.textbox3B = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox3B, 6, 2)
        self.AnalogLayout.addWidget(QLabel("Frequency in period:"), 6, 1)

        self.textbox3C = QPlainTextEdit(self)
        self.textbox3C.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox3C, 7, 2)
        self.AnalogLayout.addWidget(QLabel("Offset (ms):"), 7, 1)
        
        self.textbox3D = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox3D, 6, 4)
        self.AnalogLayout.addWidget(QLabel("Period (ms):"), 6, 3)   
        
        self.textbox3E = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox3E, 7, 4)
        self.textbox3E.setPlaceholderText('1')
        self.AnalogLayout.addWidget(QLabel("Repeat:"), 7, 3) 
        
        self.AnalogLayout.addWidget(QLabel("DC (%):"), 6, 5)
        self.textbox3F = QComboBox()
        self.textbox3F.addItems(['50','10'])
        self.AnalogLayout.addWidget(self.textbox3F, 6, 6)
        
        self.textbox3G = QPlainTextEdit(self)
        self.textbox3G.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox3G, 7, 6)
        self.AnalogLayout.addWidget(QLabel("Gap between repeat (samples):"), 7, 5)
        
        self.AnalogLayout.addWidget(QLabel("Starting amplitude (V)"), 6, 7)
        self.textbox3H = QComboBox()
        self.textbox3H.addItems(['5','1'])
        self.AnalogLayout.addWidget(self.textbox3H, 6, 8)        

        self.textbox3I = QPlainTextEdit(self)
        self.textbox3I.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox3I, 7, 8)
        self.AnalogLayout.addWidget(QLabel("Baseline (V):"), 7, 7)

        self.AnalogLayout.addWidget(QLabel("Step (V)"), 6, 9)
        self.textbox3J = QComboBox()
        self.textbox3J.addItems(['0','1', '2'])
        self.AnalogLayout.addWidget(self.textbox3J, 6, 10)

        self.AnalogLayout.addWidget(QLabel("Cycles"), 7, 9)
        self.textbox3K = QComboBox()
        self.textbox3K.addItems(['1','2', '3'])
        self.AnalogLayout.addWidget(self.textbox3K, 7, 10)
        
        self.button3 = QPushButton('SHOW WAVE', self)
        self.AnalogLayout.addWidget(self.button3, 6, 11)
        
        self.button3.clicked.connect(self.generate_488AO)
        self.button3.clicked.connect(self.generate_488AO_graphy)        
        #----------------------------------------------------------------532 AO------------------------------------------------
        self.textbox4A = QComboBox()
        self.textbox4A.addItems(['0','1'])
        self.AnalogLayout.addWidget(self.textbox4A, 9, 0)
        
        self.AnalogLayout.addWidget(QLabel("532 AO : "), 8, 0)
        
        self.textbox4B = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox4B, 8, 2)
        self.AnalogLayout.addWidget(QLabel("Frequency in period:"), 8, 1)

        self.textbox4C = QPlainTextEdit(self)
        self.textbox4C.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox4C, 9, 2)
        self.AnalogLayout.addWidget(QLabel("Offset (ms):"), 9, 1)
        
        self.textbox4D = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox4D, 8, 4)
        self.AnalogLayout.addWidget(QLabel("Period (ms):"), 8, 3)   
        
        self.textbox4E = QPlainTextEdit(self)
        self.textbox4E.setPlaceholderText('1')
        self.AnalogLayout.addWidget(self.textbox4E, 9, 4)
        self.AnalogLayout.addWidget(QLabel("Repeat:"), 9, 3) 
        
        self.AnalogLayout.addWidget(QLabel("DC (%):"), 8, 5)
        self.textbox4F = QComboBox()
        self.textbox4F.addItems(['50','10'])
        self.AnalogLayout.addWidget(self.textbox4F, 8, 6)
        
        self.textbox4G = QPlainTextEdit(self)
        self.textbox4G.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox4G, 9, 6)
        self.AnalogLayout.addWidget(QLabel("Gap between repeat (samples):"), 9, 5)
        
        self.AnalogLayout.addWidget(QLabel("Starting amplitude (V)"), 8, 7)
        self.textbox4H = QComboBox()
        self.textbox4H.addItems(['5','1'])
        self.AnalogLayout.addWidget(self.textbox4H, 8, 8)        

        self.textbox4I = QPlainTextEdit(self)
        self.textbox4I.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox4I, 9, 8)
        self.AnalogLayout.addWidget(QLabel("Baseline (V):"), 9, 7)

        self.AnalogLayout.addWidget(QLabel("Step (V)"), 8, 9)
        self.textbox4J = QComboBox()
        self.textbox4J.addItems(['0','1', '2'])
        self.AnalogLayout.addWidget(self.textbox4J, 8, 10)

        self.AnalogLayout.addWidget(QLabel("Cycles"), 9, 9)
        self.textbox4K = QComboBox()
        self.textbox4K.addItems(['1','2', '3'])
        self.AnalogLayout.addWidget(self.textbox4K, 9, 10)
        
        self.button4 = QPushButton('SHOW WAVE', self)
        self.AnalogLayout.addWidget(self.button4, 8, 11)
        
        self.button4.clicked.connect(self.generate_532AO)
        self.button4.clicked.connect(self.generate_532AO_graphy)
        AnalogContainer.setLayout(self.AnalogLayout)
        
        #-----------------------------------------------------------V-patch------------------------------------------------
        self.textbox5A = QComboBox()
        self.textbox5A.addItems(['0','1'])
        self.AnalogLayout.addWidget(self.textbox5A, 11, 0)
        
        self.AnalogLayout.addWidget(QLabel("V-patch : "), 10, 0)
        
        self.textbox5B = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox5B, 10, 2)
        self.AnalogLayout.addWidget(QLabel("Frequency in period:"), 10, 1)

        self.textbox5C = QPlainTextEdit(self)
        self.textbox5C.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox5C, 11, 2)
        self.AnalogLayout.addWidget(QLabel("Offset (ms):"), 11, 1)
        
        self.textbox5D = QPlainTextEdit(self)
        self.AnalogLayout.addWidget(self.textbox5D, 10, 4)
        self.AnalogLayout.addWidget(QLabel("Period (ms):"), 10, 3)   
        
        self.textbox5E = QPlainTextEdit(self)
        self.textbox5E.setPlaceholderText('1')
        self.AnalogLayout.addWidget(self.textbox5E, 11, 4)
        self.AnalogLayout.addWidget(QLabel("Repeat:"), 11, 3) 
        
        self.AnalogLayout.addWidget(QLabel("DC (%):"), 10, 5)
        self.textbox5F = QComboBox()
        self.textbox5F.addItems(['50','10'])
        self.AnalogLayout.addWidget(self.textbox5F, 10, 6)
        
        self.textbox5G = QPlainTextEdit(self)
        self.textbox5G.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox5G, 11, 6)
        self.AnalogLayout.addWidget(QLabel("Gap between repeat (samples):"), 11, 5)
        
        self.AnalogLayout.addWidget(QLabel("Starting amplitude (V)"), 10, 7)
        self.textbox5H = QComboBox()
        self.textbox5H.addItems(['5','1'])
        self.AnalogLayout.addWidget(self.textbox5H, 10, 8)        

        self.textbox5I = QPlainTextEdit(self)
        self.textbox5I.setPlaceholderText('0')
        self.AnalogLayout.addWidget(self.textbox5I, 11, 8)
        self.AnalogLayout.addWidget(QLabel("Baseline (V):"), 11, 7)

        self.AnalogLayout.addWidget(QLabel("Step (V)"), 10, 9)
        self.textbox5J = QComboBox()
        self.textbox5J.addItems(['0','1', '2'])
        self.AnalogLayout.addWidget(self.textbox5J, 10, 10)

        self.AnalogLayout.addWidget(QLabel("Cycles"), 11, 9)
        self.textbox5K = QComboBox()
        self.textbox5K.addItems(['1','2', '3'])
        self.AnalogLayout.addWidget(self.textbox5K, 11, 10)
        
        self.button5 = QPushButton('SHOW WAVE', self)
        self.AnalogLayout.addWidget(self.button5, 10, 11)
        
        self.button5.clicked.connect(self.generate_patchAO)
        self.button5.clicked.connect(self.generate_patchAO_graphy)
        
        AnalogContainer.setLayout(self.AnalogLayout)        
        
        
        
        #------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------Digital-------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------       
        DigitalContainer = QGroupBox("Digital signals")
        self.DigitalLayout = QGridLayout() #self.AnalogLayout manager
        
        # ------------------------------------------------------Camera triggering------------------------------------------
        self.textbox11A = QComboBox()
        self.textbox11A.addItems(['1','0'])
        self.DigitalLayout.addWidget(self.textbox11A, 1, 0)
        
        self.DigitalLayout.addWidget(QLabel("Camera triggering : "), 0, 0)
        
        self.textbox11B = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox11B, 0, 2)
        self.DigitalLayout.addWidget(QLabel("Frequency in period:"), 0, 1)

        self.textbox11C = QPlainTextEdit(self)
        self.textbox11C.setPlaceholderText('0')
        self.DigitalLayout.addWidget(self.textbox11C, 1, 2)
        self.DigitalLayout.addWidget(QLabel("Offset (ms):"), 1, 1)
        
        self.textbox11D = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox11D, 0, 4)
        self.DigitalLayout.addWidget(QLabel("Period (ms):"), 0, 3)   
        
        self.textbox11E = QPlainTextEdit(self)
        self.textbox11E.setPlaceholderText('1')
        self.DigitalLayout.addWidget(self.textbox11E, 1, 4)
        self.DigitalLayout.addWidget(QLabel("Repeat:"), 1, 3) 
        
        self.DigitalLayout.addWidget(QLabel("DC (%):"), 0, 5)
        self.textbox11F = QComboBox()
        self.textbox11F.addItems(['50','10','0','100'])
        self.DigitalLayout.addWidget(self.textbox11F, 0, 6)

        self.textbox11G = QPlainTextEdit(self)
        self.textbox11G.setPlaceholderText('0')
        self.DigitalLayout.addWidget(self.textbox11G, 1, 6)
        self.DigitalLayout.addWidget(QLabel("Gap between repeat (samples):"), 1, 5)
        
        self.button_camera = QPushButton('SHOW WAVE', self)
        self.DigitalLayout.addWidget(self.button_camera, 1, 7)
        
        self.button_camera.clicked.connect(self.generate_cameratrigger)
        self.button_camera.clicked.connect(self.generate_cameratrigger_graphy)
        
        # ----------------------------------------------------------640 blanking---------------------------------------
        self.textbox22A = QComboBox()
        self.textbox22A.addItems(['0','1'])
        self.DigitalLayout.addWidget(self.textbox22A, 3, 0)
        
        self.DigitalLayout.addWidget(QLabel("640 blanking : "), 2, 0)
        
        self.textbox22B = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox22B, 2, 2)
        self.DigitalLayout.addWidget(QLabel("Frequency in period:"), 2, 1)

        self.textbox22C = QPlainTextEdit(self)
        self.textbox22C.setPlaceholderText('0')
        self.DigitalLayout.addWidget(self.textbox22C, 3, 2)
        self.DigitalLayout.addWidget(QLabel("Offset (ms):"), 3, 1)
        
        self.textbox22D = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox22D, 2, 4)
        self.DigitalLayout.addWidget(QLabel("Period (ms):"), 2, 3)   
        
        self.textbox22E = QPlainTextEdit(self)
        self.textbox22E.setPlaceholderText('1')
        self.DigitalLayout.addWidget(self.textbox22E, 3, 4)
        self.DigitalLayout.addWidget(QLabel("Repeat:"), 3, 3) 
        
        self.DigitalLayout.addWidget(QLabel("DC (%):"), 2, 5)
        self.textbox22F = QComboBox()
        self.textbox22F.addItems(['50','10'])
        self.DigitalLayout.addWidget(self.textbox22F, 2, 6)    
        
        self.textbox22G = QPlainTextEdit(self)
        self.textbox22G.setPlaceholderText('0')
        self.DigitalLayout.addWidget(self.textbox22G, 3, 6)
        self.DigitalLayout.addWidget(QLabel("Gap between repeat (samples):"), 3, 5)
        
        self.button_640blanking = QPushButton('SHOW WAVE', self)
        self.DigitalLayout.addWidget(self.button_640blanking, 3, 7)
        
        self.button_640blanking.clicked.connect(self.generate_640blanking)
        self.button_640blanking.clicked.connect(self.generate_640blanking_graphy)
        # --------------------------------------------------------532 blanking-----------------------------------------
        self.textbox33A = QComboBox()
        self.textbox33A.addItems(['0','1'])
        self.DigitalLayout.addWidget(self.textbox33A, 5, 0)
        
        self.DigitalLayout.addWidget(QLabel("532 blanking : "), 4, 0)
        
        self.textbox33B = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox33B, 4, 2)
        self.DigitalLayout.addWidget(QLabel("Frequency in period:"), 4, 1)

        self.textbox33C = QPlainTextEdit(self)
        self.textbox33C.setPlaceholderText('0')
        self.DigitalLayout.addWidget(self.textbox33C, 5, 2)
        self.DigitalLayout.addWidget(QLabel("Offset (ms):"), 5, 1)
        
        self.textbox33D = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox33D, 4, 4)
        self.DigitalLayout.addWidget(QLabel("Period (ms):"), 4, 3)   
        
        self.textbox33E = QPlainTextEdit(self)
        self.textbox33E.setPlaceholderText('1')
        self.DigitalLayout.addWidget(self.textbox33E, 5, 4)
        self.DigitalLayout.addWidget(QLabel("Repeat:"), 5, 3) 
        
        self.DigitalLayout.addWidget(QLabel("DC (%):"), 4, 5)
        self.textbox33F = QComboBox()
        self.textbox33F.addItems(['50','10'])
        self.DigitalLayout.addWidget(self.textbox33F, 4, 6) 
        
        self.textbox33G = QPlainTextEdit(self)
        self.textbox33G.setPlaceholderText('0')
        self.DigitalLayout.addWidget(self.textbox33G, 5, 6)
        self.DigitalLayout.addWidget(QLabel("Gap between repeat (samples):"), 5, 5)
        
        self.button_532blanking = QPushButton('SHOW WAVE', self)
        self.DigitalLayout.addWidget(self.button_532blanking, 5, 7)
        
        self.button_532blanking.clicked.connect(self.generate_532blanking)
        self.button_532blanking.clicked.connect(self.generate_532blanking_graphy)
        # ------------------------------------------------------488 blanking---------------------------------------------
        self.textbox44A = QComboBox()
        self.textbox44A.addItems(['0','1'])
        self.DigitalLayout.addWidget(self.textbox44A, 7, 0)
        
        self.DigitalLayout.addWidget(QLabel("488 blanking : "), 6, 0)
        
        self.textbox44B = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox44B, 6, 2)
        self.DigitalLayout.addWidget(QLabel("Frequency in period:"), 6, 1)

        self.textbox44C = QPlainTextEdit(self)
        self.textbox44C.setPlaceholderText('0')
        self.DigitalLayout.addWidget(self.textbox44C, 7, 2)
        self.DigitalLayout.addWidget(QLabel("Offset (ms):"), 7, 1)
        
        self.textbox44D = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox44D, 6, 4)
        self.DigitalLayout.addWidget(QLabel("Period (ms):"), 6, 3)   
        
        self.textbox44E = QPlainTextEdit(self)
        self.textbox44E.setPlaceholderText('1')
        self.DigitalLayout.addWidget(self.textbox44E, 7, 4)
        self.DigitalLayout.addWidget(QLabel("Repeat:"), 7, 3) 
        
        self.DigitalLayout.addWidget(QLabel("DC (%):"), 6, 5)
        self.textbox44F = QComboBox()
        self.textbox44F.addItems(['50','10'])
        self.DigitalLayout.addWidget(self.textbox44F, 6, 6) 
                
        self.textbox44G = QPlainTextEdit(self)
        self.textbox44G.setPlaceholderText('0')
        self.DigitalLayout.addWidget(self.textbox44G, 7, 6)
        self.DigitalLayout.addWidget(QLabel("Gap between repeat (samples):"), 7, 5)
        
        self.button_488blanking = QPushButton('SHOW WAVE', self)
        self.DigitalLayout.addWidget(self.button_488blanking, 7, 7)
        
        self.button_488blanking.clicked.connect(self.generate_488blanking)
        self.button_488blanking.clicked.connect(self.generate_488blanking_graphy) 
        
        # ------------------------------------------------------blankingall---------------------------------------------
        self.textbox55A = QComboBox()
        self.textbox55A.addItems(['0','1'])
        self.DigitalLayout.addWidget(self.textbox55A, 9, 0)
        
        self.DigitalLayout.addWidget(QLabel("blanking all : "), 8, 0)
        
        self.textbox55B = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox55B, 8, 2)
        self.DigitalLayout.addWidget(QLabel("Frequency in period:"), 8, 1)

        self.textbox55C = QPlainTextEdit(self)
        self.textbox55C.setPlaceholderText('0')
        self.DigitalLayout.addWidget(self.textbox55C, 9, 2)
        self.DigitalLayout.addWidget(QLabel("Offset (ms):"), 9, 1)
        
        self.textbox55D = QPlainTextEdit(self)
        self.DigitalLayout.addWidget(self.textbox55D, 8, 4)
        self.DigitalLayout.addWidget(QLabel("Period (ms):"), 8, 3)   
        
        self.textbox55E = QPlainTextEdit(self)
        self.textbox55E.setPlaceholderText('1')
        self.DigitalLayout.addWidget(self.textbox55E, 9, 4)
        self.DigitalLayout.addWidget(QLabel("Repeat:"), 9, 3) 
        
        self.DigitalLayout.addWidget(QLabel("DC (%):"), 8, 5)
        self.textbox55F = QComboBox()
        self.textbox55F.addItems(['0','100','50'])
        self.DigitalLayout.addWidget(self.textbox55F, 8, 6) 
                
        self.textbox55G = QPlainTextEdit(self)
        self.textbox55G.setPlaceholderText('0')
        self.DigitalLayout.addWidget(self.textbox55G, 9, 6)
        self.DigitalLayout.addWidget(QLabel("Gap between repeat (samples):"), 9, 5)
        
        self.button_blankingall = QPushButton('SHOW WAVE', self)
        self.DigitalLayout.addWidget(self.button_blankingall, 9, 7)
        
        self.button_blankingall.clicked.connect(self.generate_blankingall)
        self.button_blankingall.clicked.connect(self.generate_blankingall_graphy)
              
        DigitalContainer.setLayout(self.DigitalLayout)

        #------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------Readin-------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------       
        ReadContainer = QGroupBox("Readin channels")
        self.ReadLayout = QGridLayout() #self.AnalogLayout manager
        
        # ------------------------------------------------------Camera triggering------------------------------------------
        self.textbox111A = QComboBox()
        self.textbox111A.addItems(['1','0'])
        self.ReadLayout.addWidget(self.textbox111A, 1, 0)     
        
        self.ReadLayout.addWidget(QLabel("PMT : "), 0, 0)
        
        self.textbox222A = QComboBox()
        self.textbox222A.addItems(['0','1'])
        self.ReadLayout.addWidget(self.textbox222A, 1, 1)     
        
        self.ReadLayout.addWidget(QLabel("Vp : "), 0, 1)
        
        self.textbox333A = QComboBox()
        self.textbox333A.addItems(['0','1'])
        self.ReadLayout.addWidget(self.textbox333A, 1, 2)     
        
        self.ReadLayout.addWidget(QLabel("Ip : "), 0, 2)
        
        ReadContainer.setLayout(self.ReadLayout)
        #--------------Adding to master----------------------------------------
        master = QVBoxLayout()
        master.addWidget(AnalogContainer)
        master.addWidget(DigitalContainer)
        master.addWidget(ReadContainer)
        self.setLayout(master)
        
            
            
    def generate_galvos(self):
        
        self.Daq_sample_rate = int(self.textboxAA.currentText())
        
        #Scanning settings
        if int(self.textbox1A.currentText()) == 1:
            Value_voltXMin = int(self.textbox1B.currentText())
            Value_voltXMax = int(self.textbox1C.currentText())
            Value_voltYMin = int(self.textbox1D.currentText())
            Value_voltYMax = int(self.textbox1E.currentText())
            Value_xPixels = int(self.textbox1F.currentText())
            Value_yPixels = int(self.textbox1G.currentText())
            self.averagenum =int(self.textbox1H.currentText())
            
            if not self.textbox1I.toPlainText():
                self.Galvo_samples_offset = 1
                self.offsetsamples_galvo = []

            else:
                self.Galvo_samples_offset = int(self.textbox1I.toPlainText())
                
                self.offsetsamples_number_galvo = int((self.Galvo_samples_offset/1000)*self.Daq_sample_rate) # By default one 0 is added so that we have a rising edge at the beginning.
                self.offsetsamples_galvo = np.zeros(self.offsetsamples_number_galvo) # Be default offsetsamples_number is an integer.    
            #Generate galvo samples            
            self.samples_1, self.samples_2= wavegenerator.waveRecPic(sampleRate = self.Daq_sample_rate, imAngle = 0, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, 
                             voltYMin = Value_voltYMin, voltYMax = Value_voltYMax, xPixels = Value_xPixels, yPixels = Value_yPixels, 
                             sawtooth = True)
            #ScanArrayX = wavegenerator.xValuesSingleSawtooth(sampleRate = Daq_sample_rate, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, xPixels = Value_xPixels, sawtooth = True)
            Totalscansamples = len(self.samples_1)*self.averagenum # Calculate number of samples to feed to scanner, by default it's one frame 
            self.ScanArrayXnum = int (len(self.samples_1)/Value_yPixels) # number of samples of each individual line of x scanning
            
            #print(self.Digital_container_feeder[:, 0])
            
            self.repeated_samples_1 = np.tile(self.samples_1, self.averagenum)
            self.repeated_samples_2_yaxis = np.tile(self.samples_2, self.averagenum)

            self.repeated_samples_1 = np.append(self.offsetsamples_galvo, self.repeated_samples_1)
            self.repeated_samples_2_yaxis = np.append(self.offsetsamples_galvo, self.repeated_samples_2_yaxis)
            
            self.Galvo_samples = np.vstack((self.repeated_samples_1,self.repeated_samples_2_yaxis))
            
            return self.Galvo_samples
            
    def generate_galvos_graphy(self):
            plt.figure()

            self.xlabelhere_galvo = np.arange(len(self.repeated_samples_2_yaxis))/self.Daq_sample_rate
            #plt.plot(xlabelhere_galvo, samples_1)
            plt.plot(self.xlabelhere_galvo, self.repeated_samples_2_yaxis)
            plt.text(0.1, 2, 'Time lasted:'+str(self.xlabelhere_galvo[-1])+'s', fontsize=12)
            #plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d s'))
            plt.show()
            
    def generate_galvotrigger(self):
        self.Daq_sample_rate = int(self.textboxAA.currentText())
        #Scanning settings
        if int(self.textbox1A.currentText()) == 1:
            Value_voltXMin = int(self.textbox1B.currentText())
            Value_voltXMax = int(self.textbox1C.currentText())
            Value_voltYMin = int(self.textbox1D.currentText())
            Value_voltYMax = int(self.textbox1E.currentText())
            Value_xPixels = int(self.textbox1F.currentText())
            Value_yPixels = int(self.textbox1G.currentText())
            self.averagenum =int(self.textbox1H.currentText())
            
            if not self.textbox1I.toPlainText():
                self.Galvo_samples_offset = 1
                self.offsetsamples_galvo = []

            else:
                self.Galvo_samples_offset = int(self.textbox1I.toPlainText())
                
                self.offsetsamples_number_galvo = int((self.Galvo_samples_offset/1000)*self.Daq_sample_rate) # By default one 0 is added so that we have a rising edge at the beginning.
                self.offsetsamples_galvo = np.zeros(self.offsetsamples_number_galvo) # Be default offsetsamples_number is an integer.    
            #Generate galvo samples            
            self.samples_1, self.samples_2= wavegenerator.waveRecPic(sampleRate = self.Daq_sample_rate, imAngle = 0, voltXMin = Value_voltXMin, voltXMax = Value_voltXMax, 
                             voltYMin = Value_voltYMin, voltYMax = Value_voltYMax, xPixels = Value_xPixels, yPixels = Value_yPixels, 
                             sawtooth = True)
            self.ScanArrayXnum = int (len(self.samples_1)/Value_yPixels) # number of samples of each individual line of x scanning
            
            #print(self.Digital_container_feeder[:, 0])
            
            self.repeated_samples_1 = np.tile(self.samples_1, self.averagenum)
            self.repeated_samples_2_yaxis = np.tile(self.samples_2, self.averagenum)

            self.repeated_samples_1 = np.append(self.offsetsamples_galvo, self.repeated_samples_1)
            self.repeated_samples_2_yaxis = np.append(self.offsetsamples_galvo, self.repeated_samples_2_yaxis)
       
            samplenumber_oneframe = len(self.samples_1)
            
            self.true_sample_num_singleperiod_galvotrigger = round((20/1000)*self.Daq_sample_rate) # Default the trigger lasts for 20 ms.
            self.false_sample_num_singleperiod_galvotrigger = samplenumber_oneframe - self.true_sample_num_singleperiod_galvotrigger
            
            self.true_sample_singleperiod_galvotrigger = np.ones(self.true_sample_num_singleperiod_galvotrigger, dtype=bool)
            self.true_sample_singleperiod_galvotrigger[0] = False  # first one False to give a rise.
            
            self.sample_singleperiod_galvotrigger = np.append(self.true_sample_singleperiod_galvotrigger, np.zeros(self.false_sample_num_singleperiod_galvotrigger, dtype=bool))
            
            self.sample_repeatedperiod_galvotrigger = np.tile(self.sample_singleperiod_galvotrigger, self.averagenum)
            
            self.offset_galvotrigger = np.array(self.offsetsamples_galvo, dtype=bool)
            
            self.final_galvotrigger = np.append(self.offset_galvotrigger, self.sample_repeatedperiod_galvotrigger)
            return self.final_galvotrigger
        
    def generate_galvotrigger_graphy(self):
        self.xlabelhere_galvo = np.arange(len(self.repeated_samples_2_yaxis))/self.Daq_sample_rate
        plt.figure()
        plt.plot(self.xlabelhere_galvo, self.repeated_samples_2_yaxis)
        plt.plot(self.xlabelhere_galvo, self.final_galvotrigger)
        plt.text(0.1, 2, 'Time lasted:'+str(self.xlabelhere_galvo[-1])+'s', fontsize=12)
            #plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d s'))
        plt.show()
        
    def generate_640AO(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_2 = float(self.textbox2B.toPlainText())
        if not self.textbox2C.toPlainText():
            self.uiwaveoffset_2 = 0
        else:
            self.uiwaveoffset_2 = int(self.textbox2C.toPlainText()) # in ms
        self.uiwaveperiod_2 = int(self.textbox2D.toPlainText())
        self.uiwaveDC_2 = int(self.textbox2F.currentText())
        if not self.textbox2E.toPlainText():
            self.uiwaverepeat_2 = 1
        else:
            self.uiwaverepeat_2 = int(self.textbox2E.toPlainText())
        if not self.textbox2G.toPlainText():
            self.uiwavegap_2 = 0
        else:
            self.uiwavegap_2 = int(self.textbox2G.toPlainText())
        self.uiwavestartamplitude_2 = float(self.textbox2H.currentText())
        if not self.textbox2I.toPlainText():
            self.uiwavebaseline_2 = 0
        else:
            self.uiwavebaseline_2 = float(self.textbox2I.toPlainText())
        self.uiwavestep_2 = int(self.textbox2J.currentText())
        self.uiwavecycles_2 = int(self.textbox2K.currentText())   
        
        if int(self.textbox2A.currentText()) == 1:
            
            s = generate_AO_for640(self.uiDaq_sample_rate, self.uiwavefrequency_2, self.uiwaveoffset_2, self.uiwaveperiod_2, self.uiwaveDC_2
                                   , self.uiwaverepeat_2, self.uiwavegap_2, self.uiwavestartamplitude_2, self.uiwavebaseline_2, self.uiwavestep_2, self.uiwavecycles_2)
            self.finalwave_640 = s.generate()
            return self.finalwave_640
            
    def generate_640AO_graphy(self):            
        xlabelhere_640 = np.arange(len(self.finalwave_640))/self.uiDaq_sample_rate
        #plt.plot(xlabelhere_galvo, samples_1)
        plt.plot(xlabelhere_640, self.finalwave_640)
        plt.text(0.1, 2, 'Time lasted:'+str(xlabelhere_640[-1])+'s', fontsize=12)
        #plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d s'))
        plt.show()            

    def generate_488AO(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_488AO = float(self.textbox3B.toPlainText())
        if not self.textbox3C.toPlainText():
            self.uiwaveoffset_488AO = 0
        else:
            self.uiwaveoffset_488AO = int(self.textbox3C.toPlainText()) # in ms
        self.uiwaveperiod_488AO = int(self.textbox3D.toPlainText())
        self.uiwaveDC_488AO = int(self.textbox3F.currentText())
        if not self.textbox3E.toPlainText():
            self.uiwaverepeat_488AO = 1
        else:
            self.uiwaverepeat_488AO = int(self.textbox3E.toPlainText())
        if not self.textbox3G.toPlainText():
            self.uiwavegap_488AO = 0
        else:
            self.uiwavegap_488AO = int(self.textbox3G.toPlainText())
        self.uiwavestartamplitude_488AO = float(self.textbox3H.currentText())
        if not self.textbox3I.toPlainText():
            self.uiwavebaseline_488AO = 0
        else:
            self.uiwavebaseline_488AO = float(self.textbox3I.toPlainText())
        self.uiwavestep_488AO = int(self.textbox3J.currentText())
        self.uiwavecycles_488AO = int(self.textbox3K.currentText())   
        
        if int(self.textbox3A.currentText()) == 1:
            
            s = generate_AO_for488(self.uiDaq_sample_rate, self.uiwavefrequency_488AO, self.uiwaveoffset_488AO, self.uiwaveperiod_488AO, self.uiwaveDC_488AO
                                   , self.uiwaverepeat_488AO, self.uiwavegap_488AO, self.uiwavestartamplitude_488AO, self.uiwavebaseline_488AO, self.uiwavestep_488AO, self.uiwavecycles_488AO)
            self.finalwave_488 = s.generate()
            return self.finalwave_488
            
    def generate_488AO_graphy(self):
        xlabelhere_488 = np.arange(len(self.finalwave_488))/self.uiDaq_sample_rate
        #plt.plot(xlabelhere_galvo, samples_1)
        plt.plot(xlabelhere_488, self.finalwave_488)
        plt.text(0.1, 2, 'Time lasted:'+str(xlabelhere_488[-1])+'s', fontsize=12)
        #plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d s'))
        plt.show()
        
    def generate_532AO(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_532AO = float(self.textbox4B.toPlainText())
        if not self.textbox4C.toPlainText():
            self.uiwaveoffset_532AO = 0
        else:
            self.uiwaveoffset_532AO = int(self.textbox4C.toPlainText()) # in ms
        self.uiwaveperiod_532AO = int(self.textbox4D.toPlainText())
        self.uiwaveDC_532AO = int(self.textbox4F.currentText())
        if not self.textbox4E.toPlainText():
            self.uiwaverepeat_532AO = 1
        else:
            self.uiwaverepeat_532AO = int(self.textbox4E.toPlainText())
        if not self.textbox4G.toPlainText():
            self.uiwavegap_532AO = 0
        else:
            self.uiwavegap_532AO = int(self.textbox4G.toPlainText())
        self.uiwavestartamplitude_532AO = float(self.textbox4H.currentText())
        if not self.textbox4I.toPlainText():
            self.uiwavebaseline_532AO = 0
        else:
            self.uiwavebaseline_532AO = float(self.textbox4I.toPlainText())
        self.uiwavestep_532AO = int(self.textbox4J.currentText())
        self.uiwavecycles_532AO = int(self.textbox4K.currentText())   
        
        if int(self.textbox4A.currentText()) == 1:
            
            s = generate_AO_for532(self.uiDaq_sample_rate, self.uiwavefrequency_532AO, self.uiwaveoffset_532AO, self.uiwaveperiod_532AO, self.uiwaveDC_532AO
                                   , self.uiwaverepeat_532AO, self.uiwavegap_532AO, self.uiwavestartamplitude_532AO, self.uiwavebaseline_532AO, self.uiwavestep_532AO, self.uiwavecycles_532AO)
            self.finalwave_532 = s.generate()
            return self.finalwave_532
            
    def generate_532AO_graphy(self):
        xlabelhere_532 = np.arange(len(self.finalwave_532))/self.uiDaq_sample_rate
        #plt.plot(xlabelhere_galvo, samples_1)
        plt.plot(xlabelhere_532, self.finalwave_532)
        plt.text(0.1, 2, 'Time lasted:'+str(xlabelhere_532[-1])+'s', fontsize=12)
        #plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d s'))
        plt.show()  
        
        
    def generate_patchAO(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_patchAO = float(self.textbox5B.toPlainText())
        if not self.textbox5C.toPlainText():
            self.uiwaveoffset_patchAO = 0
        else:
            self.uiwaveoffset_patchAO = int(self.textbox5C.toPlainText()) # in ms
        self.uiwaveperiod_patchAO = int(self.textbox5D.toPlainText())
        self.uiwaveDC_patchAO = int(self.textbox5F.currentText())
        if not self.textbox5E.toPlainText():
            self.uiwaverepeat_patchAO = 1
        else:
            self.uiwaverepeat_patchAO = int(self.textbox5E.toPlainText())
        if not self.textbox5G.toPlainText():
            self.uiwavegap_patchAO = 0
        else:
            self.uiwavegap_patchAO = int(self.textbox5G.toPlainText())
        self.uiwavestartamplitude_patchAO = float(self.textbox5H.currentText())
        if not self.textbox5I.toPlainText():
            self.uiwavebaseline_patchAO = 0
        else:
            self.uiwavebaseline_patchAO = float(self.textbox5I.toPlainText())
        self.uiwavestep_patchAO = int(self.textbox5J.currentText())
        self.uiwavecycles_patchAO = int(self.textbox5K.currentText())   
        
        if int(self.textbox5A.currentText()) == 1:
            
            s = generate_AO_forpatch(self.uiDaq_sample_rate, self.uiwavefrequency_patchAO, self.uiwaveoffset_patchAO, self.uiwaveperiod_patchAO, self.uiwaveDC_patchAO
                                   , self.uiwaverepeat_patchAO, self.uiwavegap_patchAO, self.uiwavestartamplitude_patchAO, self.uiwavebaseline_patchAO, self.uiwavestep_patchAO, self.uiwavecycles_patchAO)
            self.finalwave_patch = s.generate()
            return self.finalwave_patch
            
    def generate_patchAO_graphy(self):
        xlabelhere_patch = np.arange(len(self.finalwave_patch))/self.uiDaq_sample_rate
        #plt.plot(xlabelhere_galvo, samples_1)
        plt.plot(xlabelhere_patch, self.finalwave_patch)
        plt.text(0.1, 2, 'Time lasted:'+str(xlabelhere_patch[-1])+'s', fontsize=12)
        #plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d s'))
        plt.show()

    def generate_cameratrigger(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_cameratrigger = float(self.textbox11B.toPlainText())
        if not self.textbox11C.toPlainText():
            self.uiwaveoffset_cameratrigger = 0
        else:
            self.uiwaveoffset_cameratrigger = int(self.textbox11C.toPlainText())
        self.uiwaveperiod_cameratrigger = int(self.textbox11D.toPlainText())
        self.uiwaveDC_cameratrigger = int(self.textbox11F.currentText())
        if not self.textbox11E.toPlainText():
            self.uiwaverepeat_cameratrigger_number = 1
        else:
            self.uiwaverepeat_cameratrigger_number = int(self.textbox11E.toPlainText())
        if not self.textbox11G.toPlainText():
            self.uiwavegap_cameratrigger = 0
        else:
            self.uiwavegap_cameratrigger = int(self.textbox11G.toPlainText())
        
        if int(self.textbox11A.currentText()) == 1:
            
            cameratrigger = generate_DO_forcameratrigger(self.uiDaq_sample_rate, self.uiwavefrequency_cameratrigger, self.uiwaveoffset_cameratrigger,
                                                         self.uiwaveperiod_cameratrigger, self.uiwaveDC_cameratrigger, self.uiwaverepeat_cameratrigger_number, self.uiwavegap_cameratrigger)
            self.finalwave_cameratrigger = cameratrigger.generate()
            return self.finalwave_cameratrigger
            
    def generate_cameratrigger_graphy(self):

        xlabelhere_cameratrigger = np.arange(len(self.finalwave_cameratrigger))/self.uiDaq_sample_rate
        #plt.plot(xlabelhere_galvo, samples_1)
        plt.plot(xlabelhere_cameratrigger, self.finalwave_cameratrigger)
        plt.text(0.1, 1.1, 'Time lasted:'+str(xlabelhere_cameratrigger[-1])+'s', fontsize=12)
        #plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d s'))
        plt.show()     
            
    def generate_640blanking(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_640blanking = float(self.textbox22B.toPlainText())
        if not self.textbox22C.toPlainText():
            self.uiwaveoffset_640blanking = 0
        else:
            self.uiwaveoffset_640blanking = int(self.textbox22C.toPlainText())
        self.uiwaveperiod_640blanking = int(self.textbox22D.toPlainText())
        self.uiwaveDC_640blanking = int(self.textbox22F.currentText())
        if not self.textbox22E.toPlainText():
            self.uiwaverepeat_640blanking_number = 1
        else:
            self.uiwaverepeat_640blanking_number = int(self.textbox22E.toPlainText())
        if not self.textbox22G.toPlainText():
            self.uiwavegap_640blanking = 0
        else:
            self.uiwavegap_640blanking = int(self.textbox22G.toPlainText())
        
        if int(self.textbox22A.currentText()) == 1:
            
            blanking640 = generate_DO_for640blanking(self.uiDaq_sample_rate, self.uiwavefrequency_640blanking, self.uiwaveoffset_640blanking,
                                                         self.uiwaveperiod_640blanking, self.uiwaveDC_640blanking, self.uiwaverepeat_640blanking_number, self.uiwavegap_640blanking)
            self.finalwave_640blanking = blanking640.generate()
            return self.finalwave_640blanking
            
    def generate_640blanking_graphy(self):    

        xlabelhere_640blanking = np.arange(len(self.finalwave_640blanking))/self.uiDaq_sample_rate
        #plt.plot(xlabelhere_galvo, samples_1)
        plt.plot(xlabelhere_640blanking, self.finalwave_640blanking)
        plt.text(0.1, 1.1, 'Time lasted:'+str(xlabelhere_640blanking[-1])+'s', fontsize=12)
        #plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d s'))
        plt.show()
        
    def generate_532blanking(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_532blanking = float(self.textbox33B.toPlainText())
        if not self.textbox33C.toPlainText():
            self.uiwaveoffset_532blanking = 0
        else:
            self.uiwaveoffset_532blanking = int(self.textbox33C.toPlainText())
        self.uiwaveperiod_532blanking = int(self.textbox33D.toPlainText())
        self.uiwaveDC_532blanking = int(self.textbox33F.currentText())
        if not self.textbox33E.toPlainText():
            self.uiwaverepeat_532blanking_number = 1
        else:
            self.uiwaverepeat_532blanking_number = int(self.textbox33E.toPlainText())
        if not self.textbox33G.toPlainText():
            self.uiwavegap_532blanking = 0
        else:
            self.uiwavegap_532blanking = int(self.textbox33G.toPlainText())
        
        if int(self.textbox33A.currentText()) == 1:
            
            blanking532 = generate_DO_for532blanking(self.uiDaq_sample_rate, self.uiwavefrequency_532blanking, self.uiwaveoffset_532blanking,
                                                         self.uiwaveperiod_532blanking, self.uiwaveDC_532blanking, self.uiwaverepeat_532blanking_number, self.uiwavegap_532blanking)
            self.finalwave_532blanking = blanking532.generate()
            return self.finalwave_532blanking
            
    def generate_532blanking_graphy(self):    

        xlabelhere_532blanking = np.arange(len(self.finalwave_532blanking))/self.uiDaq_sample_rate
        #plt.plot(xlabelhere_galvo, samples_1)
        plt.plot(xlabelhere_532blanking, self.finalwave_532blanking)
        plt.text(0.1, 1.1, 'Time lasted:'+str(xlabelhere_532blanking[-1])+'s', fontsize=12)
        #plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d s'))
        plt.show()
        
    def generate_488blanking(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_488blanking = float(self.textbox44B.toPlainText())
        if not self.textbox44C.toPlainText():
            self.uiwaveoffset_488blanking = 0
        else:
            self.uiwaveoffset_488blanking = int(self.textbox44C.toPlainText())
        self.uiwaveperiod_488blanking = int(self.textbox44D.toPlainText())
        self.uiwaveDC_488blanking = int(self.textbox44F.currentText())
        if not self.textbox44E.toPlainText():
            self.uiwaverepeat_488blanking_number = 1
        else:
            self.uiwaverepeat_488blanking_number = int(self.textbox44E.toPlainText())
        if not self.textbox44G.toPlainText():
            self.uiwavegap_488blanking = 0
        else:
            self.uiwavegap_488blanking = int(self.textbox44G.toPlainText())
        
        if int(self.textbox44A.currentText()) == 1:
            
            blanking488 = generate_DO_for488blanking(self.uiDaq_sample_rate, self.uiwavefrequency_488blanking, self.uiwaveoffset_488blanking,
                                                         self.uiwaveperiod_488blanking, self.uiwaveDC_488blanking, self.uiwaverepeat_488blanking_number, self.uiwavegap_488blanking)
            self.finalwave_488blanking = blanking488.generate()
            return self.finalwave_488blanking
            
    def generate_488blanking_graphy(self):    

        xlabelhere_488blanking = np.arange(len(self.finalwave_488blanking))/self.uiDaq_sample_rate
        #plt.plot(xlabelhere_galvo, samples_1)
        plt.plot(xlabelhere_488blanking, self.finalwave_488blanking)
        plt.text(0.1, 1.1, 'Time lasted:'+str(xlabelhere_488blanking[-1])+'s', fontsize=12)
        #plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d s'))
        plt.show()
        
    def generate_blankingall(self):
        
        self.uiDaq_sample_rate = int(self.textboxAA.currentText())
        self.uiwavefrequency_blankingall = float(self.textbox55B.toPlainText())
        if not self.textbox55C.toPlainText():
            self.uiwaveoffset_blankingall = 0
        else:
            self.uiwaveoffset_blankingall = int(self.textbox55C.toPlainText())
        self.uiwaveperiod_blankingall = int(self.textbox55D.toPlainText())
        self.uiwaveDC_blankingall = int(self.textbox55F.currentText())
        if not self.textbox55E.toPlainText():
            self.uiwaverepeat_blankingall_number = 1
        else:
            self.uiwaverepeat_blankingall_number = int(self.textbox55E.toPlainText())
        if not self.textbox55G.toPlainText():
            self.uiwavegap_blankingall = 0
        else:
            self.uiwavegap_blankingall = int(self.textbox55G.toPlainText())
        
        if int(self.textbox55A.currentText()) == 1:
            
            blanking640 = generate_DO_forblankingall(self.uiDaq_sample_rate, self.uiwavefrequency_blankingall, self.uiwaveoffset_blankingall,
                                                         self.uiwaveperiod_blankingall, self.uiwaveDC_blankingall, self.uiwaverepeat_blankingall_number, self.uiwavegap_blankingall)
            self.finalwave_blankingall = blanking640.generate()
            return self.finalwave_blankingall
            
    def generate_blankingall_graphy(self):    

        xlabelhere_blankingall = np.arange(len(self.finalwave_blankingall))/self.uiDaq_sample_rate
        #plt.plot(xlabelhere_galvo, samples_1)
        plt.plot(xlabelhere_blankingall, self.finalwave_blankingall)
        plt.text(0.1, 1.1, 'Time lasted:'+str(xlabelhere_blankingall[-1])+'s', fontsize=12)
        #plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d s'))
        plt.show()
        
    def show_all(self):
        
        self.switch_galvos = int(self.textbox1A.currentText())
        self.switch_640AO = int(self.textbox2A.currentText())
        self.switch_488AO = int(self.textbox3A.currentText())
        self.switch_532AO = int(self.textbox4A.currentText())
        self.switch_patchAO = int(self.textbox5A.currentText())
        
        self.switch_cameratrigger = int(self.textbox11A.currentText())
        self.switch_galvotrigger = int(self.textbox1K.currentText())
        self.switch_blankingall = int(self.textbox55A.currentText())
        self.switch_640blanking = int(self.textbox22A.currentText())
        self.switch_532blanking = int(self.textbox33A.currentText())
        self.switch_488blanking = int(self.textbox44A.currentText())
        
        # Use dictionary to execute functions: https://stackoverflow.com/questions/9168340/using-a-dictionary-to-select-function-to-execute/9168387#9168387
        dictionary_analog = {'galvos':[self.switch_galvos,self.generate_galvos],
                              '640AO':[self.switch_640AO,self.generate_640AO],
                              '488AO':[self.switch_488AO,self.generate_488AO],
                              '532AO':[self.switch_532AO,self.generate_532AO],
                              'patchAO':[self.switch_patchAO,self.generate_patchAO],
                             }
                              
                              
        dictionary_digital = {'cameratrigger':[self.switch_cameratrigger,self.generate_cameratrigger],
                              'galvotrigger':[self.switch_galvotrigger,self.generate_galvotrigger], 
                              'blankingall':[self.switch_blankingall, self.generate_blankingall],
                              '640blanking':[self.switch_640blanking, self.generate_640blanking],
                              '532blanking':[self.switch_532blanking, self.generate_532blanking],
                              '488blanking':[self.switch_488blanking, self.generate_488blanking]
                              }
        # Calculate the length of reference wave
        # tags in the dictionary above should be the same as that in reference combox, then the dictionary below can work
        reference_wave = dictionary_analog[self.textboxBB.currentText()][1]()
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
                self.analog_data_container[key] = dictionary_analog[key][1]()
        
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
        
        self.digital_data_container = {}
        
        for key in dictionary_digital:
            if dictionary_digital[key][0] == 1: # if the signal line is added
                self.digital_data_container[key] = dictionary_digital[key][1]()
        
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
                
        xlabelhere_all = np.arange(self.reference_length)/int(self.textboxAA.currentText())
        plt.figure()
        for i in range(analogloopnum):
            if self.analogcontainer_array['Sepcification'][i] != 'galvosx'+'avgnum_'+str(int(self.textbox1H.currentText())): #skip the galvoX, as it is too intense
                plt.plot(xlabelhere_all, self.analogcontainer_array['Waveform'][i])
        for i in range(digitalloopnum):
            plt.plot(xlabelhere_all, self.digitalcontainer_array['Waveform'][i])
        plt.text(0.1, 1.1, 'Time lasted:'+str(xlabelhere_all[-1])+'s', fontsize=12)
        plt.show()
        
        self.readinchan = []
        
        if int(self.textbox111A.currentText()) == 1:
            self.readinchan.append('PMT')
        if int(self.textbox222A.currentText()) == 1:
            self.readinchan.append('Vp')
        if int(self.textbox333A.currentText()) == 1:
            self.readinchan.append('Ip')       
        
        print(self.readinchan)
        
        #execute(int(self.textboxAA.currentText()), self.analogcontainer_array, self.digitalcontainer_array, self.readinchan)
        return self.analogcontainer_array, self.digitalcontainer_array, self.readinchan

        
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainwin = adgenerator()
        mainwin.show()
        app.exec_()
    run_app()