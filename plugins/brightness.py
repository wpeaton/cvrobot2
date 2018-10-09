
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
    instance = Brightness()
    instance.setSizeMarginSpacing()
    return instance
    
# keep statusbar_message as module level variable
statusbar_message = 'adjust brightness/contrast or gamma correction'

class Brightness(Plugin):
    def __init__(self, parent = None):
        
        super(Brightness, self).__init__()

        self.Params = {}
        
        self.setObjectName('brightness') # should be plugin name
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
               
        labels = ['brightness/contrast', 'gamma correction']
        groupBox1, self.bgrpMethod = radio_filler('Method', labels, 1)
        self.buttonGroupList.append(self.bgrpMethod)
        self.bgrpMethod.buttonClicked.connect(self.radio_handler)
        
        
        self.stackedLayout = QStackedLayout()
        brightPage = QWidget()
        gammaPage  = QWidget()
            
        vbox2 = QVBoxLayout()
        
        self.spinBrightness = QSpinBox()
        self.spinBrightness.setObjectName('spinBrightness')
        hbox1 = spinbox_slider(self.spinBrightness, label = 'brightness', 
                    orientation = 'horizontal', min_ = -127, max_ = 127, 
                   single_step = 1, default_value = 0)
        
        self.spinContrast = QSpinBox()
        self.spinContrast.setObjectName('spinContrast')
        hbox2 = spinbox_slider(self.spinContrast, label = 'contrast', 
                    orientation = 'horizontal', min_ = -127, max_ = 127, 
                   single_step = 1, default_value = 0)

        vbox2.addLayout(hbox1)
        vbox2.addLayout(hbox2)
        brightPage.setLayout(vbox2)
        
        self.dblGamma   = QDoubleSpinBox()
        self.dblGamma.setObjectName('dblGamma')
        hbox3 = spinbox_slider(self.dblGamma, label = 'gamma', 
                    orientation = 'horizontal', min_ = 0.1, max_ = 10., 
                   single_step = .01, default_value = 1, decimals = 2, log = True)
        # ~ self.dblGamma.setRange(.1,10.)
        # ~ self.dblGamma.setDecimals(2)
        # ~ self.dblGamma.setValue(1)
        # ~ self.dblGamma.setSingleStep(.01)
        # ~ self.dblGamma.setAccelerated(True)
        # ~ hbox3.addWidget(self.dblGamma)
        # ~ hbox3.addWidget(QLabel('gamma'))
        
        gammaPage.setLayout(hbox3)
        
        self.stackedLayout.addWidget(brightPage)
        self.stackedLayout.addWidget(gammaPage)
        
        vbox1.addWidget(groupBox1)
        vbox1.addLayout(self.stackedLayout)

        self.setLayout(vbox1)
        # ~ widget.img = None
        
        # set all sizepolicy s to preferred
        for item in self.findChildren(QWidget):
            item.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        # set brightness/contrast to default
        self.bgrpMethod.button(0).setChecked(True)
        self.stackedLayout.setCurrentIndex(0)
               
    def radio_handler(self):
        bid = self.bgrpMethod.checkedId()
        self.stackedLayout.setCurrentIndex(bid)
        self.stackedLayout.setCurrentIndex(bid)
        
    def mainFunc(self, playing, scriptList, row):
        
        if self.inputImg is not None:
            if self.bgrpMethod.button(0).isChecked():
                # ~ widget.stackedLayout.currentIndex() == 0:  # brightness/contrast
                b = self.spinBrightness.value()
                c = self.spinContrast.value()
                
                # from pippin.gimp.org/image_processing/chap_point.html
                #   new_value = (old_value - 0.5)*contrast + 0.5 + brightness
                #   but we need contrast to go from -127 to +127 not 0 to 1
                #   new_value = (old_value - 127)*(contrast/127 - 1) + 127 + brightness
                # simplifies to (old_value)*(contrast/127 - 1) - contrast + brightness
                img = None
                # ~ img = cv.convertScaleAbs(widget.inputImg, img, 1. + c/127., b - c)
                
                # there doesn't seem to be a good way to do a*x+b on an image
                # cv.convertScaleAbs comes close but does an absolute value which we don't want
                # 
                # so we'll use numpy and do it brute force.
                # ~ img = np.int16(self.inputImg)  # convert to signed 16 bit. hopefully 16 bits should be enough
                                                 # ~ # to handle overflow
                # ~ img = (1. + c/127.)*img + (b-c)
                # ~ img = np.clip(img, 0, 255)  # force all values to be between 0 and 255
                
                # ~ self.outputImg = np.uint8(img)
                
                #  ~ f = 259*(c + 255)/(255*(259-c))
                #  ~ self.outputImg = cv.addWeighted(self.inputImg, f, self.inputImg, 0, b + 127*(1-f))
                
                self.outputImg = cv.addWeighted(self.inputImg, c, self.inputImg, 0, b + 127*(1-b))
                
                self.outputImg = cv.addWeighted(self.inputImg, 1. + c/127., self.inputImg, 0, b*2-c)
                #  ~ self.outputImg = cv.addWeighted(self.inputImg, 1. + c/127., self.inputImg, 0, b-c/254)
                
                
            elif self.bgrpMethod.button(1).isChecked():
                # ~ widget.stackedLayout.currentIndex() == 1:  # gamma
                gamma = self.dblGamma.value()
                img = self.inputImg/255.0
                img = cv.pow(img, 1/gamma)
                self.outputImg = np.uint8(img*255)
