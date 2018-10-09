
from plugin import Plugin

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QStackedLayout, QLayout,
                             QFileDialog, QButtonGroup,
                             QSizePolicy,
                             )
from PyQt5.QtCore import QDir, pyqtSignal, QObject
from widget_helpers import radio_filler

import cv2 as cv

cap = cv.VideoCapture(0)



statusbar_message = 'Load image from camera or hard disk'

def getInstance():
    instance = Binarize()
    instance.setSizeMarginSpacing()
    
    return instance

class Binarize(Plugin):
    
    def __init__(self, parent = None):
        
        super(Binarize, self).__init__()

        self.Params = {}
        
        self.setObjectName('binarize') # should be plugin name
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        
        labels = [ 'Global', 'Adaptive', 'Adaptive Gaussian']
        groupBox1, self.bgrpMethod = radio_filler('Binarization Method', labels)
        self.buttonGroupList.append(self.bgrpMethod)
        self.bgrpMethod.buttonClicked.connect(self.radio_handler)
        
        hbox1 = QHBoxLayout()
        self.chkInvert = QCheckBox('invert')
        self.chkInvert.setObjectName('chkInvert')
        self.chkInvert.setToolTip('swap black and white')
        self.dblMaxVal = QDoubleSpinBox()
        self.dblMaxVal.setObjectName('dblMaxVal')
        self.dblMaxVal.setRange(0.,255.)
        self.dblMaxVal.setValue(255)
        self.dblMaxVal.setToolTip('Non-zero value assigned to the pixels for which the condition is satisfied ')
        hbox1.addWidget(self.chkInvert)
        hbox1.addWidget(self.dblMaxVal)
        hbox1.addWidget(QLabel('maxval'))
        
        self.stackedLayout =QStackedLayout()
        
        page0 = QWidget() # global
        page1 = QWidget() # adaptive, gaussian mean

      
        hboxp0 = QHBoxLayout()
        self.dblThresh = QDoubleSpinBox()
        self.dblThresh.setObjectName('dblThresh')
        self.dblThresh.setRange(0.,255.)
        self.dblThresh.setValue(127.)
        self.dblThresh.setDecimals(0.0)
        hboxp0.addWidget(self.dblThresh)
        hboxp0.addWidget(QLabel('Threshold'))
        page0.setLayout(hboxp0)
           
        hboxp2 = QHBoxLayout()
        self.dblKSize = QDoubleSpinBox()
        self.dblKSize.setObjectName('dblKSize')
        self.dblKSize.setRange(3.,31.)
        self.dblKSize.setSingleStep(2.0)
        self.dblKSize.setValue(11.0)
        self.dblKSize.setDecimals(0.0)
        self.dblKSize.lineEdit().setReadOnly(True)
        self.dblKSize.setToolTip('''Size of a pixel neighborhood that is used to calculate a threshold
                                      value for the pixel: 3, 5, 7, and so on.''')
        self.dblC = QDoubleSpinBox()
        self.dblC.setObjectName('dblC')
        self.dblC.setRange(-10.,10.)
        self.dblC.setSingleStep(1.0)
        self.dblC.setValue(2.0)
        self.dblC.setDecimals(0.0)
        self.dblC.setToolTip('''Constant subtracted from the mean or weighted mean. Normally, 
                           it is positive but may be zero or negative as well.''')
        
        hboxp2.addWidget(self.dblKSize)
        hboxp2.addWidget(QLabel('ksize'))
        hboxp2.addWidget(self.dblC)
        hboxp2.addWidget(QLabel('C'))
        page1.setLayout(hboxp2)
        
        self.stackedLayout.addWidget(page0)
        self.stackedLayout.addWidget(page1)

        vbox1.addWidget(groupBox1)
        vbox1.addLayout(hbox1)
        vbox1.addLayout(self.stackedLayout)

        self.setLayout(vbox1)
        
        # set all sizepolicy s to preferred
        for item in self.findChildren(QWidget):
            item.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            
        # set margins and spacing for all Layouts
        for item in self.findChildren(QLayout):
            item.setContentsMargins(0, 0, 0, 0)
            item.setSpacing(2)
        
        # set default method to Global
        self.bgrpMethod.button(0).setChecked(True)
        self.stackedLayout.setCurrentIndex(0)
        

    def radio_handler(self):
        if self.bgrpMethod.checkedId() == 0:
            self.stackedLayout.setCurrentIndex(0)
        elif self.bgrpMethod.checkedId() in [1,2]:
            self.stackedLayout.setCurrentIndex(1)


    def mainFunc(self, playing, scriptList, row):
        
        if self.inputImg is not None:
            if self.inputImg.ndim == 3:
                # need to convert to grayscale
                img = cv.cvtColor(self.inputImg, cv.COLOR_RGB2GRAY)
            else:
                img = self.inputImg
            
            threshold_type = self.chkInvert.isChecked()
            
            maxval = self.dblMaxVal.value()
            
            bid = self.bgrpMethod.checkedId()
            
            if bid == 0:  # Global
                threshold = int(self.dblThresh.value())
                retval, self.outputImg = cv.threshold(img, 
                                                threshold,
                                                maxval,
                                                threshold_type)
            elif bid in [1,2]:
                method = bid - 1  # cv.ADAPTIVE_THRESH_MEAN_C = 0, cv.ADAPTIVE_THRESH_GAUSSIAN_C = 1
                ksize = int(self.dblKSize.value())
                C     = int(self.dblC.value())
                self.outputImg = cv.adaptiveThreshold(img, 
                                                        maxval,
                                                        method,
                                                        threshold_type,
                                                        ksize,
                                                        C )


