from plugin import Plugin
from widget_helpers import radio_filler, spinbox_slider

from PyQt5.QtWidgets import (QMainWindow, QGraphicsView,
                             QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGroupBox, QLayout, QSpinBox,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QStackedLayout,
                             QFileDialog, QButtonGroup,
                             QSizePolicy,
                             QGraphicsRectItem, QGraphicsEllipseItem,
                             QGraphicsScene,
                             )
from PyQt5.QtGui import ( QFont, QPen, QColor)
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPen, QColor, QWindow
from widget_helpers import radio_filler

import cv2 as cv
import numpy as np


font = cv.FONT_HERSHEY_SIMPLEX

statusbar_message = 'crop input image to circle from Hough circles'

def getInstance():
    instance = CropCircle()
    instance.setSizeMarginSpacing()
    
    return instance

class CropCircle(Plugin):
        
    def __init__(self, parent = None):
        
        super(CropCircle, self).__init__()
        
        
        self.setObjectName('crop_circle') # should be plugin name
           
        self.mask = None
        self.targetFname = ''
        
        # declare all parameter widgets below
        grid1 = QGridLayout()
        grid1.addWidget(QLabel('circles row'), 0, 0)
        self.spinCRow = QSpinBox(minimum = 1, objectName = 'spinCRow')
        grid1.addWidget(self.spinCRow,         0, 1)
        labels = ['black', 'white']
        groupBox1, self.bgrpBackground = radio_filler('Background Color', labels, 2)
        grid1.addWidget(groupBox1,  1, 0, 1, 2)

        self.setLayout(grid1)
        # ~ widget.img = None
        
    
    def mainFunc(self, playing, scriptList, row):
        
        if self.inputImg is not None:
            crow = self.spinCRow.value()
            circle = scriptList[crow-1][1].graphicsItems[0]
            x1 = circle.x()
            y1 = circle.y()
            x2 = x1 + circle.width()
            y2 = y1 + circle.height()
            r = circle.width()/2
            x0 = x1 + r
            y0 = y1 + r
            
            bg = self.bgrpBackground.checkedId()  # black is zero, white is 1
            
            
            if self.inputImg.ndim == 2:
                subimage = self.inputImg[y1:y2+1, x1:x2+1].copy()
                cv.circle(self.outputImg,(x0,y0),r,(0,255,0),2)
                if bg:
                    mask = 255*np.ones((circle.width(), circle.height()), dtype = np.uint8)
                else:
                    mask = np.zeros((circle.width(), circle.height()), dtype = np.uint8)
                mask = cv.circle(mask,(x0,y0),r, color = 1, thickness = -1)
            else:
                subimage = self.inputImg[y1:y2+1, x1:x2+1, :].copy()
                if bg:
                    mask = 255*np.ones((circle.width(), circle.height(), 3), dtype = np.uint8)
                else:
                    mask = np.zeros((circle.width(), circle.height(), 3), dtype = np.uint8)
                mask = cv.circle(mask,(x0,y0),r, color = (1,1,1), thickness = -1)
            
            self.outputImg = cv.multiply(subimage, mask)
            
            
