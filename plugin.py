from PyQt5.QtWidgets import (QWidget, QLabel, QDoubleSpinBox, QCheckBox,
                             QSpinBox, QSlider, QGroupBox,
                             QRadioButton, QLineEdit, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QStackedLayout, QLayout,
                             QFileDialog, QButtonGroup,
                             QSizePolicy,
                             )
from PyQt5.QtCore import QObject

class Plugin(QWidget):
    '''base class for all plugins
       this class is pretty small it only contains a few default properties
       
       the big methods implemented are getParams and setParams
       
       most of the code will reside in subclasses
    '''
    def __init__(self, parent = None):
        
        super(QWidget, self).__init__()
                
        # defaults for properties
        self.isSource = False
        self.inputImg = None
        self.outputImg = None
        self.inputRow = 1
        self.targetImg = None
        self.needsGraphicsView = False
        self.needsEventFilter = False
        self.needsTarget = False
        self.graphicsItems = []
        self.pass_ = True
        
        self.buttonGroupList = [] # need to store button groups here to find later in get params
        self.Params = {}
        
    def setSizeMarginSpacing(self):
        # set all sizepolicy s to preferred
        for item in self.findChildren(QWidget):
            # ~ print(item.objectName())
            # ~ item.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # set margins and spacing for all Layouts
        for item in self.findChildren(QLayout):
            item.setContentsMargins(0, 0, 0, 0)
            item.setSpacing(1)
        
    # ~ def getParams(self, maindain):
    def getParams(self):
        params = {}  # initialize to empty dictionary
        params['plugin_name'] = self.objectName()           
        params['inputRow'] = self.inputRow
        # ~ print('in getParams inputRow is ', self.inputRow)
            
        for bgroup in self.findChildren((QButtonGroup)):
            params[bgroup.objectName()] = bgroup.checkedId()
            
            # do i need to call radio_handler?  -- let's try it
            self.radio_handler()
        
        for widget in self.findChildren((QCheckBox, QGroupBox)):
            if widget.isCheckable():
                params[widget.objectName()] = widget.isChecked()
                
        # ignore sliders. so far sliders are only used in conjunction with
        # spinBoxes
        
        for spinbox in self.findChildren((QSpinBox, QDoubleSpinBox)):
            # ~ print('spinbox.objectName() ', spinbox.objectName() )
            params[spinbox.objectName()] = spinbox.value()
        
        # ~ for checkbox in self.findChildren(()):
            # ~ params[checkbox.objectName()] = checkbox.isChecked()
            
        for line_edit in self.findChildren((QLineEdit)):
            if line_edit.objectName() == 'qt_spinbox_lineedit':
                pass
            else:
                params[line_edit.objectName()] = line_edit.text()
        
        self.Params = params
        return params
    
    def setParams(self, params):
        ''' params argument should be a dictionary that was read from disk
            this function is almost the exact reverse of getParams
            
            the dictionary we write to disk is all typed correctly (int,
            boole, etc). But the dictionary we get from configparser is
            all strings, so we must convert data types.
        '''
        self.inputRow = int(params['inputRow'])
        # ~ print('in setParams inputRow is ', self.inputRow)
        
        for bgroup in self.buttonGroupList:
            # by convention, we use the objectName of the QButtonGroup
            # as the dictionary key and checkedId() as the value
            bgroup.button(int(params[bgroup.objectName()])).setChecked(True) 
            
            # do i need to call radio_handler?  -- let's try it
            self.radio_handler()
        
        for spinbox in self.findChildren((QSpinBox)):
            # ~ print(spinbox.objectName())
            spinbox.setValue(int(params[spinbox.objectName()]))
            
        for spinbox in self.findChildren((QDoubleSpinBox)):
            # ~ print(spinbox.objectName())
            spinbox.setValue(float(params[spinbox.objectName()]))
        
        for widget in self.findChildren((QCheckBox, QGroupBox)):
            if widget.isCheckable():
                b = params[widget.objectName()] == 'True'
                widget.setChecked(b)
            
        for line_edit in self.findChildren((QLineEdit)):
            # ~ print('line_edit.objectName() ', line_edit.objectName())
            if line_edit.objectName() not in ['qt_spinbox_lineedit']:
                line_edit.setText(params[line_edit.objectName()])
        
        self.Params = params
        
    def radio_handler(self):
        pass
        
