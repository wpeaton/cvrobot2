
from plugin import Plugin

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QSpinBox, QSlider,
                             QRadioButton, QLineEdit, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QStackedLayout,
                             QFileDialog, QButtonGroup,
                             QSizePolicy,
                             )
from PyQt5.QtCore import QDir, pyqtSignal, QObject, Qt


import cv2 as cv
import numpy as np

from widget_helpers import radio_filler, spinbox_slider

def getInstance():
    ''' provides easy way for plugin finder to get an instance of this
        particular plugin
    '''
    instance = MovingAverage()
    instance.setSizeMarginSpacing()
    return instance
    
# keep statusbar_message as module level variable
statusbar_message = 'display average over n frames. will take fps*n time to stabilize'

class MovingAverage(Plugin):
    def __init__(self, parent = None):
        
        super(MovingAverage, self).__init__()

        self.Params = {}
        
        self.setObjectName('moving_average') # should be plugin name
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        self.spinFrames = QSpinBox(objectName = 'spinFrames')
        hbox1 = spinbox_slider(self.spinFrames, label = 'num frames', 
                    orientation = 'horizontal', min_ = 1, max_ = 10, 
                   single_step = 1, default_value = 1)
               
        vbox1.addLayout(hbox1)

        self.setLayout(vbox1)
        # ~ widget.img = None
        
               
    def radio_handler(self):
        bid = self.bgrpMethod.checkedId()
        self.stackedLayout.setCurrentIndex(bid)
        self.stackedLayout.setCurrentIndex(bid)
        
    def mainFunc(self, playing, scriptList, row):
        #    dst = src1*alpha + src2*beta + gamma
        src1 = self.inputImg
        alpha = 1.0/float(self.spinFrames.value())
        
        if self.outputImg is not None:
            src2 = self.outputImg
        else:
            src2 = self.inputImg
        
        beta = 1.0 - alpha
        
        print('alpha: ', alpha, '  beta: ', beta)
        
        self.outputImg = cv.addWeighted(src1, alpha, src2, beta, 0.0)
                
