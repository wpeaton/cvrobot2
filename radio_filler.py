from PyQt5.QtWidgets import (QRadioButton, QGroupBox, QGridLayout,
                             QButtonGroup)
                             
# TODO TODO TODO
# TODO TODO TODO
#
# look into using type hints as specified in PEP 484 
#
# TODO TODO TODO
# TODO TODO TODO
# TODO TODO TODO

import re

def radio_filler(group_caption, labels, buttons_per_row = None, tool_tips = None):
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
    button_group = QButtonGroup()
    bname = re.split("[\'\/ ,.]+", group_caption)
    bname = ' '.join(bname).title().replace(' ', '')
    bname = 'bgrp' + bname
    button_group.setObjectName(bname)
    
    for idx, label in enumerate(labels):
        radio_button = QRadioButton(label)
        # re.split seems to be the only way to quickly split on multiple
        # delimiters
        oname = re.split("[\'\/ ,.]+", label)
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
        
        
    
    
    
