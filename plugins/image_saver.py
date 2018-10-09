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
from PyQt5.QtCore import QDir, pyqtSignal, QObject

import cv2 as cv
import numpy as np

cap = cv.VideoCapture(0)

statusbar_message = 'Save processed image to disk'

def getInstance():
    ''' provides easy way for plugin finder to get an instance of this
        particular plugin
    '''
    instance = ImageSaver()
    instance.setSizeMarginSpacing()
    
    return instance

class ImageSaver(Plugin):
    def __init__(self, parent = None):
        
        super(ImageSaver, self).__init__()

        self.Params = {}
        
        self.setObjectName('image_saver') # should be plugin name
        
        self.isSource = True
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        hbox1 = QHBoxLayout()
        self.chkGrayScale = QCheckBox('Gray Scale')
        self.chkGrayScale.setObjectName('chkGrayScale')
        btnSaveNow = QPushButton('Save Now')
        btnSaveNow.clicked.connect(self.on_btnSaveNow_clicked)
        hbox1.addWidget(self.chkGrayScale)
        hbox1.addWidget(btnSaveNow)
                
        hbox2 = QHBoxLayout()
        lblFile = QLabel('File:')
        self.txtFile = QLineEdit()
        self.txtFile.setObjectName('txtFile')
        btnBrowseFile = QPushButton('Browse...')
        btnBrowseFile.clicked.connect(self.on_btnBrowseFile_clicked)
        hbox2.addWidget(lblFile)
        hbox2.addWidget(self.txtFile)
        hbox2.addWidget(btnBrowseFile)
        
        vbox1.addLayout(hbox1)
        vbox1.addLayout(hbox2)

        self.setLayout(vbox1)
        # ~ widget.img = None
        for item in self.findChildren(QWidget):
            item.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def on_btnBrowseFile_clicked(self):

        fileFilter = 'JPEG (*.jpg);;PNG (*.png)'
        selectedFilter = 'PNG (*.png)'
        fname, _filter = QFileDialog.getSaveFileName(None, 'Select Image File', 
                        QDir.currentPath(), fileFilter, selectedFilter)
        print(fname)
        if fname:
            self.txtFile.setText(fname)  # on cancel fname is empty string so no need to wrap it in if statement
        
    # ~ def mainFunc(file_ = None, widget = None):
    
    def on_btnSaveNow_clicked(self):
        
        fname = self.txtFile.text()
        
        if fname != '':
            img = self.inputImg
            
            if img.ndim == 3: # it's a color image. grayscale has no color. duh!
                if self.chkGrayScale.isChecked():
                    img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
                else:
                    #opencv assumes all images are BGR and automatically converts to RGB when saving.
                    # this is a real shame because we end up doing 
                    # many conversions.
                    img = cv.cvtColor(img, cv.COLOR_RGB2BGR)    
        
            cv.imwrite(fname, img)
        



    def mainFunc(self, playing, scriptList, row):
        
        # ~ self.outputImg = self.inputImg.copy()
        # don't think we need a copy. can be the same object, right?
        self.outputImg = self.inputImg
        

