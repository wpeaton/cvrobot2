''' collection of helper functions that generate
    commonly used layouts
'''


from PyQt5.QtWidgets import (QRadioButton, QGroupBox, QGridLayout,
                             QButtonGroup, QHBoxLayout, QVBoxLayout,
                             QSpinBox, QDoubleSpinBox, QSlider,
                             QLabel)
from PyQt5.QtCore import Qt, pyqtSignal

import math # need log10 for DoubleSlider
                             
# TODO TODO TODO
# TODO TODO TODO
#
# look into using type hints as specified in PEP 484 
#
# TODO TODO TODO
# TODO TODO TODO
# TODO TODO TODO

import re

def radio_filler( group_caption, labels, buttons_per_row = None, tool_tips = None):
    """ create a QGroupBox filled with a QGridLayout of QRadioButtons 
        that are part of a QButtonGroup
        
        group_caption: 
        
        labels:    list of strings that contain text for QRadioButtons
                   order of this list is important as the index is
                   used for QButtonGroup.Id
                   
        buttons_per_row: optional argument. number of QRadioButtons in
                         each row of the output QGridLayout.
                         
                         If None, all QRadioButtons
                         will be placed on one row. 
                         
        tool_tips: list of toolTip strings that will be added to each
                   QRadioButton.
                   
                   If None, no toolTips are added
    """
       
    group_box = QGroupBox(group_caption)
    grid = QGridLayout()
    bname = re.split("[\'\/ ,.]+", group_caption)
    bname = ' '.join(bname).title().replace(' ', '')
    bname = 'bgrp' + bname
    button_group = QButtonGroup(group_box)
    button_group.setObjectName(bname)
    # ~ button_group = QButtonGroup(group_box)
    
    
    for idx, label in enumerate(labels):
        radio_button = QRadioButton(label)
        # re.split seems to be the only way to quickly split on multiple
        # delimiters
        oname = re.split("[\'\/ ,.\n\-]+", label)
        oname = ' '.join(oname).title().replace(' ', '')
        oname = 'opt' + oname
        
        radio_button.setObjectName(oname)
        if tool_tips is not None:
            if len(tool_tips) == len(labels):
                radio_button.setToolTip(tool_tips[idx])
                
        if buttons_per_row is None:
            # all QRadioButtons go in row 0
            row = 0
            col = idx
        else:
            row = int(idx/buttons_per_row)
            col = idx % buttons_per_row
        button_group.addButton(radio_button, idx) # set Id to idx
        
        grid.addWidget(radio_button, row, col)
    
    group_box.setLayout(grid)
    
    return (group_box, button_group)
        
        
def spinbox_slider(spinbox, label = 'param', orientation = 'horizontal', min_ = 0, max_ = 1, 
                   single_step = 1, default_value = 1, decimals = 0, log = False):
    # single step for qsliders is worthless. doesn't work 
    
    if orientation == 'horizontal':
        box = QHBoxLayout()
        ori = Qt.Horizontal
    elif orientation == 'vertical':
        box = QVBoxLayout()
        ori = Qt.Vertical
    spinbox.setRange(min_, max_)
    spinbox.setValue(default_value)
    spinbox.setSingleStep(single_step)
    spinbox.setAccelerated(True)
    if decimals:
        slider = DoubleSlider(decimals = decimals, log = log, orientation = ori)
        slider.doubleValueChanged.connect(spinbox.setValue)
        # ~ slider.valueChanged.connect(spinbox.setValue)
    else:
        slider = QSlider(ori)
        slider.valueChanged.connect(spinbox.setValue)
        spinbox.valueChanged.connect(slider.setValue)
    # ~ slider.setRange(min_,max_)
    slider.setMinimum(min_)
    slider.setMaximum(max_)
    slider.setValue(default_value)
    # ~ slider.setSingleStep(single_step)
    # ~ print(slider.singleStep())
    box.addWidget(slider)
    box.addWidget(spinbox)
    box.addWidget(QLabel(label))
    
    return box
 
 
class DoubleSlider(QSlider):
    
    doubleValueChanged = pyqtSignal(float)
    
    def __init__(self, decimals=3, log = False, *args, **kargs):
        super(DoubleSlider, self).__init__( *args, **kargs)
        self._multi = 10 ** decimals
        self.log = log

        self.valueChanged.connect(self.emitDoubleValueChanged)
        
    def emitDoubleValueChanged(self):
        if self.log:
            value = math.pow(10, float(super(DoubleSlider, self).value()) / self._multi)
        else:
            value = float(super(DoubleSlider, self).value())/self._multi

        self.doubleValueChanged.emit(value)

    def value(self):

        if self.log:
            return math.pow(10, float(super(DoubleSlider, self).value()) / self._multi)
        else:
            return float(super(DoubleSlider, self).value()) / self._multi
        

    def setMinimum(self, value):
        if self.log:
            return super(DoubleSlider, self).setMinimum(math.log10(value) * self._multi)
        else:
            return super(DoubleSlider, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        if self.log:
            return super(DoubleSlider, self).setMaximum(math.log10(value) * self._multi)
        else:
            return super(DoubleSlider, self).setMaximum(value * self._multi)
        
    def setSingleStep(self, value):
        if self.log:
            return super(DoubleSlider, self).setSingleStep(math.log10(value) * self._multi)
        else:
            return super(DoubleSlider, self).setSingleStep(value * self._multi)
        
    def singleStep(self):
        if self.log:
            return math.pow(10, float(super(DoubleSlider, self).singleStep()) / self._multi)
        else:
            return float(super(DoubleSlider, self).singleStep()) / self._multi
    def setValue(self, value):

        if self.log:
            super(DoubleSlider, self).setValue(int(math.log10(value) * self._multi))
        else:
            super(DoubleSlider, self).setValue(int(value * self._multi))
    
    
    
