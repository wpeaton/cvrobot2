
from plugin import Plugin
from widget_helpers import radio_filler, spinbox_slider

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QStackedLayout, QLayout,
                             QFileDialog, QButtonGroup,
                             QSizePolicy
                             )
from PyQt5.QtCore import QDir, pyqtSignal, QObject

import cv2 as cv
import numpy as np


statusbar_message = 'Find circular or partial circular features in a Grayscale image'

def getInstance():
    instance = Blur()
    
    return instance
    
class Blur(Plugin):
    def __init__(self, parent = None):
        
        super(Blur, self).__init__()
        
        self.setObjectName('blur') # should be plugin name
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        vbox1.setSpacing(2)
        hbox1 = QHBoxLayout()
        hbox1.setSpacing(2)
            
        labels = ['box', 'Gaussian', 'Median', 'Bilateral']
        groupBox, self.bgrpBlurMethod = radio_filler('Blur Method', labels, 
                                buttons_per_row = 2, tool_tips = None)
        self.bgrpBlurMethod.buttonClicked.connect(self.radio_handler)
        
        self.stackedLayout = QStackedLayout()
        self.boxPage      = QWidget()
        self.gaussianPage = QWidget()
        self.medianPage   = QWidget()
        self.bilateralPage   = QWidget()
        
        gridLayout = QGridLayout()
        gridLayout.setSpacing(2)
        self.dblBoxKSize = QDoubleSpinBox()
        self.dblBoxKSize.setObjectName('dblBoxKSize')
        self.dblBoxKSize.setValue(5)
        self.dblBoxKSize.setMinimum(1)
        self.dblBoxKSize.setSingleStep(2)
        tt = '''blurring kernel size'''
        self.dblBoxKSize.setToolTip(tt)
        gridLayout.addWidget(QLabel('ksize'))
        gridLayout.addWidget(self.dblBoxKSize)
        self.boxPage.setLayout(gridLayout)
        
        gridLayout = QGridLayout()
        gridLayout.setSpacing(2)
        self.dblGaussianKSize = QDoubleSpinBox()
        self.dblGaussianKSize.setObjectName('dblGaussianKSize')
        self.dblGaussianKSize.setValue(5)
        self.dblGaussianKSize.setMinimum(1)
        self.dblGaussianKSize.setSingleStep(2)
        tt = '''blurring kernel size'''
        self.dblGaussianKSize.setToolTip(tt)
        self.dblSigma = QDoubleSpinBox()
        self.dblSigma.setObjectName('dblSigma')
        self.dblSigma.setValue(0)
        tt = '''Gaussian kernel standard deviation.  If sigma is zero, it is computed from ksize
                (see getGaussianKernel for details);'''
        self.dblSigma.setToolTip(tt)
        self.dblSigma.setSingleStep(.1)
        gridLayout.addWidget(QLabel('ksize'), 0, 0)
        gridLayout.addWidget(self.dblGaussianKSize, 0 , 1)
        gridLayout.addWidget(QLabel('sigma'), 1 ,0 )
        gridLayout.addWidget(self.dblSigma, 1, 1)
        self.gaussianPage.setLayout(gridLayout)
        
        gridLayout = QGridLayout()
        gridLayout.setSpacing(2)
        self.dblMedianKSize = QDoubleSpinBox()
        self.dblMedianKSize.setObjectName('dblMedianKSize')
        self.dblMedianKSize.setValue(5)
        self.dblMedianKSize.setMinimum(1)
        self.dblMedianKSize.setSingleStep(2)
        tt = '''aperture linear size; it must be odd and greater than 1, 
                for example: 3, 5, 7 ... '''
        self.dblMedianKSize.setToolTip(tt)
        gridLayout.addWidget(QLabel('ksize'))
        gridLayout.addWidget(self.dblMedianKSize)
        self.medianPage.setLayout(gridLayout)
        
        gridLayout = QGridLayout()
        gridLayout.setSpacing(2)
        self.dblD = QDoubleSpinBox()
        self.dblD.setObjectName('dblD')
        self.dblD.setValue(5)
        self.dblD.setMinimum(1)
        self.dblD.setSingleStep(1)
        tt = '''Diameter of each pixel neighborhood that is used during filtering.
                If it is non-positive, it is computed from sigma'''
        self.dblD.setToolTip(tt)
        self.dblBSigma = QDoubleSpinBox()
        self.dblBSigma.setObjectName('dblBSigma')
        self.dblBSigma.setValue(50)
        tt = '''Filter sigma in the color space. A larger value of the parameter
                means that farther colors within the pixel neighborhood (see 
                sigmaSpace) will be mixed together, resulting in larger areas 
                of semi-equal color.'''
        self.dblBSigma.setToolTip(tt)
        self.dblBSigma.setSingleStep(.1)
        gridLayout.addWidget(QLabel('d'), 0, 0)
        gridLayout.addWidget(self.dblD, 0 , 1)
        gridLayout.addWidget(QLabel('sigma'), 1, 0)
        gridLayout.addWidget(self.dblBSigma ,1 ,1)
        self.bilateralPage.setLayout(gridLayout)
        
        self.stackedLayout.addWidget(self.boxPage)
        self.stackedLayout.addWidget(self.gaussianPage)
        self.stackedLayout.addWidget(self.medianPage)
        self.stackedLayout.addWidget(self.bilateralPage)
        
        vbox1.addWidget(groupBox)
        vbox1.addLayout(self.stackedLayout)

        self.setLayout(vbox1)
        # ~ self.img = None
        
        # set all sizepolicy s to preferred
        for item in self.findChildren(QWidget):
            item.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        # set margins and spacing for all Layouts
        for item in self.findChildren(QLayout):
            item.setContentsMargins(0, 0, 0, 0)
            item.setSpacing(2)
        
        self.bgrpBlurMethod.button(0).setChecked(True)
        
    def radio_handler(self):
        self.stackedLayout.setCurrentIndex(self.bgrpBlurMethod.checkedId())
    
    def mainFunc(self, playing, scriptList, row):
        
        if self.inputImg is not None:
            if self.stackedLayout.currentIndex() == 0:  # box blur
                ksize = int(self.dblBoxKSize.value())
                ksize = (ksize, ksize)
                # ~ anchor = (-1, -1)
                self.outputImg = cv.blur(self.inputImg,
                                           ksize)
            elif self.stackedLayout.currentIndex() == 1:  # Gaussian blur
                ksize = int(self.dblGaussianKSize.value())
                ksize = (ksize, ksize)
                sigma = self.dblSigma.value()
                # ~ anchor = (-1, -1)
                self.outputImg = cv.GaussianBlur(self.inputImg,
                                           ksize,
                                           sigma, sigma)
                                           
            elif self.stackedLayout.currentIndex() == 2:  # median blur
                ksize = int(self.dblMedianKSize.value())
                self.outputImg = cv.medianBlur(self.inputImg,
                                           ksize)
            
            elif self.stackedLayout.currentIndex() == 3:  # bilateral
                d = int(self.dblD.value())
                sigma = self.dblBSigma.value()
                self.outputImg = cv.bilateralFilter(self.inputImg, d, sigma, sigma)
            
