from plugin import Plugin
from widget_helpers import radio_filler, spinbox_slider

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QButtonGroup, QGraphicsEllipseItem )
from PyQt5.QtGui import QPen, QColor
# ~ from PyQt5.QtCore import QDir, QObject

import cv2 as cv
import numpy as np
import time


statusbar_message = 'Find circular or partial circular features in a Grayscale image'

pen = QPen(QColor(0, 255, 0), 5)

def getInstance():
    instance = Circles()
    instance.setSizeMarginSpacing()
    
    return instance

class Circles(Plugin):
        
    def __init__(self, parent = None):
        
        super(Circles, self).__init__()
        
        self.setObjectName('circles') # should be plugin name
    
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        hbox1 = QHBoxLayout()
        lblDp = QLabel('dp')
        self.dblDp = QDoubleSpinBox()
        self.dblDp.setObjectName('dblDp')
        self.dblDp.setValue(1.0)
        self.dblDp.setSingleStep(0.1)
        tt = '''Inverse ratio of the accumulator resolution to the image resolution. 
                For example, if dp=1 , the accumulator has the same resolution as the 
                input image. If dp=2 , the accumulator has half as big width and height.'''
        lblDp.setToolTip(tt)
        self.dblDp.setToolTip(tt)
        lblMinDist = QLabel('minDist')
        self.dblMinDist = QDoubleSpinBox()
        self.dblMinDist.setObjectName('dblMinDist')
        tt = '''Minimum distance between the centers of the detected circles. 
                If the parameter is too small, multiple neighbor circles may be falsely 
                detected in addition to a true one. If it is too large, some circles 
                may be missed.'''
        lblMinDist.setToolTip(tt)
        self.dblMinDist.setToolTip(tt)
        self.dblMinDist.setSingleStep(5)
        self.dblMinDist.setMaximum(2000)
        self.dblMinDist.setValue(150)
        hbox1.addWidget(lblDp)
        hbox1.addWidget(self.dblDp)
        hbox1.addWidget(lblMinDist)
        hbox1.addWidget(self.dblMinDist)
        
        hbox2 = QHBoxLayout()
        lblParam1 = QLabel('param1')
        self.dblParam1 = QDoubleSpinBox()
        self.dblParam1.setObjectName('dblParam1')
        self.dblParam1.setSingleStep(1)
        self.dblParam1.setValue(50)
        tt = '''First method-specific parameter. In case of HOUGH_GRADIENT , it is the higher 
                threshold of the two passed to the Canny edge detector (the lower one is twice smaller).'''
        lblParam1.setToolTip(tt)
        self.dblParam1.setToolTip(tt)
        lblParam2 = QLabel('param2')
        self.dblParam2 = QDoubleSpinBox()
        self.dblParam2.setObjectName('dblParam2')
        self.dblParam2.setSingleStep(1)
        self.dblParam2.setValue(45)
        tt = '''Second method-specific parameter. In case of HOUGH_GRADIENT , it is the accumulator
                threshold for the circle centers at the detection stage. The smaller it is,
                the more false circles may be detected. Circles, corresponding to the larger
                accumulator values, will be returned first.'''
        lblParam2.setToolTip(tt)
        self.dblParam2.setToolTip(tt)
        hbox2.addWidget(lblParam1)
        hbox2.addWidget(self.dblParam1)
        hbox2.addWidget(lblParam2)
        hbox2.addWidget(self.dblParam2)
        
        hbox3 = QHBoxLayout()
        lblMinRadius = QLabel('minRadius')
        self.dblMinRadius = QDoubleSpinBox()
        self.dblMinRadius.setObjectName('dblMinRadius')
        self.dblMinRadius.setSingleStep(1)
        self.dblMinRadius.setMaximum(2000)
        self.dblMinRadius.setValue(150)
        tt = '''Inverse ratio of the accumulator resolution to the image resolution. 
                For example, if dp=1 , the accumulator has the same resolution as the 
                input image. If dp=2 , the accumulator has half as big width and height.'''
        lblMinRadius.setToolTip(tt)
        self.dblMinRadius.setToolTip(tt)
        lblMaxRadius = QLabel('maxRadius')
        self.dblMaxRadius = QDoubleSpinBox()
        self.dblMaxRadius.setObjectName('dblMaxRadius')
        self.dblMaxRadius.setSingleStep(1)
        self.dblMaxRadius.setMaximum(2000)
        self.dblMaxRadius.setValue(200)
        
        tt = '''Minimum distance between the centers of the detected circles. 
                If the parameter is too small, multiple neighbor circles may be falsely 
                detected in addition to a true one. If it is too large, some circles 
                may be missed.'''
        lblMaxRadius.setToolTip(tt)
        self.dblMaxRadius.setToolTip(tt)
        hbox3.addWidget(lblMinRadius)
        hbox3.addWidget(self.dblMinRadius)
        hbox3.addWidget(lblMaxRadius)
        hbox3.addWidget(self.dblMaxRadius)
        
        hbox4 = QHBoxLayout()
        self.chkCrop = QCheckBox('Crop ', 
                                 objectName = 'chkCrop')
        labels = ['black', 'white']
        groupBox1, self.bgrpBackground = radio_filler('Background Color', labels, 2)
        self.bgrpBackground.button(0).setChecked(True)
        hbox4.addWidget(self.chkCrop)
        hbox4.addWidget(groupBox1)
        hbox4.setStretch(0,1)
        hbox4.setStretch(1,3)
        
        
        vbox1.addLayout(hbox1)
        vbox1.addLayout(hbox2)
        vbox1.addLayout(hbox3)
        vbox1.addLayout(hbox4)
        vbox1.setSpacing(2)

        self.setLayout(vbox1)
        # ~ self.img = None
    
    def mainFunc(self, playing, scriptList, scriptPos):
        
        if self.inputImg is not None:
            # convert to grayscale if image is color
            if self.inputImg.ndim == 3:
                img = cv.cvtColor(self.inputImg, cv.COLOR_RGB2GRAY)
            else:
                img = self.inputImg
            # need to make a copy because this plugin superimposes a circle
            # on it's output image
            self.outputImg = self.inputImg.copy()

            
            circles = cv.HoughCircles(img,
                                  method = cv.HOUGH_GRADIENT,
                                  dp       = self.dblDp.value(),
                                  minDist  = self.dblMinDist.value(),
                                  param1   = self.dblParam1.value(),
                                  param2   = self.dblParam2.value(),
                                  minRadius = int(self.dblMinRadius.value()),
                                  maxRadius = int(self.dblMaxRadius.value()))
            
            self.graphicsItems = []
            if circles is not None:
                # ~ circles = np.uint16(np.around(circles))
                # ~ print(circles)
                for i, c in enumerate(circles[0,:]):
                    # draw the outer circle
                    x0 = c[0]
                    y0 = c[1]
                    r  = c[2]
                    # ~ print('x0 y0 r ', x0, y0, r)
                    cv.circle(self.outputImg,(x0,y0),r,(0,255,0),2)
                    exes = [x0-r, x0+r]
                    wyes = [y0-r, y0+r]
                    x1 = int(min(exes))
                    x2 = int(max(exes))
                    y1 = int(min(wyes))
                    y2 = int(max(wyes))
                    w = x2-x1
                    h = y2-y1
                    qcircle = QGraphicsEllipseItem(x1, y1, w, h)
                    off_x = 0.0
                    off_y = 0.0
                    if x1 < 0:
                        off_x = x1
                        x1 = 0
                    if y1 < 0:
                        off_y = y1
                        y1 = 0
                    imh, imw = img.shape[0:2]
                    if x2 > imw:
                        off_x = x2 - imw
                        x2 = imw
                    if y2 > imh:
                        off_y = y2 - imh
                        y2 = imh
                    w = int(w - abs(off_x))
                    h = int(h - abs(off_y))
                    # ~ print('qcircle.rect() ', qcircle.rect())
                    qcircle.setPen(pen)
                    self.graphicsItems.append(qcircle)
                    # draw the center of the circle
                    cv.circle(self.outputImg,(x0,y0),2,(0,0,255),3)
                    
                    if i == 0 and self.chkCrop.isChecked():
                        bg = self.bgrpBackground.checkedId()  # black is zero, white is 1
                        
                        
                        x0 = int(w/2 + off_x)
                        y0 = int(h/2 + off_y)
        
                        if self.inputImg.ndim == 2:
                            subimage = self.inputImg[y1:y2, x1:x2].copy()
                            cv.circle(self.outputImg,(x0,y0),r,(0,255,0),2)
                            if bg:
                                mask = 255*np.ones((h, w), dtype = np.uint8)
                            else:
                                mask = np.zeros((h, w), dtype = np.uint8)
                            mask = cv.circle(mask,(x0,y0),r, color = 1, thickness = -1)
                        else:
                            subimage = self.inputImg[y1:y2, x1:x2, :].copy()
                            if bg:
                                mask = 255*np.ones((h, w, 3), dtype = np.uint8)
                            else:
                                mask = np.zeros((h, w, 3), dtype = np.uint8)
                            mask = cv.circle(mask,(x0,y0),r, color = (1,1,1), thickness = -1)
                        
                        #~ print('subimage ', subimage.shape)
                        #~ print('mask ', mask.shape)
                        if subimage.shape == mask.shape:
                            self.outputImg = cv.multiply(subimage, mask)
                        else:
                            self.outputImg = mask
                            print('subimage ', subimage.shape, '.  mask ', mask.shape)
                            print('off_x ', off_x, '.  off_y ', off_y)
                
                    
            else:
                print(time.time(), ':  no effing circles. what kind of jive is this man?')


