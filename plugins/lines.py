from plugin import Plugin
from widget_helpers import radio_filler, spinbox_slider

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QButtonGroup )
# ~ from PyQt5.QtCore import QDir, QObject

import cv2 as cv
import numpy as np
import time


statusbar_message = 'Find lines using probabilistic Hough transform'

def getInstance():
    instance = Lines()
    instance.setSizeMarginSpacing()
    
    return instance

class Lines(Plugin):
        
    def __init__(self, parent = None):
        
        super(Lines, self).__init__()
        
        self.setObjectName('lines') # should be plugin name
    
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        hbox1 = QHBoxLayout()
        grid1 = QGridLayout()
        lblRho = QLabel('rho')
        self.dblRho = QDoubleSpinBox()
        self.dblRho.setObjectName('dblRho')
        self.dblRho.setValue(1.0)
        self.dblRho.setSingleStep(0.1)
        tt = 'Distance resolution of the accumulator in pixels'
        lblRho.setToolTip(tt)
        self.dblRho.setToolTip(tt)
        lblTheta = QLabel('theta')
        self.dblTheta = QDoubleSpinBox()
        self.dblTheta.setObjectName('dblTheta')
        tt = 'Angle resolution of the accumulator in degrees'
        lblTheta.setToolTip(tt)
        self.dblTheta.setToolTip(tt)
        self.dblTheta.setSingleStep(5)
        self.dblTheta.setMinimum(0)
        self.dblTheta.setMaximum(360)
        self.dblTheta.setValue(1)
        grid1.addWidget(lblRho,        0, 0)
        grid1.addWidget(self.dblRho,   0, 1)
        grid1.addWidget(lblTheta,      0, 2)
        grid1.addWidget(self.dblTheta, 0, 3)
        
        
        lblThreshold = QLabel('threshold')
        self.dblThreshold = QDoubleSpinBox()
        self.dblThreshold.setObjectName('dblThreshold')
        self.dblThreshold.setSingleStep(1)
        self.dblThreshold.setValue(50)
        self.dblThreshold.setMaximum(1000)
        tt = '<FONT COLOR = black>Accumulator threshold parameter. Only those lines are returned that get enough votes ( >threshold )</FONT>'
        lblThreshold.setToolTip(tt)
        self.dblThreshold.setToolTip(tt)
        lblMinLineLength = QLabel('minLineLength')
        self.dblMinLineLength = QDoubleSpinBox()
        self.dblMinLineLength.setObjectName('dblMinLineLength')
        self.dblMinLineLength.setSingleStep(10)
        self.dblMinLineLength.setValue(100)
        self.dblMinLineLength.setMaximum(2000)
        tt = '<FONT COLOR = black>Minimum line length. Line segments shorter than that are rejected.</FONT>'
        lblMinLineLength.setToolTip(tt)
        self.dblMinLineLength.setToolTip(tt)
        grid1.addWidget(lblThreshold,          1, 0)
        grid1.addWidget(self.dblThreshold,     1, 1)
        grid1.addWidget(lblMinLineLength,      1, 2)
        grid1.addWidget(self.dblMinLineLength, 1, 3)
        
        hbox3 = QHBoxLayout()
        lblMaxLineGap = QLabel('maxLineGap')
        self.dblMaxLineGap = QDoubleSpinBox()
        self.dblMaxLineGap.setObjectName('dblMaxLineGap')
        self.dblMaxLineGap.setSingleStep(10)
        self.dblMaxLineGap.setMaximum(2000)
        self.dblMaxLineGap.setValue(10)
        tt = '<FONT COLOR = black>Maximum allowed gap between points on the same line to link them</FONT>'
        self.dblMaxLineGap.setToolTip(tt)
        grid1.addWidget(lblMaxLineGap,      2, 0)
        grid1.addWidget(self.dblMaxLineGap, 2, 1)

        self.setLayout(grid1)
        # ~ self.img = None
    
    def mainFunc(self, playing, scriptList, row):
        
        if self.inputImg is not None:
            
            if self.inputImg.ndim == 3: # it's a color image. grayscale has no color. duh!
                img = cv.cvtColor(self.inputImg, cv.COLOR_RGB2GRAY)
            else:
                img = self.inputImg.copy()
                
            lines = cv.HoughLinesP(img, 
                                   rho = self.dblRho.value(),
                                   theta = self.dblTheta.value()*np.pi/180,
                                   threshold = int(self.dblThreshold.value()),
                                   minLineLength = self.dblMinLineLength.value(),
                                   maxLineGap = self.dblMaxLineGap.value() )
            
            self.outputImg = self.inputImg.copy()
            
            if lines is not None:
                print(len(lines), ' lines')
                for line in lines:
                    x1,y1,x2,y2 = line[0]
                    # ~ cv.line(self.outputImg,(x1,y1),(x2,y2),(0,255,0),2) # green lines
                    cv.line(self.outputImg,(x1,y1),(x2,y2),(255,255,255),4) # white lines
            else:
                print(time.time(), ':  no fucking lines. what kind of jive is this man?')


