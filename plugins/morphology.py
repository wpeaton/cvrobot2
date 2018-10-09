from plugin import Plugin
from widget_helpers import radio_filler, spinbox_slider

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGroupBox,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QStackedLayout, QButtonGroup)
from PyQt5.QtCore import QDir, pyqtSignal, QObject

import cv2 as cv
import numpy as np


statusbar_message = 'dilate, erode, open, close, gradient, tophat, blackhat, hitmiss'

def getInstance():
    instance = Morphology()
    instance.setSizeMarginSpacing()
    
    return instance

class Morphology(Plugin):
        
    def __init__(self, parent = None):
        
        super(Morphology, self).__init__()
        
        self.setObjectName('morphology') # should be plugin name

        # declare all parameter widgets below
        
        labels = ['Erode', 'Dilate', 'Open', 'Close', 
                  'Gradient', 'TopHat', 'BlackHat']
        tt = ['erodes away the boundaries of foreground object (Always try to keep foreground in white)',
              'makes the foreground fatter (Always try to keep foreground in white)',
              'erosion followed by dilation. It is useful in removing noise'  ,
            '''Dilation followed by Erosion. It is useful in closing small holes inside
               the foreground objects (white), or small black points on the object.''' ,
            '''the difference between dilation and erosion of an image. The result will look
               like the outline of the object. ''',     
              'the difference between input image and Opening of the image',
              'difference between the closing of the input image and input image.']
        #radio_filler(group_caption, labels, buttons_per_row = None, tool_tips = None):
        groupBox1, self.bgrpMorphMethod = radio_filler('Morphology Operation', labels, 2, tt)


        self.bgrpMorphMethod.button(0).setChecked(True)

        
        # ~ widget.bgrpMorphMethod.buttonClicked.connect(lambda: radiohandler(widget))
        vbox1 = QVBoxLayout()

        hbox1 = QHBoxLayout()
        
        hbox2 = QHBoxLayout()
        self.dblKSize = QDoubleSpinBox(objectName = 'dblKSize',
                            value = 5, minimum = 1, singleStep = 2)
        # ~ self.dblKSize.setObjectName('dblKSize')
        # ~ self.dblKSize.setValue(5)
        # ~ self.dblKSize.setMinimum(1)
        # ~ self.dblKSize.setSingleStep(2)
        tt = '''kernel size. must be positive and odd'''
        self.dblKSize.setToolTip(tt)
        
        hbox3 = QHBoxLayout()
        self.dblIter = QDoubleSpinBox(objectName = 'dblIter',
                            value = 1, minimum = 1, singleStep = 1)       
        hbox2.addWidget(QLabel('ksize'))
        hbox2.addWidget(self.dblKSize)
        hbox3.addWidget(QLabel('# iterations'))
        hbox3.addWidget(self.dblIter)
        
        labels = ['Rectangle', 'Circle', 'Cross']
        gbcap = 'Morphology Shape'
        groupBox2, self.bgrpMorphShape = radio_filler(gbcap, labels, 2)
        
        self.bgrpMorphShape.button(0).setChecked(True)
        
        vbox1.addLayout(hbox2)
        vbox1.addLayout(hbox3)
        vbox1.addWidget(groupBox2)
        vbox1.setStretch(0,1)
        vbox1.setStretch(1,1)
        vbox1.setStretch(2,3)


        hbox1.addWidget(groupBox1)
        hbox1.addLayout(vbox1)
        
        self.setLayout(hbox1)
        
        
    def mainFunc(self, playing, scriptList, row):
        
        if self.inputImg is not None:
            
            ksize = int(self.dblKSize.value())
            iterations = int(self.dblIter.value())
            
            if   self.bgrpMorphShape.checkedId() == 0: # Rectangle
                kernel = cv.getStructuringElement(cv.MORPH_RECT, (ksize,ksize))
            elif self.bgrpMorphShape.checkedId() == 1: # Ellipse
                kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (ksize,ksize))
            elif self.bgrpMorphShape.checkedId() == 2: # Cross
                kernel = cv.getStructuringElement(cv.MORPH_CROSS, (ksize,ksize))
            
            # ~ print()
            if self.bgrpMorphMethod.checkedId() == 0: # Erode
                op = cv.MORPH_ERODE
            if self.bgrpMorphMethod.checkedId() == 1: # Dilate
                op = cv.MORPH_DILATE
            if self.bgrpMorphMethod.checkedId() == 2: # Open
                op = cv.MORPH_OPEN
            if self.bgrpMorphMethod.checkedId() == 3: # Close
                op = cv.MORPH_CLOSE
            if self.bgrpMorphMethod.checkedId() == 4: # Gradient
                op = cv.MORPH_GRADIENT
            if self.bgrpMorphMethod.checkedId() == 5: # TopHat
                op = cv.MORPH_TOPHAT
            if self.bgrpMorphMethod.checkedId() == 6: # BlackHat
                op = cv.MORPH_BLACKHAT
            
            self.outputImg = cv.morphologyEx(self.inputImg, op, kernel,
                                iterations = iterations)
