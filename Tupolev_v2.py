#c -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 20:54:40 2019

@author: xinmeng
    ============================== ==============================================
    
    For general experiments in Dr. Daan's lab
    
    ============================== ==============================================
"""
from __future__ import division
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPoint, QRect, QObject
from PyQt5.QtGui import QColor, QPen, QPixmap, QIcon, QTextCursor, QFont

from PyQt5.QtWidgets import (QWidget, QButtonGroup, QLabel, QSlider, QSpinBox, QDoubleSpinBox, QGridLayout, QPushButton, QGroupBox, 
                             QLineEdit, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QTabWidget, QCheckBox, QRadioButton, 
                             QFileDialog, QProgressBar, QTextEdit)

import pyqtgraph as pg

import sys

from GalvoWidget.pmt_thread import pmtimagingTest, pmtimagingTest_contour
from SampleStageControl.Stagemovement_Thread import StagemovementRelativeThread
from ThorlabsFilterSlider.Filtermovement_Thread import FiltermovementThread

import NIDAQ.wavegenerator

from NIDAQ.generalDaqerThread import (execute_analog_readin_optional_digital_thread, execute_tread_singlesample_analog,
                                execute_tread_singlesample_digital, execute_analog_and_readin_digital_optional_camtrig_thread, DaqProgressBar)

import os

import PatchClamp.ui_patchclamp_sealtest
import NIDAQ.Waveformer_for_screening
import GalvoWidget.PMTWidget
import ImageAnalysis.AnalysisWidget

import time
import pyqtgraph.console
from PI_ObjectiveMotor.focuser import PIMotor
import ui_camera_lab

#Setting graph settings
#"""
#pg.setConfigOption('background', 'w')
#pg.setConfigOption('foreground', 'k')
#pg.setConfigOption('useOpenGL', True)
#pg.setConfigOption('leftButtonPan', False)
#""" 
class EmittingStream(QObject): #https://stackoverflow.com/questions/8356336/how-to-capture-output-of-pythons-interpreter-and-show-in-a-text-widget
    textWritten = pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text)) # For updating notice from console.   

class Mainbody(QWidget):
    
    waveforms_generated = pyqtSignal(object, object, list, int)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.chdir(os.path.dirname(sys.argv[0]))# Set directory to current folder.
        self.setWindowIcon(QIcon('./Icons/Icon.png'))
        self.setFont(QFont("Arial"))
#        print(str(os.getcwd())+'Tupo')
#        sys.stdout = EmittingStream(textWritten = self.normalOutputWritten) # Uncomment here to link console output to textedit.
#        sys.stdout = sys.__stdout__
        #------------------------Initiating patchclamp class-------------------
        self.pmtTest = pmtimagingTest()
        self.pmtTest_contour = pmtimagingTest_contour()
        self.OC = 0.1
        #----------------------------------------------------------------------
        #----------------------------------GUI---------------------------------
        #----------------------------------------------------------------------
        self.setMinimumSize(1710,1200)
        self.setWindowTitle("Tupolev v1.0")
        self.layout = QGridLayout(self)
        # Setting tabs
        self.tabs = QTabWidget()
        self.Galvo_WidgetInstance = GalvoWidget.PMTWidget.PMTWidgetUI()
        self.Waveformer_WidgetInstance = NIDAQ.Waveformer_for_screening.WaveformGenerator()
        self.PatchClamp_WidgetInstance = PatchClamp.ui_patchclamp_sealtest.PatchclampSealTestUI()
        #self.tab4 = ui_camera_lab_5.CameraUI()
        self.Analysis_WidgetInstance = ImageAnalysis.AnalysisWidget.AnalysisWidgetUI()
        
        # Add tabs
        self.tabs.addTab(self.Galvo_WidgetInstance,"PMT imaging")
        self.tabs.addTab(self.Waveformer_WidgetInstance,"Waveform")
        self.tabs.addTab(self.PatchClamp_WidgetInstance,"Patch clamp")
        #self.tabs.addTab(self.tab4,"Camera")        
        self.tabs.addTab(self.Analysis_WidgetInstance,"Image analysis")
        
        self.savedirectory = os.path.join(os.path.expanduser("~"), "Desktop") #'M:/tnw/ist/do/projects/Neurophotonics/Brinkslab/Data'
        
        # Establishing communication betweeb widgets.
        self.Galvo_WidgetInstance.SignalForContourScanning.connect(self.PassVariable_GalvoWidget2Waveformer)
        self.Galvo_WidgetInstance.MessageBack.connect(self.normalOutputWritten)
        self.Analysis_WidgetInstance.MessageBack.connect(self.normalOutputWritten)
        
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------GUI for set directory------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #**************************************************************************************************************************************
        setdirectoryContainer = QGroupBox("Set directory")
        self.setdirectorycontrolLayout = QGridLayout()        
        
        self.saving_prefix = ''
        self.savedirectorytextbox = QLineEdit(self)
        self.savedirectorytextbox.setPlaceholderText('Saving directory')
        self.setdirectorycontrolLayout.addWidget(self.savedirectorytextbox, 0, 1)
        
        self.prefixtextbox = QLineEdit(self)
        self.prefixtextbox.setPlaceholderText('Prefix')
        self.setdirectorycontrolLayout.addWidget(self.prefixtextbox, 0, 0)
        
        #self.setdirectorycontrolLayout.addWidget(QLabel("Saving prefix:"), 0, 0)
        
        self.toolButtonOpenDialog = QtWidgets.QPushButton('Click me!')
        self.toolButtonOpenDialog.setStyleSheet("QPushButton {color:teal;background-color: pink; border-style: outset;border-radius: 5px;border-width: 2px;font: bold 14px;padding: 2px}"
                                                "QPushButton:pressed {color:yellow;background-color: pink; border-style: outset;border-radius: 5px;border-width: 2px;font: bold 14px;padding: 2px}")

        self.toolButtonOpenDialog.setObjectName("toolButtonOpenDialog")
        self.toolButtonOpenDialog.clicked.connect(self._open_file_dialog)
        
        self.setdirectorycontrolLayout.addWidget(self.toolButtonOpenDialog, 0, 2)
        
        setdirectoryContainer.setLayout(self.setdirectorycontrolLayout)
        setdirectoryContainer.setMaximumHeight(70)
        
        self.layout.addWidget(setdirectoryContainer, 0, 0)        
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------GUI for AOTF---------------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #**************************************************************************************************************************************
        AOTFcontrolContainer = QGroupBox("AOTF control")
        self.AOTFcontrolLayout = QGridLayout()
        
        self.slider640 = QSlider(Qt.Horizontal)
        self.slider640.setMinimum(0)
        self.slider640.setMaximum(500)
        self.slider640.setTickPosition(QSlider.TicksBothSides)
        self.slider640.setTickInterval(100)
        self.slider640.setSingleStep(1)
        self.line640 = QLineEdit(self)
        self.line640.setFixedWidth(60)
        self.slider640.sliderReleased.connect(lambda:self.updatelinevalue(640))
        self.slider640.sliderReleased.connect(lambda:self.execute_tread_single_sample_analog('640AO'))
        self.line640.returnPressed.connect(lambda:self.updatesider(640))
        
        self.ICON_off_AOTF = "./Icons/AOTF_off.png"
        self.AOTF_red_iconlabel = QLabel(self)
        self.AOTF_red_iconlabel.setPixmap(QPixmap(self.ICON_off_AOTF))
        self.AOTFcontrolLayout.addWidget(self.AOTF_red_iconlabel, 0, 0)
        
        self.switchbutton_640 = QPushButton("640")
        self.switchbutton_640.setStyleSheet("QPushButton {color:white;background-color: red; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:black;background-color: red; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")
        self.switchbutton_640.setCheckable(True)
        #self.holdingbutton.toggle()
        
        self.switchbutton_640.clicked.connect(lambda: self.execute_tread_single_sample_digital('640blanking'))
        self.switchbutton_640.clicked.connect(lambda: self.change_AOTF_icon('640blanking'))
        self.AOTFcontrolLayout.addWidget(self.switchbutton_640, 0, 1)
                
        self.slider532 = QSlider(Qt.Horizontal)
        self.slider532.setMinimum(0)
        self.slider532.setMaximum(500)
        self.slider532.setTickPosition(QSlider.TicksBothSides)
        self.slider532.setTickInterval(100)
        self.slider532.setSingleStep(1)
        self.line532 = QLineEdit(self)
        self.line532.setFixedWidth(60)
        self.slider532.sliderReleased.connect(lambda:self.updatelinevalue(532))
        self.slider532.sliderReleased.connect(lambda:self.execute_tread_single_sample_analog('532AO'))
        self.line532.returnPressed.connect(lambda:self.updatesider(532))
        
        self.AOTF_green_iconlabel = QLabel(self)
        self.AOTF_green_iconlabel.setPixmap(QPixmap(self.ICON_off_AOTF))
        self.AOTFcontrolLayout.addWidget(self.AOTF_green_iconlabel, 1, 0)
        
        self.switchbutton_532 = QPushButton("532")
        self.switchbutton_532.setStyleSheet("QPushButton {color:white;background-color: green; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:black;background-color: green; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")
        self.switchbutton_532.setCheckable(True)
        #self.holdingbutton.toggle()
        
        self.switchbutton_532.clicked.connect(lambda: self.execute_tread_single_sample_digital('532blanking'))
        self.switchbutton_532.clicked.connect(lambda: self.change_AOTF_icon('532blanking'))
        self.AOTFcontrolLayout.addWidget(self.switchbutton_532, 1, 1)
        
        self.slider488 = QSlider(Qt.Horizontal)
        self.slider488.setMinimum(0)
        self.slider488.setMaximum(500)
        self.slider488.setTickPosition(QSlider.TicksBothSides)
        self.slider488.setTickInterval(100)
        self.slider488.setSingleStep(1)
        self.line488 = QLineEdit(self)
        self.line488.setFixedWidth(60)
        self.slider488.sliderReleased.connect(lambda:self.updatelinevalue(488))
        self.slider488.sliderReleased.connect(lambda:self.execute_tread_single_sample_analog('488AO'))
        self.line488.returnPressed.connect(lambda:self.updatesider(488))
        
        self.AOTF_blue_iconlabel = QLabel(self)
        self.AOTF_blue_iconlabel.setPixmap(QPixmap(self.ICON_off_AOTF))
        self.AOTFcontrolLayout.addWidget(self.AOTF_blue_iconlabel, 2, 0)
        
        self.switchbutton_488 = QPushButton("488")
        self.switchbutton_488.setStyleSheet("QPushButton {color:white;background-color: blue; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:black;background-color: blue; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")
        self.switchbutton_488.setCheckable(True)
        #self.holdingbutton.toggle()
        
        self.switchbutton_488.clicked.connect(lambda: self.execute_tread_single_sample_digital('488blanking'))
        self.switchbutton_488.clicked.connect(lambda: self.change_AOTF_icon('488blanking'))
        self.AOTFcontrolLayout.addWidget(self.switchbutton_488, 2, 1)        
        
        self.AOTFcontrolLayout.addWidget(self.slider640, 0, 2)
        self.AOTFcontrolLayout.addWidget(self.line640, 0, 3)
        self.AOTFcontrolLayout.addWidget(self.slider532, 1, 2)
        self.AOTFcontrolLayout.addWidget(self.line532, 1, 3)
        self.AOTFcontrolLayout.addWidget(self.slider488, 2, 2)
        self.AOTFcontrolLayout.addWidget(self.line488, 2, 3)
        
        AOTFcontrolContainer.setLayout(self.AOTFcontrolLayout)
        AOTFcontrolContainer.setMaximumHeight(300)
        self.layout.addWidget(AOTFcontrolContainer, 1, 0)
        
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------GUI for Stage--------------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #**************************************************************************************************************************************
        stagecontrolContainer = QGroupBox("Stage control")
        self.stagecontrolLayout = QGridLayout()
        
        self.stage_upwards = QPushButton("↑")
        self.stage_upwards.setStyleSheet("QPushButton {color:white;background-color: Olive; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        self.stagecontrolLayout.addWidget(self.stage_upwards, 1, 2)
        self.stage_upwards.clicked.connect(lambda: self.sample_stage_move_upwards())
        self.stage_upwards.setShortcut('w')
        
        self.stage_left = QPushButton("←")
        self.stage_left.setStyleSheet("QPushButton {color:white;background-color: Olive; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        self.stagecontrolLayout.addWidget(self.stage_left, 2, 1)
        self.stage_left.clicked.connect(lambda: self.sample_stage_move_leftwards())
        self.stage_left.setShortcut('a')
        
        self.stage_right = QPushButton("→")
        self.stage_right.setStyleSheet("QPushButton {color:white;background-color: Olive; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        self.stagecontrolLayout.addWidget(self.stage_right, 2, 3)
        self.stage_right.clicked.connect(lambda: self.sample_stage_move_rightwards())
        self.stage_right.setShortcut('d')
        
        self.stage_down = QPushButton("↓")
        self.stage_down.setStyleSheet("QPushButton {color:white;background-color: Olive; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        self.stagecontrolLayout.addWidget(self.stage_down, 2, 2)
        self.stage_down.clicked.connect(lambda: self.sample_stage_move_downwards())
        self.stage_down.setShortcut('s')
        
        self.stage_speed = QSpinBox(self)
        self.stage_speed.setMinimum(-10000)
        self.stage_speed.setMaximum(10000)
        self.stage_speed.setValue(300)
        self.stage_speed.setSingleStep(100)        
        self.stagecontrolLayout.addWidget(self.stage_speed, 0, 1)
        self.stagecontrolLayout.addWidget(QLabel("Moving speed:"), 0, 0)
        
        self.led_Label = QLabel("White LED: ")
        self.stagecontrolLayout.addWidget(self.led_Label, 0, 2)
        
        self.switchbutton_LED = QPushButton()
        #self.switchbutton_LED.setStyleSheet("QPushButton {color:white;background-color: blue; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            #"QPushButton:pressed {color:black;background-color: blue; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")
        self.switchbutton_LED.setCheckable(True)
        self.switchbutton_LED.setIcon(QIcon('./Icons/AOTF_off.png'))
        #self.holdingbutton.toggle()
        
        self.switchbutton_LED.clicked.connect(lambda: self.execute_tread_single_sample_digital('LED'))
        self.switchbutton_LED.clicked.connect(lambda: self.change_AOTF_icon('LED'))
        self.stagecontrolLayout.addWidget(self.switchbutton_LED, 0, 3)
        
        self.stage_current_pos_Label = QLabel("Current position: ")
        self.stagecontrolLayout.addWidget(self.stage_current_pos_Label, 1, 0)
        
        self.stage_goto = QPushButton("Move to:")
        self.stage_goto.setStyleSheet("QPushButton {color:white;background-color: blue; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        self.stagecontrolLayout.addWidget(self.stage_goto, 3, 0)
        self.stage_goto.clicked.connect(lambda: self.sample_stage_move_towards())
        
        self.stage_goto_x = QLineEdit(self)
        self.stage_goto_x.setFixedWidth(60)
        self.stagecontrolLayout.addWidget(self.stage_goto_x, 3, 1)
        
        self.stage_goto_y = QLineEdit(self)
        self.stage_goto_y.setFixedWidth(60)
        self.stagecontrolLayout.addWidget(self.stage_goto_y, 3, 2)
        
        self.stagecontrolLayout.addWidget(QLabel('Click arrow to enable WASD keyboard control'), 4, 0, 1, 3)
        
        stagecontrolContainer.setLayout(self.stagecontrolLayout)
        stagecontrolContainer.setMaximumHeight(300)
        self.layout.addWidget(stagecontrolContainer, 2, 0)        
        
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------GUI for Filter movement----------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #**************************************************************************************************************************************
        ND_filtercontrolContainer = QGroupBox("ND filter control")
        self.NDfiltercontrolLayout = QGridLayout()
        
        bGBackupFromIntExt = QButtonGroup(self)

        self.filter1_pos0 = QPushButton('0')
        self.filter1_pos0.setCheckable(True)
        bGBackupFromIntExt.addButton(self.filter1_pos0)
        self.NDfiltercontrolLayout.addWidget(self.filter1_pos0, 0, 1)
        self.filter1_pos0.clicked.connect(lambda: self.filter_move_towards("COM9", 0))

        self.filter1_pos1 = QPushButton('1')
        self.filter1_pos1.setCheckable(True)
        bGBackupFromIntExt.addButton(self.filter1_pos1)
        self.NDfiltercontrolLayout.addWidget(self.filter1_pos1, 0, 2)    
        self.filter1_pos1.clicked.connect(lambda: self.filter_move_towards("COM9", 1))
        
        self.filter1_pos2 = QPushButton('2')
        self.filter1_pos2.setCheckable(True)
        bGBackupFromIntExt.addButton(self.filter1_pos2)
        self.NDfiltercontrolLayout.addWidget(self.filter1_pos2, 0, 3)
        self.filter1_pos2.clicked.connect(lambda: self.filter_move_towards("COM9", 2))
        
        self.filter1_pos3 = QPushButton('3')
        self.filter1_pos3.setCheckable(True)
        bGBackupFromIntExt.addButton(self.filter1_pos3)
        self.NDfiltercontrolLayout.addWidget(self.filter1_pos3, 0, 4)
        self.filter1_pos3.clicked.connect(lambda: self.filter_move_towards("COM9", 3)) 
        
        self.NDfiltercontrolLayout.addWidget(QLabel('Filter-1 pos: '), 0, 0)

        self.NDfiltercontrolLayout.addWidget(QLabel('Filter-2 pos: '), 1, 0)        
        bGBackupFromIntExt_1 = QButtonGroup(self)

        self.filter2_pos0 = QPushButton('0')
        self.filter2_pos0.setCheckable(True)
        bGBackupFromIntExt_1.addButton(self.filter2_pos0)
        self.NDfiltercontrolLayout.addWidget(self.filter2_pos0, 1, 1)
        self.filter2_pos0.clicked.connect(lambda: self.filter_move_towards("COM7", 0))

        self.filter2_pos1 = QPushButton('0.1')
        self.filter2_pos1.setCheckable(True)
        bGBackupFromIntExt_1.addButton(self.filter2_pos1)
        self.NDfiltercontrolLayout.addWidget(self.filter2_pos1, 1, 2)    
        self.filter2_pos1.clicked.connect(lambda: self.filter_move_towards("COM7", 1))
        
        self.filter2_pos2 = QPushButton('0.3')
        self.filter2_pos2.setCheckable(True)
        bGBackupFromIntExt_1.addButton(self.filter2_pos2)
        self.NDfiltercontrolLayout.addWidget(self.filter2_pos2, 1, 3)
        self.filter2_pos2.clicked.connect(lambda: self.filter_move_towards("COM7", 2))
        
        self.filter2_pos3 = QPushButton('0.5')
        self.filter2_pos3.setCheckable(True)
        bGBackupFromIntExt_1.addButton(self.filter2_pos3)
        self.NDfiltercontrolLayout.addWidget(self.filter2_pos3, 1, 4)
        self.filter2_pos3.clicked.connect(lambda: self.filter_move_towards("COM7", 3)) 
       
        ND_filtercontrolContainer.setLayout(self.NDfiltercontrolLayout)
        ND_filtercontrolContainer.setMaximumHeight(200)
        self.layout.addWidget(ND_filtercontrolContainer, 3, 0) 

        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------GUI for Objective Motor----------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #**************************************************************************************************************************************
        
        # Movement based on relative positions.
        ObjMotorcontrolContainer = QGroupBox("Objective motor control")
        self.ObjMotorcontrolLayout = QGridLayout()
        
        self.ObjMotor_connect = QPushButton("Connect")
        self.ObjMotor_connect.setStyleSheet("QPushButton {color:white;background-color: green; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        self.ObjMotorcontrolLayout.addWidget(self.ObjMotor_connect, 0, 0)
        self.ObjMotor_connect.clicked.connect(lambda: self.ConnectMotor())       
        
        self.ObjMotor_disconnect = QPushButton("Disconnect")
        self.ObjMotor_disconnect.setStyleSheet("QPushButton {color:white;background-color: firebrick; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        self.ObjMotorcontrolLayout.addWidget(self.ObjMotor_disconnect, 0, 1)
        self.ObjMotor_disconnect.clicked.connect(lambda: self.DisconnectMotor()) 
        
        self.ObjMotor_upwards = QPushButton("↑")
        self.ObjMotor_upwards.setStyleSheet("QPushButton {color:white;background-color: teal; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        self.ObjMotorcontrolLayout.addWidget(self.ObjMotor_upwards, 2, 2)
        self.ObjMotor_upwards.clicked.connect(lambda: self.Motor_move_upwards())
#        self.ObjMotor_upwards.setShortcut('w')
        
        self.ObjMotor_down = QPushButton("↓")
        self.ObjMotor_down.setStyleSheet("QPushButton {color:white;background-color: teal; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        self.ObjMotorcontrolLayout.addWidget(self.ObjMotor_down, 3, 2)
        self.ObjMotor_down.clicked.connect(lambda: self.Motor_move_downwards())
#        self.stage_down.setShortcut('s')
        
        self.ObjMotor_target = QDoubleSpinBox(self)
        self.ObjMotor_target.setMinimum(-10000)
        self.ObjMotor_target.setMaximum(10000)
        self.ObjMotor_target.setDecimals(6)
#        self.ObjMotor_target.setValue(3.45)
        self.ObjMotor_target.setSingleStep(0.001)        
        self.ObjMotorcontrolLayout.addWidget(self.ObjMotor_target, 1, 1)
        self.ObjMotorcontrolLayout.addWidget(QLabel("Target:"), 1, 0)
        
        self.ObjMotor_current_pos_Label = QLabel("Current position: ")
        self.ObjMotorcontrolLayout.addWidget(self.ObjMotor_current_pos_Label, 2, 0)
        
        self.ObjMotor_goto = QPushButton("Move")
        self.ObjMotor_goto.setStyleSheet("QPushButton {color:white;background-color: blue; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}"
                                            "QPushButton:pressed {color:red;background-color: white; border-style: outset;border-radius: 10px;border-width: 2px;font: bold 14px;padding: 6px}")        
        self.ObjMotorcontrolLayout.addWidget(self.ObjMotor_goto, 1, 2)
        self.ObjMotor_goto.clicked.connect(self.MoveMotor)
        
        self.ObjMotor_step = QDoubleSpinBox(self)
        self.ObjMotor_step.setMinimum(-10000)
        self.ObjMotor_step.setMaximum(10000)
        self.ObjMotor_step.setDecimals(6)
        self.ObjMotor_step.setValue(0.001)
        self.ObjMotor_step.setSingleStep(0.001)        
        self.ObjMotorcontrolLayout.addWidget(self.ObjMotor_step, 3, 1)
        self.ObjMotorcontrolLayout.addWidget(QLabel("Step: "), 3, 0)  
        
        ObjMotorcontrolContainer.setLayout(self.ObjMotorcontrolLayout)
        ObjMotorcontrolContainer.setMaximumHeight(300)
        self.layout.addWidget(ObjMotorcontrolContainer, 4, 0)          
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------GUI for camera button------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------  
        #**************************************************************************************************************************************        
        self.open_cam = QPushButton('Open Camera')
        self.open_cam.clicked.connect(self.open_camera)
        self.layout.addWidget(self.open_cam,5,0)
        
        self.console_text_edit = QTextEdit()
        self.console_text_edit.setFontItalic(True)
        self.console_text_edit.setPlaceholderText('Notice board from console.')
        self.console_text_edit.setMaximumHeight(200)
        self.layout.addWidget(self.console_text_edit, 6, 0)
        
        #**************************************************************************************************************************************        
        #self.setLayout(pmtmaster)
        self.layout.addWidget(self.tabs, 0, 1, 8, 4)
        self.setLayout(self.layout)
        

        '''
        ***************************************************************************************************************************************
        ************************************************************END of GUI*****************************************************************
        '''
        
    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__
        
        '''
        ***************************************************************************************************************************************
        ************************************************************ Functions to pass variables across widges ********************************
        '''        
    def PassVariable_GalvoWidget2Waveformer(self, contour_point_number, Daq_sample_rate_pmt, time_per_contour, handle_viewbox_coordinate_x, handle_viewbox_coordinate_y):
        
        self.Waveformer_WidgetInstance.galvo_contour_label_1.setText("Points in contour: %.d" % contour_point_number)
        self.Waveformer_WidgetInstance.galvo_contour_label_2.setText("Sampling rate: %.d" % Daq_sample_rate_pmt)
        self.Waveformer_WidgetInstance.Daq_sample_rate_pmt = Daq_sample_rate_pmt
        self.Waveformer_WidgetInstance.handle_viewbox_coordinate_position_array_expanded_x = handle_viewbox_coordinate_x
        self.Waveformer_WidgetInstance.handle_viewbox_coordinate_position_array_expanded_y = handle_viewbox_coordinate_y
        self.Waveformer_WidgetInstance.time_per_contour = time_per_contour
        
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------Fuc for AOTF---------------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #**************************************************************************************************************************************
    def updatelinevalue(self, wavelength):
        if wavelength == 640:
            self.line640.setText(str(self.slider640.value()/100))
        if wavelength == 532:
            self.line532.setText(str(self.slider532.value()/100))
        if wavelength == 488:
            self.line488.setText(str(self.slider488.value()/100))
        
    def updateslider(self, wavelength):
        #self.slider640.setSliderPosition(int(float((self.line640.text())*100)))
        if wavelength == 640:
            self.slider640.setValue(int(float(self.line640.text())*100))
        if wavelength == 532:
            self.slider532.setValue(int(float(self.line532.text())*100))
        if wavelength == 488:
            self.slider488.setValue(int(float(self.line488.text())*100))
            
    def execute_tread_single_sample_analog(self, channel):
        if channel == '640AO':
            execute_tread_singlesample_AOTF_analog = execute_tread_singlesample_analog()
            execute_tread_singlesample_AOTF_analog.set_waves(channel, self.slider640.value())
            execute_tread_singlesample_AOTF_analog.start()
        elif channel == '532AO':
            execute_tread_singlesample_AOTF_analog = execute_tread_singlesample_analog()
            execute_tread_singlesample_AOTF_analog.set_waves(channel, self.slider532.value())
            execute_tread_singlesample_AOTF_analog.start()
        elif channel == '488AO':
            execute_tread_singlesample_AOTF_analog = execute_tread_singlesample_analog()
            execute_tread_singlesample_AOTF_analog.set_waves(channel, self.slider488.value())
            execute_tread_singlesample_AOTF_analog.start()            
            
    def execute_tread_single_sample_digital(self, channel):
        if channel == '640blanking':
            if self.switchbutton_640.isChecked():
                execute_tread_singlesample_AOTF_digital = execute_tread_singlesample_digital()
                execute_tread_singlesample_AOTF_digital.set_waves(channel, 1)
                execute_tread_singlesample_AOTF_digital.start()
            else:
                execute_tread_singlesample_AOTF_digital = execute_tread_singlesample_digital()
                execute_tread_singlesample_AOTF_digital.set_waves(channel, 0)
                execute_tread_singlesample_AOTF_digital.start()
        elif channel == '532blanking':
            if self.switchbutton_532.isChecked():
                execute_tread_singlesample_AOTF_digital = execute_tread_singlesample_digital()
                execute_tread_singlesample_AOTF_digital.set_waves(channel, 1)
                execute_tread_singlesample_AOTF_digital.start()
            else:
                execute_tread_singlesample_AOTF_digital = execute_tread_singlesample_digital()
                execute_tread_singlesample_AOTF_digital.set_waves(channel, 0)
                execute_tread_singlesample_AOTF_digital.start()        
        elif channel == '488blanking':
            if self.switchbutton_488.isChecked():
                execute_tread_singlesample_AOTF_digital = execute_tread_singlesample_digital()
                execute_tread_singlesample_AOTF_digital.set_waves(channel, 1)
                execute_tread_singlesample_AOTF_digital.start()
            else:
                execute_tread_singlesample_AOTF_digital = execute_tread_singlesample_digital()
                execute_tread_singlesample_AOTF_digital.set_waves(channel, 0)
                execute_tread_singlesample_AOTF_digital.start()  
                
        elif channel == 'LED':
            if self.switchbutton_LED.isChecked():
                execute_tread_singlesample_AOTF_digital = execute_tread_singlesample_digital()
                execute_tread_singlesample_AOTF_digital.set_waves(channel, 1)
                execute_tread_singlesample_AOTF_digital.start()
            else:
                execute_tread_singlesample_AOTF_digital = execute_tread_singlesample_digital()
                execute_tread_singlesample_AOTF_digital.set_waves(channel, 0)
                execute_tread_singlesample_AOTF_digital.start() 
                
    def change_AOTF_icon(self, channel):
        if channel == '640blanking':
            if self.switchbutton_640.isChecked():
                self.AOTF_red_iconlabel.setPixmap(QPixmap('./Icons/AOTF_red_on.png'))
            else:
                self.AOTF_red_iconlabel.setPixmap(QPixmap(self.ICON_off_AOTF))
        elif channel == '532blanking':
            if self.switchbutton_532.isChecked():
                self.AOTF_green_iconlabel.setPixmap(QPixmap('./Icons/AOTF_green_on.png'))
            else:
                self.AOTF_green_iconlabel.setPixmap(QPixmap(self.ICON_off_AOTF))        
        elif channel == '488blanking':
            if self.switchbutton_488.isChecked():
                self.AOTF_blue_iconlabel.setPixmap(QPixmap('./Icons/AOTF_blue_on.png'))
            else:
                self.AOTF_blue_iconlabel.setPixmap(QPixmap(self.ICON_off_AOTF)) 
        elif channel == 'LED':
            if self.switchbutton_LED.isChecked():
                self.switchbutton_LED.setIcon(QIcon('./Icons/LED_on.png'))
            else:
                self.switchbutton_LED.setIcon(QIcon('./Icons/AOTF_off.png'))
                
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------Fucs for set directory-----------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #**************************************************************************************************************************************
    def _open_file_dialog(self):
        self.savedirectory = str(QtWidgets.QFileDialog.getExistingDirectory())
        self.savedirectorytextbox.setText(self.savedirectory)
        self.saving_prefix = str(self.prefixtextbox.text())
        
        # Set the savedirectory and prefix of Waveform widget in syn.
        self.tab2.savedirectory = self.savedirectory
        self.tab2.saving_prefix = self.saving_prefix
        
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------Fucs for stage movement----------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #**************************************************************************************************************************************        
    def sample_stage_move_upwards(self):
        self.sample_move_distance_yRel = int(self.stage_speed.value())
        stage_movement_thread = StagemovementRelativeThread(0, self.sample_move_distance_yRel)
        stage_movement_thread.current_position.connect(self.update_stage_current_pos)
        stage_movement_thread.start()
        time.sleep(0.5)
        stage_movement_thread.quit()
        stage_movement_thread.wait()
        
    def sample_stage_move_downwards(self):
        self.sample_move_distance_yRel = int(self.stage_speed.value())
        stage_movement_thread = StagemovementRelativeThread(0, -1*self.sample_move_distance_yRel)
        stage_movement_thread.current_position.connect(self.update_stage_current_pos)
        stage_movement_thread.start()
        time.sleep(0.5)
        stage_movement_thread.quit()
        stage_movement_thread.wait()

    def sample_stage_move_leftwards(self):
        self.sample_move_distance_xRel = int(self.stage_speed.value())
        stage_movement_thread = StagemovementRelativeThread(self.sample_move_distance_xRel, 0)
        stage_movement_thread.current_position.connect(self.update_stage_current_pos)
        stage_movement_thread.start()
        time.sleep(0.5)
        stage_movement_thread.quit()
        stage_movement_thread.wait()
        
    def sample_stage_move_rightwards(self):
        self.sample_move_distance_xRel = int(self.stage_speed.value())
        stage_movement_thread = StagemovementRelativeThread(-1*self.sample_move_distance_xRel, 0)
        stage_movement_thread.current_position.connect(self.update_stage_current_pos)
        stage_movement_thread.start()
        time.sleep(0.5)
        stage_movement_thread.quit()
        stage_movement_thread.wait()
        
    def sample_stage_move_towards(self):
        self.sample_move_x = int(float(self.stage_goto_x.text()))
        self.sample_move_y = int(float(self.stage_goto_y.text()))
        stage_movement_thread = StagemovementRelativeThread(self.sample_move_x, self.sample_move_y)
        stage_movement_thread.current_position.connect(self.update_stage_current_pos)
        stage_movement_thread.start()
        time.sleep(2)
        stage_movement_thread.quit()
        stage_movement_thread.wait()
        
    def update_stage_current_pos(self, current_pos):
        self.stage_current_pos = current_pos
        self.stage_current_pos_Label.setText('X:'+str(self.stage_current_pos[0])+' Y: '+str(self.stage_current_pos[1]))
        
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------Fucs for filter movement---------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #************************************************************************************************************************************** 
    def filter_move_towards(self, COMport, pos):
        filter_movement_thread = FiltermovementThread(COMport, pos)
        #filter_movement_thread.filtercurrent_position.connect(self.update_stage_current_pos)
        filter_movement_thread.start()
        time.sleep(1.5)
        filter_movement_thread.quit()
        filter_movement_thread.wait()

        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------Fucs for camera options---------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #************************************************************************************************************************************** 
    def open_camera(self):
        self.camWindow = ui_camera_lab.CameraUI()
        
        '''
        I set the roiwindow immeadiately to save time, however this funcion also 
        sets the ROI. This is why I clear the ROI afterwards.
        '''
        
        self.camWindow.setGeometry(QRect(100, 100, 600, 600))
        self.camWindow.show()
        
        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------Fucs for console display---------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #************************************************************************************************************************************** 
    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.console_text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.console_text_edit.setTextCursor(cursor)
        self.console_text_edit.ensureCursorVisible()        

        #**************************************************************************************************************************************
        #--------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------Fucs for Motor movement----------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------          
        #**************************************************************************************************************************************         
    def ConnectMotor(self):
        self.ObjMotor_connect.setEnabled(False)
        self.ObjMotor_disconnect.setEnabled(True)
        
        self.pi_device_instance = PIMotor()
        self.normalOutputWritten('Objective motor connected.'+'\n')
        
        self.ObjCurrentPos = self.pi_device_instance.pidevice.qPOS(self.pi_device_instance.pidevice.axes)
        self.ObjMotor_current_pos_Label.setText("Current position: {:.4f}".format(self.ObjCurrentPos['1'])) # Axis here is a string.
        self.ObjMotor_target.setValue(self.ObjCurrentPos['1'])
        
    def MoveMotor(self):
        
        pos = PIMotor.move(self.pi_device_instance.pidevice, self.ObjMotor_target.value())
        self.ObjCurrentPos = self.pi_device_instance.pidevice.qPOS(self.pi_device_instance.pidevice.axes)
        self.ObjMotor_current_pos_Label.setText("Current position: {:.4f}".format(self.ObjCurrentPos['1'])) # Axis here is a string.
        self.ObjMotor_target.setValue(self.ObjCurrentPos['1'])        
      
    def DisconnectMotor(self):
        self.ObjMotor_connect.setEnabled(True)
        self.ObjMotor_disconnect.setEnabled(False)
        
        PIMotor.CloseMotorConnection(self.pi_device_instance.pidevice)
        self.normalOutputWritten('Objective motor disconnected.'+'\n')
        
    def Motor_move_upwards(self):
        self.MotorStep = self.ObjMotor_step.value()
        pos = PIMotor.move(self.pi_device_instance.pidevice, (self.ObjCurrentPos['1'] + self.MotorStep))
        self.ObjCurrentPos = self.pi_device_instance.pidevice.qPOS(self.pi_device_instance.pidevice.axes)
        self.ObjMotor_current_pos_Label.setText("Current position: {:.4f}".format(self.ObjCurrentPos['1'])) # Axis here is a string.
        
    def Motor_move_downwards(self):
        self.MotorStep = self.ObjMotor_step.value()
        pos = PIMotor.move(self.pi_device_instance.pidevice, (self.ObjCurrentPos['1'] - self.MotorStep))
        self.ObjCurrentPos = self.pi_device_instance.pidevice.qPOS(self.pi_device_instance.pidevice.axes)
        self.ObjMotor_current_pos_Label.setText("Current position: {:.4f}".format(self.ObjCurrentPos['1'])) # Axis here is a string.

        
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        pg.setConfigOptions(imageAxisOrder='row-major')
        mainwin = Mainbody()
        mainwin.show()
        app.exec_()
    run_app()