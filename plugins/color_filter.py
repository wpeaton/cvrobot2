from plugin import Plugin
from widget_helpers import radio_filler, spinbox_slider

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QFileDialog, QButtonGroup,
                             QSizePolicy,
                             )
from PyQt5.QtCore import QDir, pyqtSignal, QObject

import cv2 as cv
import numpy as np


statusbar_message = 'display selected RGB channels'

def getInstance():
    instance = ColorFilter()
    instance.setSizeMarginSpacing()
    
    return instance

class ColorFilter(Plugin):
        
    def __init__(self, parent = None):
        
        super(ColorFilter, self).__init__()
        
        self.setObjectName('color_filter') # should be plugin name
        
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        self.chkRed = QCheckBox('Show Red', objectName = 'chkRed')
        self.chkGreen = QCheckBox('Show Green', objectName = 'chkGreen')
        self.chkBlue = QCheckBox('Show Blue', objectName = 'chkBlue')
        # ~ label.setWordWrap(True)
        vbox1.addWidget(self.chkRed)
        vbox1.addWidget(self.chkGreen)
        vbox1.addWidget(self.chkBlue)
        
        self.setLayout(vbox1)
        
        self.chkRed.setChecked(False)
        self.chkGreen.setChecked(False)
        self.chkBlue.setChecked(False)

        
    def mainFunc(self, playing, scriptList, scriptPos):
        
        if self.inputImg is not None:
            # ~ img = self.inputImg.copy()
            img = cv.copyMakeBorder(self.inputImg,0,0,0,0,cv.BORDER_REPLICATE)
            
            if img.ndim == 3: # it's a color image. grayscale has no color. duh!
                # -> HSV -> split -> equalize -> merge
                split = cv.split(img)
                split[0] = self.chkRed.isChecked()*split[0]
                split[1] = self.chkGreen.isChecked()*split[1]
                split[2] = self.chkBlue.isChecked()*split[2]
                
                img = cv.merge(split)


            self.outputImg = img
        
    
    
