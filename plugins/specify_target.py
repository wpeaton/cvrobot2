from plugin import Plugin
from widget_helpers import radio_filler, spinbox_slider
from uuid import uuid4

from PyQt5.QtWidgets import (QMainWindow, QGraphicsView,
                             QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGroupBox, QLayout,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QStackedLayout, QGraphicsScene,
                             QFileDialog, QButtonGroup,
                             QSizePolicy, QGraphicsPixmapItem, 
                             QGraphicsRectItem, QGraphicsEllipseItem,
                             QGraphicsScene,
                             )
from PyQt5.QtCore import  (QDir, pyqtSignal, QObject, QRectF, QLineF, 
                           QPointF, Qt)
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPen, QColor, QWindow, QPixmap, QImage

import cv2 as cv
import numpy as np
import time

statusbar_message = 'draw target region and save to file'

def getInstance():
    instance = SpecifyTarget()
    instance.setSizeMarginSpacing()
    
    return instance

class SpecifyTarget(Plugin):
        
    def __init__(self, parent = None):
        
        super(SpecifyTarget, self).__init__()
        
        self.setObjectName('specify_target') # should be plugin name
    
        # ~ self.needsGraphicsView = True
        self.needsEventFilter = True
        self.fname = ''
        self.image = None
        self.targetImg = None
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        hbox1 = QHBoxLayout()
        self.dblNumTargets = QDoubleSpinBox(objectName = 'dblNumTargets')
        self.dblNumTargets.setMinimum(1)
        self.dblNumTargets.setMaximum(5)
        self.dblNumTargets.setValue(1)
        self.dblNumTargets.setSingleStep(1)
        self.chkSaveTarget = QCheckBox('save target.png', objectName = 'chkSaveTarget')
        hbox1.addWidget(self.dblNumTargets)
        hbox1.addWidget(QLabel('num targets'))
        hbox1.addWidget(self.chkSaveTarget)
        
        
        labels = ['Rectangle', 'Square', 'Ellipse', 'Circle']
        groupBox1, self.bgrpShape = radio_filler('target shape', labels, 2)

        labels = ['opposite\ncorners', 'center\n-edge']
        groupBox2, self.bgrpDrawMethod = radio_filler('draw method', labels, 2)
        
        self.lblStatus = QLabel(wordWrap = True)
        groupBox2.layout().addWidget(self.lblStatus, 0, 2)
                   
        self.bgrpShape.button(0).setChecked(True)
        self.bgrpDrawMethod.button(0).setChecked(True)
        
        self.bgrpShape.buttonClicked.connect(self.radio_handler)
        
        self.targetView = QGraphicsView()
        scene = QGraphicsScene()
        self.targetView.setScene(scene)
        # ~ vbox1.addLayout(hbox1)
        # ~ vbox1.addWidget(groupBox1)
        vbox1.addWidget(self.targetView)
        vbox1.addWidget(groupBox2)
        vbox1.setStretch(0,3)
        vbox1.setStretch(1,1)

        self.setLayout(vbox1)
        
        self.chkSaveTarget.setChecked(True)
        
        # class variables
        self.targetShape = None
        self.target = None
        self.begin = None
        self.end = None
        self.training = False
    
    def getParams(self):
        params = super(SpecifyTarget, self).getParams()
        params['fname'] = self.fname
        self.Params = params
        return params
        
    def setParams(self, params):
        params = super(SpecifyTarget, self).setParams(params)
        
        self.fname = self.Params['fname']
        
    def showImg(self, img):
        if len(img.shape) == 3:
            # ~ #img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            height, width, bpc = img.shape
            bpl = bpc * width
            # ~ print(subimage.data, ', ', width, ', ', height, ', ', bpl)
            qimg = QImage(img, width, height, bpl, QImage.Format_RGB888)
        else:
            height, width = img.shape
            bpc = 1
            bpl = bpc*width
            qimg = QImage(img.data, width, height, bpl, QImage.Format_Grayscale8)
        
        self.image = QGraphicsPixmapItem(QPixmap.fromImage(qimg))
        self.targetImg = img
        self.targetView.scene().clear()
        self.targetView.scene().addItem(self.image)
        
        self.targetView.fitInView(self.image.boundingRect(), Qt.KeepAspectRatio)
    
    def eventFilter(self, source, event):

        if event.type() == QtCore.QEvent.MouseButtonPress:
            print(time.time(), ' mousebuttonpress')
            if isinstance(source, QGraphicsView):
            
                self.mouseButtonPress(source)

                return True
        elif isinstance(source, QGraphicsView) or source.objectName() == 'MainWindowWindow':
            if self.training:
                if (event.type() == QtCore.QEvent.MouseMove and
                        source.objectName() == 'MainWindowWindow'):
                    if event.buttons() != QtCore.Qt.NoButton:
                        # ~ global end
                        self.mouseMove()
                        
                    return True
                elif (event.type() == QtCore.QEvent.MouseButtonRelease and
                        source.objectName() == 'MainWindowWindow'):

                    self.mouseButtonRelease()
                    
                    return True # this is for eventFilter. when True, stop processing events
  
        return False # this is for eventFilter. when False, keep processing events
    
    def mouseButtonPress(self, source):
        pos = QtGui.QCursor.pos()
            
        viewPoint  = source.mapFromGlobal(pos)
        scenePoint = source.mapToScene(viewPoint)
        # ~ global graphicsView
        self.graphicsView = source
        self.begin = scenePoint
        self.training = True
        
        # ~ print(pos)
        # ~ print(self.begin)
        
        rect = QRectF(self.begin, self.begin)
        # ~ print(rect)
        # ~ self.targetShape = QGraphicsRectItem(rect)
        # ~ global targetShapes
        if self.targetShape is not None:
            try:
                print('targetShape ', self.targetShape)
                source.scene().removeItem(self.targetShape)
            except RuntimeError:
                pass
            
        # ~ bshape = self.bgrpShape.checkedId()
        bshape = 0
        # ~ print('bshape ', bshape)
        if  bshape == 0:  # Rectangle
            self.targetShape = QGraphicsRectItem(rect)
        elif bshape == 1: # Square
            self.targetShape = QGraphicsRectItem(rect)
        elif bshape == 2: # Ellipse
            self.targetShape = QGraphicsEllipseItem(rect)
        elif bshape == 3: # Circle
            self.targetShape = QGraphicsEllipseItem(rect)
        
        self.targetShape.setZValue(1)

        pen = QPen(QColor(0, 255, 0), 5) 
        self.targetShape.setPen(pen)
        try:
            source.scene().addItem(self.targetShape)

        except RuntimeError:
            pass
        print('mousie pressie')
    
    def mouseMove(self):
        pos = QtGui.QCursor.pos()
                        
        viewPoint  = self.graphicsView.mapFromGlobal(pos)
        scenePoint = self.graphicsView.mapToScene(viewPoint)
    
        self.end = scenePoint
        # ~ print('end :', self.end)
        try:
            # ~ bshape = self.bgrpShape.checkedId()
            bshape = 0
            bmethod = self.bgrpDrawMethod.checkedId()
            if bshape == 3 :  # circle
                if bmethod == 1:
                    # center radius circle
                    r = QLineF(self.begin, self.end).length()
                    cx = self.begin.x()
                    cy = self.begin.y()
                    # ~ x1 = self.begin.x() - r
                    # ~ y1 = self.begin.y() - r
                    # ~ x2 = self.begin.x() + r
                    # ~ y2 = self.begin.y() + r
                elif bmethod == 0:
                    r = QLineF(self.begin, self.end).length()/2
                    # ~ center = line.center()  # not available until qt > 5.8
                    cx = float(self.begin.x() + self.end.x())/2.0
                    cy = float(self.begin.y() + self.end.y())/2.0
                x1 = cx - r
                y1 = cy - r
                x2 = cx + r
                y2 = cy + r
                # ~ print('begin ', self.begin, ' end ', self.end)     
                # ~ print('r ', r, ' cx  ', cx, ' cy ', cy)
            elif bshape == 1:   # square
                if bmethod == 1:
                    # center radius circle
                    r = QLineF(self.begin, self.end).length()/np.sqrt(2)
                    cx = self.begin.x()
                    cy = self.begin.y()
                    x1 = cx - r
                    y1 = cy - r
                    x2 = cx + r
                    y2 = cy + r
                elif bmethod == 0:
                    line = QLineF(self.begin, self.end)
                    r = line.length()/np.sqrt(2)
                    sx = np.sign(line.dx())
                    sy = np.sign(line.dy())
                    x1 = self.begin.x()
                    y1 = self.begin.y()
                    x2 = self.begin.x() + sx*r
                    y2 = self.begin.y() + sy*r
            
            #rectangles and ellipses
            else:
                if bmethod == 0:
                    # 2 corners rectangle
                    x1 = self.begin.x()
                    y1 = self.begin.y()
                    x2 = self.end.x()
                    y2 = self.end.y()
                elif bmethod == 1:
                    # center/corner rectangle
                    x1 = self.begin.x() - abs(self.begin.x() - self.end.x())
                    y1 = self.begin.y() - abs(self.begin.y() - self.end.y())
                    x2 = self.begin.x() + abs(self.begin.x() - self.end.x())
                    y2 = self.begin.y() + abs(self.begin.y() - self.end.y())
            
            # ~ self.targetShape.setRect(QRectF(begin, end))
            # ~ idx = len(self.targetShapes)-1
            self.targetShape.setRect(QRectF(QPointF(x1, y1), 
                                           QPointF(x2, y2)))
            self.lblStatus.setText('drawing target')
            
            # ~ print('x1, y1, x2, y2: ', x1, y1, x2, y2)
            
        except RuntimeError as e:
            # ~ pass
            print('RuntimeError in mouseMove. ', e)
    
    def mouseButtonRelease(self):
        self.training = False
                    
        # time to save target image. but first we need to 
        # check the sizes
        
        self.graphicsItems.append(self.targetShape)
        
        # only save to target.png if checkbox is checked
        # ~ if self.chkSaveTarget.isChecked():
        try:
            rect = self.targetShape.rect()
            print('target rect ', rect)
                
            x1 = int(round(min([rect.left(), rect.right()])))
            y1 = int(round(min([rect.top(), rect.bottom()])))
            x2 = int(round(max([rect.left(), rect.right()])))
            y2 = int(round(max([rect.top(), rect.bottom()])))
            
            # ~ print( 'x1, x2, y1, y2: %d, %d, %d, %d' % (x1, x2, y1, y2))
            # ~ print('width: ', rect.width(), '. height: ', rect.height())

            
            # for circle and ellipse, we want width and height to be divisible
            # by two. so we'll add an extra pixel if necessary
            x2 += (x2 - x1) % 2  # remainder will be 1 for odd widths
            y2 += (y2 - y1) % 2
            
            # ~ print( 'x2, y2: %d, %d' % (x2, y2))
            
            if abs(y2-y1) > 20:
                
                # ~ dx = x2-x1
                # ~ dy = y2-y1
                
                # use +1 because slice notation is screwy
                subimage = self.inputImg[y1:y2, x1:x2].copy()
                self.showImg(subimage)
                
                if subimage.ndim == 3:
                    subimage = cv.cvtColor(subimage, cv.COLOR_RGB2BGR)

                fname = 'target_' + str(uuid4()) + '.png'
                # ~ print(fname)
                self.fname = fname
                cv.imwrite(fname, subimage)
                self.lblStatus.setText('target set')
            else:
                self.lblStatus.setText('')
            self.graphicsView.scene().removeItem(self.targetShape)
        except RuntimeError as e:
            print('RuntimeError in mouseButtonRelease. ', e)
    
    def mainFunc(self, playing, scriptList, row):
        # ~ print(self.inputImg)
        if self.inputImg is not None:
            self.outputImg = self.inputImg  # here we don't even need to
                                            # make a copy. it's a straight
                                            # pass through.
            # ~ self.outputImg = self.inputImg.copy()
            # ~ print('copy')
        if self.image is None:
            if self.fname:
                img = cv.imread(self.fname)
                if img is None:
                    self.lblStatus.setText('target file not found')
                else:
                    if img.ndim == 3:
                        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                    self.showImg(img)
        
    def resizeEvent(self, event = 0):
        try:
            rect = self.targetView.scene().items()[0].boundingRect()
            self.targetView.fitInView(rect, Qt.KeepAspectRatio)
        except IndexError:
            pass
    
    def radio_handler(self):
        self.bgrpDrawMethod.button(1).setChecked(True)
        # ~ if self.bgrpShape.checkedId() in [1,3]: # square or circle
            # ~ # set draw method to center-edge by default
            # ~ self.bgrpDrawMethod.button(1).setChecked(True)
            # print('corner-edge')
        # ~ else:
            # ~ self.bgrpDrawMethod.button(0).setChecked(True)
            # print('fuck you')
