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
from PyQt5.QtCore import QDir, pyqtSignal, pyqtSlot, QObject, QThread, QTimer
import cv2 as cv
import numpy as np
import time

cap = cv.VideoCapture(0)

statusbar_message = 'Load image from camera or hard disk'

def getInstance():
    ''' provides easy way for plugin finder to get an instance of this
        particular plugin
    '''
    instance = ImageLoader()
    instance.setSizeMarginSpacing()
    
    return instance
    
class Grabber(QObject):
    def __init__(self):
        super().__init__()
        self.cap = cv.VideoCapture(0)
        self.running = False
    
    @pyqtSlot(bool)
    def setRunning(self, running):
        self.running = running
    
    # ~ @pyqtSlot()
    def grab(self, img, grayScale):
        while self.running:
            ret, img = self.cap.read() 
            if ret:
                print('img.shape ', img.shape)
                if grayScale:
                    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                else:
                    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            #~ print(time.time(), ' grab grab')
                
            # might need a delay. how about some kind of qobject timer funciton?


class ImageLoader(Plugin):
    def __init__(self, parent = None):
        
        super(ImageLoader, self).__init__()

        self.Params = {}
        
        self.setObjectName('image_loader') # should be plugin name
        
        self.isSource  = True
        self.running   = False
        self.grayScale = False
        self.outputBuffer = None
        
        self.grabber = Grabber()
        self.thread  = QThread()
        self.grabber.moveToThread(self.thread)
        self.thread.started.connect(lambda: self.grabber.grab( 
                                    img = self.outputBuffer, 
                                    grayScale = self.grayScale))
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        self.chkGrayScale = QCheckBox('Gray Scale')
        self.chkGrayScale.setObjectName('chkGrayScale')
        
        group_box, self.bgrpSource = radio_filler('Image Source', 
                                                 ['File', 'Camera'], 2)
        # ~ print('init image_loader. bgrpSource parent ', self.bgrpSource.parent())
        self.bgrpSource.setParent(self)
        self.buttonGroupList.append(self.bgrpSource)
        # ~ print('self.bgrpSource.objectName()  ', self.bgrpSource.objectName())
        self.bgrpSource.buttonClicked.connect(self.radiohandler)
        # ~ bgrpSource.buttonClicked.connect(shambo)
        
        hbox2 = QHBoxLayout()
        lblFile = QLabel('File:')
        self.txtFile = QLineEdit()
        self.txtFile.setObjectName('txtFile')
        btnBrowseFile = QPushButton('Browse...')
        btnBrowseFile.clicked.connect(self.on_btnBrowseFile_clicked)
        hbox2.addWidget(lblFile)
        hbox2.addWidget(self.txtFile)
        hbox2.addWidget(btnBrowseFile)
        
        vbox1.addWidget(self.chkGrayScale)
        vbox1.addWidget(group_box)
        vbox1.addLayout(hbox2)

        self.setLayout(vbox1)
        # ~ widget.img = None
        for item in self.findChildren(QWidget):
            item.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        self.bgrpSource.button(1).setChecked(True)
        
        # ~ self.cap = cv.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.grab)
        
        #~ cap.set(cv.CAP_PROP_FRAME_WIDTH,  1280)
        #~ cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        
        # ~ QTimer.singleShot(500, self.grab)
    
    def grab(self):
        # ~ print(time.time(), ' grab grab')
        ret, img = cap.read() 
        if ret:
            if self.grayScale:
                img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            else:
                img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            # ~ print(time.time(), ' grab grab')
            #~ print('grab shape ', img.shape)
            # ~ img = cv.resize(img, (0,0), fx = 0.5, fy = 0.5,
                            # ~ interpolation = cv.INTER_AREA)
            self.outputImg = img
                
            # might need a delay. how about some kind of qobject timer funciton?
        else:
            self.outputImg = None
    def radiohandler(self,):
        # ~ print('radiohandler')
        # ~ print(widget.findChild(QLineEdit, 'txtFile').text())
        # ~ self.mainFunc()
        pass

    def on_btnBrowseFile_clicked(self):

        fileFilter = 'Image files (*.jpg *.png)'
        fname, _filter = QFileDialog.getOpenFileName(None, 'Select Image File', 
                        QDir.currentPath(), fileFilter)
        print(fname)
        if fname:
            self.bgrpSource.button(0).setChecked(True)
            self.txtFile.setText(fname)  # on cancel fname is empty string so no need to wrap it in if statement
        
    # ~ def mainFunc(file_ = None, widget = None):
    def mainFunc(self, playing, scriptList, scriptPos):
        
        # ~ grayScale = widget.findChild(QCheckBox, 'chkGrayScale').isChecked()
        # ~ useFile = widget.findChild(QRadioButton, 'optFile').isChecked()
        # ~ useCamera = widget.findChild(QRadioButton, 'optCamera').isChecked()
        self.grayScale = self.chkGrayScale.isChecked()
        useFile = self.bgrpSource.button(0).isChecked()
        useCamera = self.bgrpSource.button(1).isChecked()
        # ~ print('useFile, useCamera:  ', useFile, ', ', useCamera)
        
        
        if useFile:
            if self.inputImg is None:
                file_ = self.txtFile.text()
                if file_ != '':
                    if self.grayScale:
                        self.outputImg = cv.imread(file_, 0)
                    else:
                        img = cv.imread(file_)
                        self.outputImg = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            else:
                pass
        elif useCamera:
            # ~ pass
            # ~ if playing == False:
                # ~ # read 40 times to equalize lighting
                # ~ for i in range(40):
                    # ~ cap.read()
                
            # ~ ret, self.outputImg = cap.read() 
            # ~ if grayScale:
                # ~ self.outputImg = cv.cvtColor(self.outputImg, cv.COLOR_BGR2GRAY)
            # ~ else:
                # ~ self.outputImg = cv.cvtColor(self.outputImg, cv.COLOR_BGR2RGB)
            
            #comment out if not using timer
            if self.running != playing:
                self.running = playing
                self.grabber.setRunning(self.running)
                
                if self.running:
                    self.timer.start(33)
                else:
                    self.timer.stop()
            
            # ~ if self.outputBuffer is not None:
                # ~ self.outputImg = self.outputBuffer.copy()
                    

