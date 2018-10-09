from plugin import Plugin
from widget_helpers import radio_filler, spinbox_slider

from PyQt5.QtWidgets import (QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QFileDialog, QButtonGroup,
                             QSizePolicy,
                             )
from PyQt5.QtCore import QDir, pyqtSignal, QObject

import cv2 as cv
import numpy as np


statusbar_message = 'convert OpenCV rgb image to grayscale'

def getInstance():
    return RGB2Gray()

class RGB2Gray(Plugin):
        
    def __init__(self, parent = None):
        
        super(RGB2Gray, self).__init__()
        
        self.setObjectName('rgb2gray') # should be plugin name

    
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()

    
    def mainFunc(self, playing, scriptList, row):
        
        if self.inputImg is not None:
            # convert to grayscale if image is color
            if self.inputImg.ndim == 3:
                self.outputImg = cv.cvtColor(self.inputImg, cv.COLOR_RGB2GRAY)
            else:
                self.outputImg = self.inputImg
    
