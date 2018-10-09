from plugin import Plugin
from widget_helpers import radio_filler, spinbox_slider

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QSpinBox,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QFileDialog, QButtonGroup,
                             QSizePolicy,
                             )
from PyQt5.QtCore import QDir, pyqtSignal, QObject

import cv2 as cv
import numpy as np


statusbar_message = 'keeps pixels in range of HSV values'

def getInstance():
    instance = InRange()
    instance.setSizeMarginSpacing()
    
    return instance

class InRange(Plugin):
        
    def __init__(self, parent = None):
        
        super(InRange, self).__init__()
        
        self.setObjectName('inrange') # should be plugin name
        
        
        # declare all parameter widgets below
        grid = QGridLayout()
        
        grid.addWidget(QLabel('H'),  0, 1)
        grid.addWidget(QLabel('S'),  0, 2)
        grid.addWidget(QLabel('V'),  0, 3)
        grid.addWidget(QLabel('LO'), 1, 0)
        grid.addWidget(QLabel('HI'), 2, 0)
        
        self.spinHLO = QSpinBox(minimum = 0, maximum = 255, 
                                value = 127, objectName = 'spinHLO')
        self.spinHHI = QSpinBox(minimum = 0, maximum = 255, 
                                value = 127, objectName = 'spinHHI')
        self.spinSLO = QSpinBox(minimum = 0, maximum = 255, 
                                value = 127, objectName = 'spinSLO')
        self.spinSHI = QSpinBox(minimum = 0, maximum = 255, 
                                value = 127, objectName = 'spinSHI')
        self.spinVLO = QSpinBox(minimum = 0, maximum = 255, 
                                value = 127, objectName = 'spinVLO')
        self.spinVHI = QSpinBox(minimum = 0, maximum = 255, 
                                value = 127, objectName = 'spinVHI')
        
        grid.addWidget(self.spinHLO, 1, 1)
        grid.addWidget(self.spinHHI, 2, 1)
        grid.addWidget(self.spinSLO, 1, 2)
        grid.addWidget(self.spinSHI, 2, 2)
        grid.addWidget(self.spinVLO, 1, 3)
        grid.addWidget(self.spinVHI, 2, 3)
        
        self.setLayout(grid)
        
    def mainFunc(self, playing, scriptList, row):
        
        if self.inputImg is not None:
            if self.inputImg.ndim == 3:  # assume it's RGB
                img = cv.copyMakeBorder(self.inputImg,0,0,0,0,cv.BORDER_REPLICATE)
                # ~ img = cv.cvtColor(img, cv.COLOR_RGB2HSV)
                # ~ img = cv.cvtColor(img, cv.COLOR_RGB2Lab)
                img = cv.cvtColor(img, cv.COLOR_RGB2Luv)
                
                HLO = self.spinHLO.value()
                HHI = self.spinHHI.value()
                SLO = self.spinSLO.value()
                SHI = self.spinSHI.value()
                VLO = self.spinVLO.value()
                VHI = self.spinVHI.value()
                
                self.outputImg = cv.inRange(img, 
                        (HLO, SLO, VLO),
                        (HHI, SHI, VHI))
            
        
    
    
