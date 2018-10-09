
from plugin import Plugin
from widget_helpers import radio_filler, spinbox_slider

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QSpinBox,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QStackedLayout, QLayout,
                             QFileDialog, QButtonGroup,
                             QSizePolicy
                             )
from PyQt5.QtCore import QDir, pyqtSignal, QObject

import cv2 as cv
import numpy as np


statusbar_message = 'Sharpen image using unsharp mask technique'

def getInstance():
    instance = Unsharp()
    instance.setSizeMarginSpacing()
    
    return instance
    
class Unsharp(Plugin):
    def __init__(self, parent = None):
        
        super(Unsharp, self).__init__()
        
        self.setObjectName('unsharp') # should be plugin name
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        
        # ~ self.sliderAmount = QSpinBox()
        
        # ~ slider1 = spinbox_slider(self.sliderAmount, label = 'amount', 
                                  # ~ min_ = 0, max_ = 300, single_step = 1, 
                                  # ~ default_value = 50)
        hbox1 = QHBoxLayout()
        self.dblAmount = QDoubleSpinBox(objectName = 'dblAmount')
        self.dblAmount.setMinimum(0)
        self.dblAmount.setMaximum(10)
        self.dblAmount.setSingleStep(.1)
        self.dblAmount.setValue(0.5)
        self.dblAmount.setAccelerated(True)
        hbox1.addWidget(self.dblAmount)
        hbox1.addWidget(QLabel('amount'))
            
        hbox2 = QHBoxLayout()
        self.spinKSize = QSpinBox(objectName = 'spinKSize')
        self.spinKSize.setMinimum(1)
        self.spinKSize.setMaximum(31)
        self.spinKSize.setSingleStep(2)
        self.spinKSize.setValue(5)
        hbox2.addWidget(self.spinKSize)
        hbox2.addWidget(QLabel('ksize'))
        
        
        vbox1.addLayout(hbox1)
        vbox1.addLayout(hbox2)
        

        self.setLayout(vbox1)
        # ~ self.img = None
        
    
    def mainFunc(self, playing, scriptList, row):
        
        if self.inputImg is not None:
            amount = self.dblAmount.value()
            ksize = self.spinKSize.value()
            ksize = (ksize, ksize)
            # ~ print('ksize ', ksize)
            sigma = 0
            # ~ anchor = (-1, -1)
            blur = cv.GaussianBlur(self.inputImg,
                                       ksize,
                                       sigma, sigma)
            self.outputImg = cv.addWeighted(self.inputImg,
                                            1 + amount,
                                            blur,
                                            -amount,
                                            0)
            
            
                                           
