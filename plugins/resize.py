# any variables declared in this module need to be the same for all
# "instances". any time we want more than one version of variables,
# we need to put them in a function which hopefully generates unique
# copies when the function runs.

from plugin import Plugin
from widget_helpers import radio_filler

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QFileDialog, QButtonGroup,
                             QSizePolicy,
                             )
from PyQt5.QtCore import (QDir, pyqtSignal, pyqtSlot, QObject, QThread, 
                          QSize, QTimer)
from PyQt5 import QtGui
import cv2 as cv
import numpy as np
import time

cap = cv.VideoCapture(0)

statusbar_message = 'Resize image (bigger or smaller)'

def getInstance():
    ''' provides easy way for plugin finder to get an instance of this
        particular plugin
    '''
    instance = Resize()
    instance.setSizeMarginSpacing()
    
    return instance
    


class Resize(Plugin):
    def __init__(self, parent = None):
        
        super(Resize, self).__init__()

        self.Params = {}
        
        self.setObjectName('resize') # should be plugin name
        
        self.isSource  = False
        self.outputBuffer = None
        

        
        # declare all parameter widgets below
        grid1 = QGridLayout()
        grid1.addWidget(QLabel('Input:'),  0, 0)
        self.lblInputSize = QLabel('WWWxYYY')
        grid1.addWidget(self.lblInputSize, 0, 1)
        grid1.addWidget(QLabel('New size:'), 1, 0)
        self.lblNewSize = QLabel('WWWxYYY')
        grid1.addWidget(self.lblNewSize,     1, 1)
        grid1.addWidget(QLabel('fx: '),      2, 0)
        self.dblFx = QDoubleSpinBox(value = 1,
                                    minimum = 0.1, maximum = 4.0,
                                    singleStep = 0.1, objectName = 'dblFx')
        self.dblFx.valueChanged.connect(lambda: self.spinSync('dblFx'))
        grid1.addWidget(self.dblFx,          2, 1)
        grid1.addWidget(QLabel('fy: '),      3, 0)
        self.dblFy = QDoubleSpinBox(value = 1,
                                    minimum = 0.1, maximum = 4.0,
                                    singleStep = 0.1, objectName = 'dblFy')
        self.dblFy.valueChanged.connect(lambda: self.spinSync('dblFy'))
        grid1.addWidget(self.dblFy,          3, 1)
        
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('unlink.png'), 
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap('link.png'), 
                       QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.btnLink = QPushButton(checkable = True, icon = icon,
                                   toolTip = 'lock x and y together')
        grid1.addWidget(self.btnLink,        2, 2, 2, 1)

        self.setLayout(grid1)
        
        self.btnLink.setChecked(True)
    
    def resizeEvent(self, event = 0):
        
        # ~ print('resize resize')
        aspect_ratio = 3.75 # 620/166
        factor = 0.5
        
        print('width ', self.btnLink.width(),
              '  height ', self.btnLink.height())
        
        new_width  = int(factor*self.btnLink.height()/aspect_ratio)
        new_height = int(factor*self.btnLink.height())
        
        self.btnLink.setIconSize(QSize(new_width, new_height) )
    
    
    def radiohandler(self):
        # ~ print('radiohandler')
        # ~ print(widget.findChild(QLineEdit, 'txtFile').text())
        # ~ self.mainFunc()
        pass

    def spinSync(self, changedWidget):
        if self.btnLink.isChecked():
            if changedWidget == 'dblFx':
                self.dblFy.setValue(self.dblFx.value())
            if changedWidget == 'dblFy':
                self.dblFx.setValue(self.dblFy.value())
            
    # ~ def mainFunc(file_ = None, widget = None):
    def mainFunc(self, playing, scriptList, scriptPos):
        
        if self.inputImg is not None:
            h, w = self.inputImg.shape[0:2]
            self.lblInputSize.setText('%d×%d' % (w, h))
            
            
            if self.dblFx.value() <= 1:
                interpolation = cv.INTER_AREA
            else:
                interpolation = cv.INTER_LINEAR
            self.outputImg = cv.resize(self.inputImg, dsize = (0,0),
                                       fx = self.dblFx.value(),
                                       fy = self.dblFy.value(), 
                                       interpolation = interpolation)
            h, w = self.outputImg.shape[0:2]
            self.lblNewSize.setText( '%d×%d' % (w, h))

