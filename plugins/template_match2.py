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
from PyQt5.QtCore import QDir, pyqtSignal, QObject, QRectF, QLineF, QPointF
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPen, QColor, QWindow
from radio_filler import radio_filler

import cv2 as cv
import numpy as np

mainFunc = None

font = cv.FONT_HERSHEY_SIMPLEX

statusbar_message = 'draw target region and save to file'

def getInstance():
    instance = TemplateMatch()
    instance.setSizeMarginSpacing()
    
    return instance

class TemplateMatch(Plugin):
        
    def __init__(self, parent = None):
        
        super(TemplateMatch, self).__init__()
        
        
        self.setObjectName('templateMatch') # should be plugin name
           
        self.mask = None
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        label1 = QLabel('only TM_SQDIFF and TM_CCORR_NORMED support masks (circles and ellipses)')
        label1.setWordWrap(True)
        
        
        labels = ['TM_SQDIFF',         # 0
                  'TM_SQDIFF_NORMED',  # 1
                  'TM_CCORR',          # 2
                  'TM_CCORR_NORMED',   # 3
                  'TM_CCOEFF',         # 4
                  'TM_CCOEFF_NORMED',  # 5
                  ]
        groupBox1, self.bgrpMatchMethod = radio_filler('Match Method', labels, 2)
        self.bgrpMatchMethod.buttonClicked.connect(self.radio_handler)

        hbox1 = QHBoxLayout()
        self.dblThreshold = QDoubleSpinBox()

        self.groupBox2 = QGroupBox('inside target')
        self.groupBox2.setCheckable(True)
        grid1 = QGridLayout()
        self.spinRow = QSpinBox()
        self.spinRow.setMinimum(1)
        grid1.addWidget(QLabel('row'), 0, 0)
        grid1.addWidget(self.spinRow,  0, 1)
        self.groupBox2.setLayout(grid1)
        
        # set default method to cv.TM_CCOEFF_NORMED
        self.bgrpMatchMethod.button(cv.TM_CCOEFF_NORMED).setChecked(True)
        self.radio_handler()
        
        grid2 = QGridLayout()
        
        hbox1.addWidget(self.dblThreshold)
        hbox1.addWidget(QLabel('threshold'))
        grid2.addLayout(hbox1, 0, 0)
        grid2.addWidget(self.groupBox2, 0, 1, 2, 1) 
        
        
        self.lblResult = QLabel('score: ')
        grid2.addWidget(self.lblResult, 1, 0)
        
        vbox1.addWidget(label1)
        vbox1.addWidget(groupBox1)
        vbox1.addLayout(grid2)
        # ~ vbox1.setStretch(0, 1)
        # ~ vbox1.setStretch(1, 1)
        # ~ vbox1.setStretch(2, 2)
        # ~ vbox1.addWidget(self.lblResult)

        self.setLayout(vbox1)
        # ~ widget.img = None
        
    
    def mainFunc(self, playing, scriptList, row):
        
        self.spinRow.setMaximum(len(scriptList))
        
        if playing == False:
            # load target image from file
            if self.inputImg.ndim == 3:
                self.targetImg = cv.imread('target.png')
            else:
                self.targetImg = cv.imread('target.png', 0)
            print('target shape ', self.targetImg.shape)
    
        if self.inputImg is not None:
            img = self.inputImg.copy()
        #~ img = frame.copy()
        #~ img = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        #~ self.binarize(img)
        #~ print('img.dtype ', img.dtype)
        
            test_val = []
            numpass = 0
            
            
            template = self.targetImg
            #~ print(template.shape)
            #~ c, w, h = template.shape[::-1]
            h, w = template.shape[:2]
            
            # ~ method = cv.TM_SQDIFF
            # ~ method = cv.TM_CCOEFF_NORMED
            method = self.bgrpMatchMethod.checkedId()
            # ~ h, w, c = template.shape
            #~ print(template.shape[::-1])
            # ~ print(img.shape,'::',template.shape)
            res = cv.matchTemplate(img, template, method)
            # template matching with mask for TM_CCOEFF_NORMED not implemented yet.
            # must use either TM_SQDIFF or TM_CCORR_NORMED
            if (method in [cv.TM_SQDIFF, cv.TM_CCORR_NORMED]) and self.mask is not None:
                res = cv.matchTemplate(img, template, method, mask)
            else:
                res = cv.matchTemplate(img, template, method)
                
            # ~ res = cv.matchTemplate(img, template,cv.TM_CCORR_NORMED, mask = self.mask)
            # ~ res = cv.matchTemplate(img, template, method, mask = self.mask)
            #~ threshold = 0.6
            threshold = self.dblThreshold.value()
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
                
            
            if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
                test_val = min_val
                pass_ = (test_val <= threshold)
            else:
                test_val = max_val
                pass_ = (test_val >= threshold)
            
            if pass_:
                # ~ cv.rectangle(self.img, max_loc, (max_loc[0] + w, max_loc[1] + h), (0,255,0), 4)
                if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
                    x1 = min_loc[0]
                    y1 = min_loc[1]
                    cv.rectangle(img, min_loc, (min_loc[0] + w, min_loc[1] + h), (0,255,0), 4)
                    inside = True
                    
                    if self.groupBox2.isChecked():
                        trow = self.self.spinRow.value()
                        outer_item = scriptList[trow-1][1].graphicsItems[0]
                        found_rect = QGraphicsEllipseItem(min_loc[0], min_loc[1],
                                                          min_loc[0] + w, min_loc[1] + h)
                        pass_ = outer_item.collidesWithItem(found_rect, 
                                                           Qt.ContainsItemShape)
                else:
                    cv.rectangle(img, max_loc, (max_loc[0] + w, max_loc[1] + h), (0,255,0), 4)
            else:
                cv.line(img, (0,0), (img.shape[1], img.shape[0]), (0,0,255), 16)

            # ~ loc = np.where( res >= threshold)
            # ~ print(loc)
            # ~ for pt in zip(*loc[::-1]):
                # ~ cv.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0,255,0), 2)
            # ~ return max_val
            if pass_:    
                cv.putText(img,'PASS',(375,75), font, 3,(0,0,0),6,cv.LINE_AA)
                cv.putText(img,'PASS',(375,75), font, 3,(0,255,0),4,cv.LINE_AA)
                cv.rectangle(img, (0,0), (img.shape[1], img.shape[0]), (0,255,0), 16)
            else:
                cv.putText(img,'FAIL',(375,75), font, 3,(255,255,255),6,cv.LINE_AA)
                cv.putText(img,'FAIL',(375,75), font, 3,(0,0,255),4,cv.LINE_AA)
                cv.rectangle(img, (0,0), (img.shape[1], img.shape[0]), (0,0,255), 16)
            
            self.outputImg = img
            self.lblResult.setText('score: %f' % test_val)
    
    def radio_handler(self):
        bid = self.bgrpMatchMethod.checkedId()
        # NORMED values 1,3,5 all have max of 1
        # other values have unknown max --> set it really high
        if bid % 2: # 1, 3, 5
            self.dblThreshold.setMinimum(0.0)
            self.dblThreshold.setMaximum(1.0)
            self.dblThreshold.setSingleStep(0.1)
            self.dblThreshold.setValue(0.6)
        else:
            self.dblThreshold.setMinimum(0.0)
            self.dblThreshold.setMaximum(1e6)
            self.dblThreshold.setSingleStep(1)
            self.dblThreshold.setValue(100.0)
    
    def setMask(self):
        # we assume mask shape is elliptical and same size as self.target
        if self.target is not None:
            h, w = self.target[:2]
            if self.target.ndims == 3:
                self.mask = np.zeros((h, w, 3), np.uint8)
            else:
                self.mask = np.zeros((h, w), np.uint8)
                
            cv.ellipse( self.mask, center = (h/2, w/2), axes = (h, w), 
                        color = 255, thickness = -1 ) 
            # ~ cv.circle( self.mask, center = (int(span/2), int(span/2)), 
                       # ~ radius = int(span/2), color = 255, thickness = -1)
