from plugin import Plugin
from widget_helpers import radio_filler, spinbox_slider

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGroupBox, QLayout,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QStackedLayout,
                             QFileDialog, QButtonGroup,
                             QSizePolicy,
                             )
from PyQt5.QtCore import QDir, pyqtSignal, QObject, Qt

import cv2 as cv
import numpy as np


statusbar_message = 'detect edges'

def getInstance():
    instance = EdgeEnhance()
    instance.setSizeMarginSpacing()
    
    return instance

class EdgeEnhance(Plugin):
        
    def __init__(self, parent = None):
        
        super(EdgeEnhance, self).__init__()
        self.setObjectName('edge_detect') # should be plugin name and (plugin file name!)
    
        self.isSource = False
        self.inputImg = None
        self.outputImg = None
        self.needsGraphicsView = False
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        grid1 = QGridLayout()

        labels = ['Laplacian','Canny']
        groupBox1, self.bgrpDetectMethod = radio_filler('Detect Method', labels, 2)
        
        self.bgrpDetectMethod.buttonClicked.connect(self.radio_handler)
        
        self.stackedLayout = QStackedLayout()
        laplacianPage = QWidget()
        cannyPage     = QWidget()
        
        vbox2 = QVBoxLayout()
        labels = ['CV_8U', 'CV_16S', 'CV_64F']
        groupBox2, self.bgrpDepth = radio_filler('ddepth', labels, 3)
        tt = 'Desired depth of the destination image.'
        groupBox2.setToolTip(tt)
        
        self.bgrpDetectMethod.button(0).setChecked(True)
        self.bgrpDepth.button(0).setChecked(True)       
        # ~ self.opt8U.setChecked(True)
        
        grid2 = QGridLayout()
        self.dblKSize = QDoubleSpinBox(objectName = 'dblKSize')
        self.dblKSize.setValue(5)
        self.dblKSize.setMinimum(1)
        self.dblKSize.setMaximum(31)
        self.dblKSize.setSingleStep(2)
        tt = '''Aperture size used to compute the second-derivative filters.
                must be positive and odd'''
        self.dblKSize.setToolTip(tt)
        
        self.dblScale = QDoubleSpinBox(objectName = 'dblScale')
        self.dblScale.setValue(1)
        self.dblScale.setMinimum(0.1)
        self.dblScale.setSingleStep(.1)
        tt = '''Optional scale factor for the computed Laplacian values. 
                By default, no scaling is applied (i.e. scale = 1)'''
        self.dblScale.setToolTip(tt)
        
        self.dblDelta = QDoubleSpinBox(objectName = 'dblDelta')
        self.dblDelta.setValue(0)
        self.dblDelta.setMinimum(0.0)
        self.dblDelta.setSingleStep(.1)
        tt = '''Optional delta value that is added to the results prior to storing them in dst .'''
        self.dblDelta.setToolTip(tt)
        
        grid2.addWidget(QLabel('ksize'), 0, 0)
        grid2.addWidget(self.dblKSize, 0, 1)
        grid2.addWidget(QLabel('scale'), 0, 2)
        grid2.addWidget(self.dblScale, 0, 3)
        grid2.addWidget(QLabel('delta'), 0, 4)
        grid2.addWidget(self.dblDelta, 0, 5)
        
        vbox2.addWidget(groupBox2)
        vbox2.addLayout(grid2)
        laplacianPage.setLayout(vbox2)
        
        grid3 = QGridLayout()
        self.dblThreshold1 = QDoubleSpinBox(objectName = 'dblThreshold1')
        self.dblThreshold1.setMinimum(5)
        self.dblThreshold1.setMaximum(2000)
        self.dblThreshold1.setValue(100)
        self.dblThreshold1.setSingleStep(5)
        
        self.dblThreshold2 = QDoubleSpinBox(objectName = 'dblThreshold2')
        self.dblThreshold2.setMinimum(5)
        self.dblThreshold2.setMaximum(2000)
        self.dblThreshold2.setValue(200)
        self.dblThreshold2.setSingleStep(5)
        
        self.dblApertureSize = QDoubleSpinBox(objectName = 'dblApertureSize')
        self.dblApertureSize.setValue(3)
        self.dblApertureSize.setSingleStep(2)
        self.dblApertureSize.setMinimum(3)
        self.dblApertureSize.setMaximum(7)

        self.chkL2Gradient = QCheckBox('L2Gradient', objectName = 'L2Gradient')
        self.chkL2Gradient.setLayoutDirection(Qt.RightToLeft)

        grid3.addWidget(self.dblThreshold1,        0, 0)
        grid3.addWidget(QLabel('threshold1'), 0, 1)
        grid3.addWidget(self.dblThreshold2,        0, 2)
        grid3.addWidget(QLabel('threshold2'), 0, 3)
        grid3.addWidget(self.dblApertureSize,       1, 0)
        grid3.addWidget(QLabel('Aperture Size'), 1, 1)
        grid3.addWidget(self.chkL2Gradient,           1, 2, 1, 2)
        
        cannyPage.setLayout(grid3)
        
        self.stackedLayout.addWidget(laplacianPage)
        self.stackedLayout.addWidget(cannyPage)
        
        vbox1.addWidget(groupBox1)
        vbox1.addLayout(self.stackedLayout)
        vbox1.setStretch(0,1)
        vbox1.setStretch(1,2)

        self.setLayout(vbox1)
        # ~ self.img = None
        

    
    def radio_handler(self):
        print('self.bgrpDetectMethod.checkedId() ', self.bgrpDetectMethod.checkedId())
        self.stackedLayout.setCurrentIndex(self.bgrpDetectMethod.checkedId())
        
    def mainFunc(self, playing, scriptList, row):
        
        if self.inputImg is not None:
            
            if self.bgrpDetectMethod.checkedId() == 0: # Laplacian
                
                ksize = int(self.dblKSize.value())
            
                if   self.bgrpDepth.checkedId() == 0: # CV_8U
                    ddepth = cv.CV_8U
                    # ~ ddepth = -1
                if   self.bgrpDepth.checkedId() == 1: # CV_16S
                    ddepth = cv.CV_16S
                elif self.bgrpDepth.checkedId() == 2: # CV_64F
                    ddepth = cv.CV_64F
                
                scale = self.dblScale.value()
                delta = self.dblDelta.value()
                
                self.outputImg = cv.Laplacian(self.inputImg, 
                                                ddepth = ddepth, 
                                                ksize = ksize,
                                                scale = scale, 
                                                delta = delta)
            elif self.bgrpDetectMethod.checkedId() == 1: # Canny
                threshold1 = self.dblThreshold1.value()
                threshold2 = self.dblThreshold2.value()
                apertureSize = int(self.dblApertureSize.value())
                # ~ print('apertureSize ', apertureSize)
                L2gradient = self.chkL2Gradient.isChecked()
                
                self.outputImg = cv.Canny(self.inputImg,
                                            threshold1,
                                            threshold2,
                                            apertureSize = apertureSize,
                                            L2gradient = L2gradient)
