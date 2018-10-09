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

statusbar_message = 'find target region in image'

def getInstance():
    instance = TemplateMatch()
    instance.setSizeMarginSpacing()
    
    return instance

class TemplateMatch(Plugin):
        
    def __init__(self, parent = None):
        
        super(TemplateMatch, self).__init__()
        
        
        self.setObjectName('template_match') # should be plugin name
           
        self.mask = None
        self.targetFname = ''
        
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
        tt = 'script row that contains specify_target for this match'
        self.spinTargetRow = QSpinBox(objectName = 'spinTargetRow')
        self.spinTargetRow.setToolTip(tt)
        hbox1.addWidget(self.spinTargetRow)
        hbox1.addWidget(QLabel('target row', toolTip = tt))

        hbox2 = QHBoxLayout()
        self.dblThreshold = QDoubleSpinBox(objectName = 'dblThreshold')

        self.groupInRegion = QGroupBox('inside region')
        self.groupInRegion.setObjectName('groupInRegion')
        self.groupInRegion.setCheckable(True)
        grid1 = QGridLayout()
        self.spinInside = QSpinBox(objectName = 'spinInside')
        self.spinInside.setMinimum(1)
        grid1.addWidget(QLabel('script row'), 0, 0)
        grid1.addWidget(self.spinInside,  0, 1)
        self.groupInRegion.setLayout(grid1)
        
        # set default method to cv.TM_CCOEFF_NORMED
        self.bgrpMatchMethod.button(cv.TM_CCOEFF_NORMED).setChecked(True)
        self.radio_handler()
        
        grid2 = QGridLayout()
        
        hbox2.addWidget(self.dblThreshold)
        hbox2.addWidget(QLabel('threshold'))
        grid2.addLayout(hbox2, 0, 0)
        grid2.addWidget(self.groupInRegion, 0, 1, 2, 1) 
        
        
        self.lblResult = QLabel('score: ')
        grid2.addWidget(self.lblResult, 1, 0)
        
        # ~ vbox1.addWidget(label1)
        vbox1.addWidget(groupBox1)
        vbox1.addLayout(hbox1)
        vbox1.addLayout(grid2)
        vbox1.setStretch(0, 3)
        vbox1.setStretch(1, 1)
        vbox1.setStretch(2, 2)
        # ~ vbox1.addWidget(self.lblResult)

        self.setLayout(vbox1)
        # ~ widget.img = None
        
    
    def mainFunc(self, playing, scriptList, row):
        
        self.spinInside.setMaximum(len(scriptList))
        self.graphicsItems = []
        
        trow = self.spinTargetRow.value()
        
        try:
            targetImg = scriptList[trow-1][1].targetImg
        except AttributeError:
            targetImg = None
        
        # ~ print('tfile ', tfile)
        
        if targetImg is not None:
            
            if self.inputImg is not None:
                
                # target file should be loaded, but are dims compatible?
                indim = self.inputImg.ndim
                tdim = targetImg.ndim
                # ~ print('indim ' , indim)
                if indim == 2 and tdim == 3:
                    # input is gray but target is color
                    targetImg = cv.cvtColor(targetImg, cv.COLOR_RGB2GRAY)
                elif indim == 3 and tdim == 2:
                    # target is gray but input is color
                    # this is strictly a no no. but we'll
                    # convert gray to color and keep going 
                    targetImg = cv.cvtColor(targetImg, cv.COLOR_GRAY2BGR)
                    targetImg = cv.cvtColor(targetImg, cv.COLOR_BGR2RGB)
                
                # ~ img = self.inputImg.copy()
                img = cv.copyMakeBorder(self.inputImg,
                                        0,0,0,0,
                                        cv.BORDER_REPLICATE)
            
                test_val = []
                numpass = 0
                
                
                template = targetImg
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
                    res = cv.matchTemplate(img, template, method, self.mask)
                else:
                    res = cv.matchTemplate(img, template, method)
                    
                # ~ print('w ', w, ' h ', h, 'res.shape ', res.shape, '  ', res)
                
                
                # ~ res = cv.matchTemplate(img, template,cv.TM_CCORR_NORMED, mask = self.mask)
                # ~ res = cv.matchTemplate(img, template, method, mask = self.mask)
                #~ threshold = 0.6
                threshold = self.dblThreshold.value()
                
                if self.groupInRegion.isChecked():
                    # ~ mask = np.zeros((self.inputImg.shape[0:2]), np.uint8)
                    # ~ mask = np.zeros((self.inputImg.shape), np.uint8)
                    
                    mask = np.zeros(res.shape, np.float)
                    
                    trow = self.spinInside.value()
                    if len(scriptList[trow-1][1].graphicsItems) > 0:
                        outer = scriptList[trow-1][1].graphicsItems[0]

                        if isinstance(outer, QGraphicsEllipseItem):
                            # ~ print('ellipso')
                            box = outer.rect()
                            # img	=	cv.ellipse(	img, box, color[, thickness[, lineType]]
                            # ~ mask = cv.ellipse(mask, box, 255, thickness = -1)
                            
                            #img	=	cv.ellipse(	img, center, axes, angle, startAngle, endAngle, color[, thickness[, lineType[, shift]]]	)
                            # ~ mask = cv.ellipse(mask, (int(box.center().x()), int(box.center().y())),
                                              # ~ (int(box.height()), int(box.width())),
                                              # ~ 0, 0, 360, 255, thickness = -1)
                            mask = cv.circle(mask, (int(box.center().x()), int(box.center().y())),
                                              int(box.height()/2), color = 1, thickness = -1)
                            
                        else:
                            pass
                            # ~ box = outer.rect()
                            # img	=	cv.ellipse(	img, box, color[, thickness[, lineType]]
                            #img	=	cv.rectangle(	img, pt1, pt2, color[, thickness[, lineType[, shift]]]	)
                            # ~ mask = cv.rectangle(mask, box.topLeft, box.topRight, color = 1, thickness = -1)
                    
                        mask = cv.boxFilter(mask,
                                            ddepth = -1,
                                            ksize = (w, h),
                                            anchor = (0,0),
                                            normalize = True,
                                            borderType = cv.BORDER_ISOLATED)
                        _, mask = cv.threshold(mask, thresh = 0.9999,
                                               maxval = 1.0, type = cv.THRESH_BINARY)
                        mask = mask.astype(np.uint8)
                    
                        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res, mask)
                    else:
                        self.outputImg = img
                        return
                else:
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
                        
                    else:
                        # ~ cv.rectangle(img, max_loc, (max_loc[0] + w, max_loc[1] + h), (0,255,0), 4)
                        x1 = max_loc[0]
                        y1 = max_loc[1]
                    cv.rectangle(img, (x1, y1), (x1+w, y1+h), (0,255,0), 4)
                    rect = QGraphicsRectItem(x1, y1, w, h)
                    pen = QPen(QColor(0, 255, 0), 5)
                    rect.setPen(pen)
                    self.graphicsItems.append(rect)
                    # ~ if self.groupInRegion.isChecked():
                        # ~ trow = self.spinRow.value()
                        # ~ if len(scriptList[trow-1][1].graphicsItems) > 0:

                            # ~ # target is always rectangular
                            # ~ outer = scriptList[trow-1][1].graphicsItems[0]
                            # ~ target = QGraphicsRectItem(x1, y1,
                                                              # ~ w, h)
                            
                            # ~ pass_ = target.collidesWithItem(outer, 
                                                               # ~ Qt.ContainsItemShape)
                            # ~ pass_ = outer.collidesWithItem(target, 
                                                               # ~ Qt.ContainsItemShape)
                            # ~ pass_ = self.target_inside_outer(target, outer)
                                                              
                            # ~ print(pass_)
                        # ~ else:
                            # ~ pass_ = False
                    
                else:
                    # ~ cv.line(img, (0,0), (img.shape[1], img.shape[0]), (0,0,255), 16)
                    pass

                # ~ loc = np.where( res >= threshold)
                # ~ print(loc)
                # ~ for pt in zip(*loc[::-1]):
                    # ~ cv.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0,255,0), 2)
                # ~ return max_val
                # ~ if pass_:
                    # ~ cv.putText(img,'PASS',(375,75), font, 3,(0,0,0),6,cv.LINE_AA)
                    # ~ cv.putText(img,'PASS',(375,75), font, 3,(0,255,0),4,cv.LINE_AA)
                    # ~ cv.rectangle(img, (0,0), (img.shape[1], img.shape[0]), (0,255,0), 16)
                # ~ else:
                    # ~ cv.putText(img,'FAIL',(375,75), font, 3,(255,255,255),6,cv.LINE_AA)
                    # ~ cv.putText(img,'FAIL',(375,75), font, 3,(0,0,255),4,cv.LINE_AA)
                    # ~ cv.rectangle(img, (0,0), (img.shape[1], img.shape[0]), (0,0,255), 16)
                
                self.pass_ = pass_
                
                self.outputImg = img
                self.lblResult.setText('score: %f' % test_val)
    
    def target_inside_outer(self, target, outer):
        if isinstance(outer, QGraphicsEllipseItem):
            # circle or ellipse. equations are the same if we use 
            # general equation of ellipse:
            #  x^2/a + y^2/b = 1
            # ~ print('friggin ellipse')
            x0 = outer.rect().center().x()
            y0 = outer.rect().center().y()
            
            a = outer.rect().width()/2
            b = outer.rect().height()/2
            
            print('x0: %d; y0: %d; a: %d; b:%d' % (x0,y0,a,b))
            
            # need to test all four corners of target
            x = target.rect().topLeft().x()
            y = target.rect().topLeft().y()
            
            print('x: %d; y: %d;' % (x,y))
            topLeft = (x-x0)*(x-x0)/(a*a) + (y-y0)*(y-y0)/(b*b) <= 1
            
            x = target.rect().topRight().x()
            y = target.rect().topRight().y()
            print('x: %d; y: %d;' % (x,y))
            topRight = (x-x0)*(x-x0)/(a*a) + (y-y0)*(y-y0)/(b*b) <= 1
            
            x = target.rect().bottomLeft().x()
            y = target.rect().bottomLeft().y()
            print('x: %d; y: %d;' % (x,y))
            bottomLeft = (x-x0)*(x-x0)/(a*a) + (y-y0)*(y-y0)/(b*b) <= 1
    
            x = target.rect().bottomRight().x()
            y = target.rect().bottomRight().y()
            print('x: %d; y: %d;' % (x,y))
            bottomRight = (x-x0)*(x-x0)/(a*a) + (y-y0)*(y-y0)/(b*b) <= 1
        elif isinstance(outer, QGraphicsRectItem):
            topLeft = (outer.topLeft().x() >= target.topLeft.x() and 
                       outer.topLeft().y() >= target.topLeft.y() )
            topRight = (outer.topRight().x() >= target.topRight.x() and 
                       outer.topRight().y() >= target.topRight.y() )
            bottomLeft = (outer.bottomLeft().x() >= target.bottomLeft.x() and 
                       outer.bottomLeft().y() >= target.bottomLeft.y() )
            bottomRight = (outer.bottomRight().x() >= target.bottomRight.x() and 
                       outer.bottomRight().y() >= target.bottomRight.y() )
        else:
            raise AttributeError('outer object neither ellipse nor rectangle, dude')
    
        pass_ = topLeft and topRight and bottomLeft and bottomRight
        return pass_
    
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
            
            
