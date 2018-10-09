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


statusbar_message = 'equalize brightness of image'

def getInstance():
    instance = Equalize()
    instance.setSizeMarginSpacing()
    
    return instance

class Equalize(Plugin):
        
    def __init__(self, parent = None):
        
        super(Equalize, self).__init__()
        
        self.setObjectName('equalize') # should be plugin name
        
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        
        labels = ['EqHist', 'CLAHE']
        groupBox, self.bgrpEqMethod = radio_filler('Equalization Method', labels, 
                                buttons_per_row = 2, tool_tips = None)
                                
        hbox1 = QHBoxLayout()
        self.dblClipLimit = QDoubleSpinBox()
        self.dblClipLimit.setObjectName('dblClipLimit')
        self.dblClipLimit.setMinimum(0.)
        self.dblClipLimit.setMaximum(200.)
        self.dblClipLimit.setValue(40.)
        self.dblClipLimit.setSingleStep(1)
        
        self.spinTileSize = QSpinBox()
        self.spinTileSize.setObjectName('spinTileSize')
        self.spinTileSize.setMinimum(1)
        self.spinTileSize.setMaximum(200)
        self.spinTileSize.setValue(8)
        self.spinTileSize.setSingleStep(1)
        
        hbox1.addWidget(self.dblClipLimit)
        hbox1.addWidget(QLabel('clipLimit'))
        hbox1.addWidget(self.spinTileSize)
        hbox1.addWidget(QLabel('tileGridSize'))
        
        self.chkHue = QCheckBox('Equalize Hue')
        self.chkHue.setObjectName('chkHue')
        self.chkSaturation = QCheckBox('Equalize Saturation')
        self.chkSaturation.setObjectName('chkSaturation')
        self.chkValue = QCheckBox('Equalize Value')
        self.chkValue.setObjectName('chkValue')
        # ~ label.setWordWrap(True)
        vbox1.addWidget(groupBox)
        vbox1.addLayout(hbox1)        
        vbox1.addWidget(self.chkHue)
        vbox1.addWidget(self.chkSaturation)
        vbox1.addWidget(self.chkValue)
        
        self.setLayout(vbox1)
        
        self.chkValue.setChecked(True)
        self.bgrpEqMethod.button(0).setChecked(True)

        
    def mainFunc(self, playing, scriptList, row):
        
        if self.inputImg is not None:
            # ~ img = self.inputImg.copy()
            img = cv.copyMakeBorder(self.inputImg,0,0,0,0,cv.BORDER_REPLICATE)
            
            # dst	=	cv.addWeighted(	src1, alpha, src2, beta, gamma[, dst[, dtype]]	)
            #dst=saturate(src1*alpha+src2*beta+gamma)
            
            if (self.chkHue.isChecked() or 
                self.chkSaturation.isChecked() or 
                self.chkValue.isChecked()):
                
                
                if self.bgrpEqMethod.checkedId() == 0:  
                    fxn = cv.equalizeHist
                elif self.bgrpEqMethod.checkedId() == 1:  # CLAHE
                    cL = self.dblClipLimit.value()
                    tgs = self.spinTileSize.value()
                    clahe = cv.createCLAHE(clipLimit = cL, tileGridSize=(tgs, tgs))
                    fxn = clahe.apply
                    
                if img.ndim == 3: # it's a color image. grayscale has no color. duh!
                    # -> HSV -> split -> equalize -> merge
                    img = cv.cvtColor(img, cv.COLOR_RGB2HSV)
                    # ~ img = cv.cvtColor(img, cv.COLOR_RGB2HLS)
                    # ~ img = cv.cvtColor(img, cv.COLOR_RGB2YCrCb)
                    # ~ img = cv.cvtColor(img, cv.COLOR_RGB2YUV)
                    split = cv.split(img)
                    if self.chkHue.isChecked():
                        # ~ split[0] = fxn(split[0])
                        imax = np.max(split[0])
                        imin = np.min(split[0])
                        alpha = 255/(imax - imin)
                        gamma = -imin*255/(imax-imin)
                        split[0] = cv.addWeighted( split[0], alpha, split[0], 0, gamma )
                    if self.chkSaturation.isChecked():
                        # ~ split[1] = fxn(split[1])
                        imax = np.max(split[1])
                        imin = np.min(split[1])
                        alpha = 255/(imax - imin)
                        gamma = -imin*255/(imax-imin)
                        split[1] = cv.addWeighted( split[1], alpha, split[1], 0, gamma )
                    if self.chkValue.isChecked():
                        # ~ split[2] = fxn(split[2])
                        imax = np.max(split[2])
                        imin = np.min(split[2])
                        alpha = 255/(imax - imin)
                        gamma = -imin*255/(imax-imin)
                        split[2] = cv.addWeighted( split[2], alpha, split[2], 0, gamma )
                    img = cv.merge(split)
                    img = cv.cvtColor(img, cv.COLOR_HSV2RGB)
                    # ~ img = cv.cvtColor(img, cv.COLOR_HLS2RGB)
                    # ~ img = cv.cvtColor(img, cv.COLOR_YCrCb2RGB)
                    # ~ img = cv.cvtColor(img, cv.COLOR_YUV2RGB)
                else:  # assume it's grayscale
                    # ~ clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                    img = fxn(img)
            
            self.outputImg = img
        
    
    
