from plugin import Plugin
from widget_helpers import radio_filler, spinbox_slider

from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QFileDialog, QButtonGroup,
                             QGraphicsRectItem, QGraphicsLineItem,
                             QSizePolicy, QGraphicsSimpleTextItem
                             )
from PyQt5.QtGui import (QBrush, QPen, QFont, QColor)
from PyQt5.QtCore import QDir, pyqtSignal, QObject

import cv2 as cv
import numpy as np
import time


statusbar_message = 'show graphics items'

def getInstance():
    instance = ShowGraphicsItems()
    instance.setSizeMarginSpacing()
    
    return instance

class ShowGraphicsItems(Plugin):
        
    def __init__(self, parent = None):
        
        super(ShowGraphicsItems, self).__init__()
        
        self.setObjectName('show_graphics_items') # should be plugin name
        self.needsGraphicsView = True
        
        # declare all parameter widgets below
        vbox1 = QVBoxLayout()
        self.chkShowPass = QCheckBox('show pass/fail', checked = True, objectName = 'chkShowPass')
        vbox1.addWidget(self.chkShowPass)
        
        self.setLayout(vbox1)


        
    def mainFunc(self, playing, scriptList, scriptPos):
        
        if self.inputImg is not None:
            self.outputImg = self.inputImg
            
            pass_ = 0
            
            fx = 1.0
            fy = 1.0
            offset_x = 0.0
            offset_y = 0.0
            for i in range(scriptPos):
                widget = scriptList[i][1]
                if widget.objectName() == 'resize':
                    fx *= widget.dblFx.value()
                    fy *= widget.dblFx.value()
                        
                pass_ += widget.pass_
                for item in widget.graphicsItems:
                    try:
                        # ~ print('item.rect() ', item.rect())
                        if fx != 1.0:
                            item.setScale(1/fx)
                        # ~ if fy != 1.0:
                            # ~ item.setHeight(item.height()/fy)
                        if offset_x:
                            item.setX( (item.x() + offset_x)/fx )
                            # ~ item.setX( (item.x() + offset_x)/1.0 )
                            # ~ print('offset_x: ', offset_x, '  fx: ', fx)
                        if offset_y:
                            item.setY( (item.y() + offset_y)/fy )
                            # ~ item.setY( (item.y() + offset_y)/1.0 )
                        self.graphicsView.scene().addItem(item)
                        item.setZValue(1)
                    except RuntimeError as e:
                        print(time.time(), 'Runtime Error show_graphics_items mainFunc')
                        print(e)
                        
                if widget.objectName() == 'circles':
                    if widget.chkCrop.isChecked():
                        try:
                            circle = widget.graphicsItems[0]
                            # ~ circle = item
                            offset_x = circle.x()
                            offset_x = circle.rect().left()
                            offset_y = circle.y()
                            offset_y = circle.rect().top()
                            # ~ print('offer setter ', offset_x)
                        except IndexError as e:
                            print(e)
            if self.chkShowPass.isChecked():
                # ~ h = self.graphicsView.scene().height()
                # ~ w = self.graphicsView.scene().width()
                h = self.inputImg.shape[0]
                w = self.inputImg.shape[1]
                
                # ~ sfh = float(h)/float(self.graphicsView.minimumHeight())
                # ~ sfw = float(w)/float(self.graphicsView.minimumWidth())
                # ~ sf = min(sfh,sfw)
                
                outlineRect = QGraphicsRectItem(0, 0, w, h)
                outlineLine = QGraphicsLineItem(0, h, w, 0)
                
                font = QFont("DejaVu Sans", 45)
                
                if pass_ == scriptPos:
                    # the overall result is pass
                    text = 'PASS'
                    pen = QPen(QColor(0, 255, 0), 8) #green for pass
                    brush = QBrush(QColor(0, 255, 0))
                      
                else:
                    # overall result is fail
                    text = 'FAIL'
                    pen = QPen(QColor(255, 0, 0), 8) #red for fail
                    brush = QBrush(QColor(255, 0, 0))
                
                    outlineLine.setPen(pen)
                    self.graphicsView.scene().addItem(outlineLine)
                    outlineLine.setZValue(1)
                
                outlineRect.setPen(pen)
                self.graphicsView.scene().addItem(outlineRect)
                textItem = QGraphicsSimpleTextItem(text, )
                textItem.setFont(font)
                textItem.setBrush(brush)
                textItem.setPos(w/10.0, h/10.0)
                self.graphicsView.scene().addItem(textItem)
                textItem.setZValue(1)
    
