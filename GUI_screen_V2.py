# -*- coding: utf-8 -*-
"""
Created on Wed May  1 16:04:50 2019

@author: xinmeng
"""

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
from StagescanClass import Stagescan
#from stagescan_v3_UIclass import Stagescan

 
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
        
        self.textboxM = QComboBox()
        self.textboxM.addItems(['1','2','3','4','5'])
        Layout.addWidget(self.textboxM, 6, 1)
        Layout.addWidget(QLabel("average over:"), 6, 0)

        # Create a button in the window
        self.button1 = QPushButton('Show text', self)
        Layout.addWidget(self.button1, 7, 0)
        
        self.button2 = QPushButton('Start', self)
        Layout.addWidget(self.button2, 7, 1)
        
         
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
        
        textboxValue13 = self.textboxM.currentText()
        UI_averagenum = int(textboxValue13)
        
        self.S = Stagescan(UI_row_start, UI_row_end, UI_column_start, UI_column_end, UI_step, UI_Daq_sample_rate, UI_voltXMin, UI_voltXMax, UI_voltYMin, UI_voltYMax, UI_Value_xPixels, UI_Value_yPixels, UI_averagenum)
        self.S.start()
            
if __name__ == "__main__":
    def run_app():
        app = QtWidgets.QApplication(sys.argv)
        mainWin = MainWindow()
        mainWin.show()
        app.exec_()
    run_app()