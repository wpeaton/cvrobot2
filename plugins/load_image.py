# any variables declared in this module need to be the same for all
# "instances". any time we want more than one version of variables,
# we need to put them in a function which hopefully generates unique
# copies when the function runs.

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QFileDialog, QButtonGroup,
                             QSizePolicy,
                             )
from PyQt5.QtCore import QDir, pyqtSignal, QObject

import cv2 as cv
import numpy as np

cap = cv.VideoCapture(0)

needBrowser = False
fileFilter = 'Image files (*.jpg *.png)'
# If you want to use multiple filters, separate each one with two semicolons. For example:
# 'Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)'

statusbar_message = 'Load image from camera or hard disk'

class SignalClass(QObject):
    imageSignal = pyqtSignal('PyQt_PyObject') # this one might be necessary 
    # not clear whether the args to pyqtSignal correspond to args emitted
    # with signal.
    
mysignal = SignalClass()

def getWidget():
        
    widget = QWidget()
    widget.setObjectName('load_image')  # should be plugin name
    
    widget.isSource = True
    widget.inputImg = None
    widget.outputImg = None
    widget.needsGraphicsView = False
    
    # declare all parameter widgets below
    vbox1 = QVBoxLayout()
    widget.chkGrayScale = QCheckBox('Gray Scale')
    # ~ chkGrayScale.setObjectName('chkGrayScale')
    
    hbox1 = QHBoxLayout()
    lblSource = QLabel('Image Source')
    bgrpSource = QButtonGroup(widget) # need to provide parent (widget) or the button group is orphaned and won't work properly
    widget.optFile = QRadioButton('File', widget)
    widget.optFile.setObjectName('optFile')
    widget.optCamera = QRadioButton('Camera')
    widget.optCamera.setObjectName('optCamera')
    bgrpSource.addButton(widget.optFile, 1)
    bgrpSource.addButton(widget.optCamera, 2)
    bgrpSource.buttonClicked.connect(lambda: radiohandler(widget))
    # ~ bgrpSource.buttonClicked.connect(shambo)
    hbox1.addWidget(lblSource)
    hbox1.addWidget(widget.optFile)
    hbox1.addWidget(widget.optCamera)
    
    hbox2 = QHBoxLayout()
    lblFile = QLabel('File:')
    widget.txtFile = QLineEdit()
    widget.txtFile.setObjectName('txtFile')
    btnBrowseFile = QPushButton('Browse...')
    btnBrowseFile.clicked.connect(lambda: on_btnBrowseFile_clicked(widget))
    hbox2.addWidget(lblFile)
    hbox2.addWidget(widget.txtFile)
    hbox2.addWidget(btnBrowseFile)
    
    vbox1.addWidget(widget.chkGrayScale)
    vbox1.addLayout(hbox1)
    vbox1.addLayout(hbox2)

    widget.setLayout(vbox1)
    # ~ widget.img = None
    for item in widget.findChildren(QWidget):
        item.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    
    widget.optCamera.setChecked(True)
    
    return widget
    
def radiohandler(widget):
    print('radiohandler')
    # ~ print(widget.findChild(QLineEdit, 'txtFile').text())
    mainFunc(widget)
    mysignal.imageSignal.emit(widget.outputImg)

def on_btnBrowseFile_clicked(widget):
    # ~ idx = self.lstScript.currentRow()
    # ~ pluginObject = self.scriptList[idx][0]
    fname, _filter = QFileDialog.getOpenFileName(None, 'Select Image File', 
                    QDir.currentPath(), fileFilter)
    print(fname)
    if fname:
        widget.optFile.setChecked(True)
        widget.txtFile.setText(fname)  # on cancel fname is empty string so no need to wrap it in if statement
    
# ~ def mainFunc(file_ = None, widget = None):
def mainFunc(widget, playing):
    
    # ~ grayScale = widget.findChild(QCheckBox, 'chkGrayScale').isChecked()
    # ~ useFile = widget.findChild(QRadioButton, 'optFile').isChecked()
    # ~ useCamera = widget.findChild(QRadioButton, 'optCamera').isChecked()
    grayScale = widget.chkGrayScale.isChecked()
    useFile = widget.optFile.isChecked()
    useCamera = widget.optCamera.isChecked()
    # ~ print('useFile, useCamera:  ', useFile, ', ', useCamera)
    
     
    if useFile:
        if widget.inputImg is None:
            file_ = widget.txtFile.text()
            if grayScale:
                widget.outputImg = cv.imread(file_, 0)
            else:
                img = cv.imread(file_)
                widget.outputImg = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        else:
            pass
    elif useCamera:
        
        if playing == False:
            # read 40 times to equalize lighting
            for i in range(40):
                cap.read()
            
        ret, widget.outputImg = cap.read() 
        if grayScale:
            widget.outputImg = cv.cvtColor(widget.outputImg, cv.COLOR_BGR2GRAY)
        else:
            widget.outputImg = cv.cvtColor(widget.outputImg, cv.COLOR_BGR2RGB)

        


