#!/usr/bin/env python
from __future__ import print_function
import sys
import copy

import configobj
import validate

#~ from PyQt4 import QtGui
#~ from PyQt4 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

gfont = None  # global font. used everywhere



class Option(object):
    """Description and value of an option"""
    def __init__(self, name, section, type, args, kwargs, default, comment, widget_maker, check):
        self.name = name
        self.section = section
        self.type = type
        self.args = args
        self.kwargs = kwargs
        self.default = default
        self.comment = comment
        self.check = check
        self.widget_maker = widget_maker

    def get(self):
        """Get current value of the option"""
        return self.section[self.name]

    def set(self, value):
        """Get current value of the option"""
        # Workaround for problem in validate with lists from string
        value = str(value) # Start with a normal string
        if self.type.endswith('list'):
            value = [x.strip() for x in value.split(',')]
        try:
            self.section[self.name] = self.check(value, *self.args, **self.kwargs)
        except:
            pass

    def __repr__(self):
        """Convert option to string for debugging purposes"""
        return 'Option(%s,%s,%s,%s,%s,%s,%s)'%(self.name, self.section, self.type, self.args, self.kwargs, self.default, self.comment)

    def restoreDefault(self):
        """Change option value to the default value"""
        self.section.restore_default(self.name)

    def isDefault(self):
        """Check whether the option has the default value"""
        return self.name in self.section.defaults

    def widget(self):
            return self.widget_maker(self, *self.args, **self.kwargs)


class ConfigPage(QtWidgets.QWidget):
    """Container for widgets describing options in a section"""
    def __init__(self, section, item, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        layout = QtWidgets.QFormLayout(self)

        for option in [section[x] for x in section.scalars]:
            valueWidget = option.widget()
            valueWidget.optionChanged.connect(self.optionChanged.emit) 
            option_title = option.name.replace('_',' ')
            option_title = option_title[0].upper() + option_title[1:]
            layout.addRow(option_title, valueWidget)

        self.item = item # Store SectionBrowser item corresponding to this page
        self.conf = section # Store configuration section corresponding to this page

    optionChanged = QtCore.pyqtSignal(Option) # Chain signal upwards

    def restoreDefault(self):
        """Restore default value to all widgets on the page"""
        for widget in [self.layout().itemAt(i) for i in range(self.layout().count())]:
            try:
                widget.widget().restoreDefault()
            except AttributeError: # Skip widgets that can't be restored
                pass

class SectionBrowser(QtWidgets.QWidget):
    """TreeView browser of configuration sections. Also manages creating of config pages. It's a bit messy."""
    def __init__(self, conf, validator, font, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        layout = QtWidgets.QVBoxLayout(self)
        self.validator = validator

        # Create treeview
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setFont(font)
        self.tree.header().hide()
        self.tree.currentItemChanged.connect(lambda new, old: self.currentItemChanged.emit(new))
        layout.addWidget(self.tree)

        # Box that displays add/remove section buttons
        buttonBox = QtWidgets.QWidget()
        buttonLayout = QtWidgets.QHBoxLayout(buttonBox)
        self.addButton = QtWidgets.QPushButton('Add section')
        self.addButton.setIcon(QtGui.QIcon.fromTheme('list-add'))
        self.addButton.setEnabled(False)
        self.addButton.clicked.connect(lambda: self.addEmptySection(self.tree.currentItem()))
        buttonLayout.addWidget(self.addButton)

        self.removeButton = QtWidgets.QPushButton('Remove section')
        self.removeButton.setIcon(QtGui.QIcon.fromTheme('list-remove'))
        self.removeButton.setEnabled(False)
        buttonLayout.addWidget(self.removeButton)
        self.removeButton.clicked.connect(lambda: self.removeSection(self.tree.currentItem()))
        layout.addWidget(buttonBox)
        self.tree.currentItemChanged.connect(self.activateButtons)

        self.conf = conf # Store configuration
        self.page_lookup = {} # Mappig from treeview item to configuration page
        self.type_mapping = ConfigWindow.type_mapping

    # A few signals
    currentItemChanged = QtCore.pyqtSignal(QtWidgets.QTreeWidgetItem)
    pageAdded = QtCore.pyqtSignal(ConfigPage)
    pageRemoved = QtCore.pyqtSignal(ConfigPage)
    sectionAdded = QtCore.pyqtSignal(configobj.Section)
    sectionRemoved = QtCore.pyqtSignal(configobj.Section)

    def addSection(self, newsection):
        """Take a configuration section and add corresponding page and treeview item"""
        if newsection.name == None: # Top-level
            item = QtWidgets.QTreeWidgetItem(self.tree, ['Root'])
            self.tree.addTopLevelItem(item)
        else:
            parent_item = newsection.parent.tree_item
            item = QtWidgets.QTreeWidgetItem(parent_item, [newsection.name])
        item.setExpanded(True)

        page = ConfigPage(newsection, item)
        self.pageAdded.emit(page)
        newsection.tree_item = item
        self.page_lookup[id(item)] = page

        pages = [page]
        for section in [newsection[x] for x in newsection.sections]:
            pages.extend(self.addSection(section))

        return pages

    def activateButtons(self, item):
        """Activate add/remove section buttons if appropriate"""
        page = self.page_lookup[id(item)]
        conf = page.conf
        self.addButton.setEnabled(conf.many)
        self.removeButton.setEnabled(conf.optional)

    def addEmptySection(self, item):
        """Add a new empty section based on the spec of the parent section corresponding to item"""
        parent = self.page_lookup[id(item)].conf # Load combined config for page matching selected item
        print('added empty section')
        spec = parent.spec['__many__'] # Get spec
        conf = configobj.ConfigObj(configspec=spec)
        conf.validate(self.validator) # Create an empty config matching spec

        combined = merge_spec(conf, spec, self.type_mapping) # Combine spec and new config

        name, ok = QtWidgets.QInputDialog.getText(self, 'Add new section', 'Section name:')
        if ok:
            name = str(name)
            combined.name = name
            combined.parent = parent
            parent[name] = combined

            # Copy new config information into old config
            # Workaround for ConfigObj issues
            parent.conf[name] = {}
            def fix_depth(section):
                section.depth = section.parent.depth + 1
                [fix_depth(s) for s in section.sections]
            for key in conf:
                parent.conf[name][key] = conf[key]
                conf[key].parent = parent.conf[name][key]
                if isinstance(conf[key], configobj.Section):
                    fix_depth(conf[key])

            self.addSection(combined)
            self.sectionAdded.emit(combined)

    def removeSection(self, item):
        """Delete configuration section corresponding to item"""
        item.parent().removeChild(item)
        page = self.page_lookup[item]
        self.sectionRemoved.emit(page.conf)
        del page.conf.conf.parent[str(item.text(0))]
        self.pageRemoved.emit(page)
        del self.page_lookup[item]


class MyScrollArea(QtWidgets.QScrollArea):
    """QtGui.QScrollArea which has a more sensible sizeHint"""
    def __init__(self, parent=None):
        QtWidgets.QScrollArea.__init__(self, parent)
    def sizeHint(self):
        if self.widget() != None:
            return self.widget().sizeHint()*1.1
        else:
            return QtCore.QSize(10, 10)

class MyWidget(QtWidgets.QWidget):
    """Base for widget describing an option"""
    def __init__(self, option, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.option = option
        self.onlywidget = False

    def init(self, option, main_widget, change_signal):
        """Initialization that has to be performed after some actions made in __init__ in derived classes"""
        self.main_widget = main_widget
        self.main_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.layout.addWidget(main_widget)

        self.myconnect(change_signal, self.setValue)
        self.myconnect(change_signal, self.validate)

        # Add validity icon
        self.isValidIcon = QtWidgets.QLabel()
        self.isValidIcon.setScaledContents(True)
        self.isValidIcon.setPixmap(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxWarning).pixmap(256, 256))
        self.isValidIcon.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.isValidIcon.setMaximumHeight(self.main_widget.height()*0.8)
        self.isValidIcon.setMaximumWidth(self.main_widget.height()*0.8)
        self.isValidIcon.hide()
        self.layout.addWidget(self.isValidIcon)

        # Add button to restore default value
        self.restoreDefaultButton = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_DialogResetButton), '')
        self.restoreDefaultButton.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.restoreDefaultButton.clicked.connect(self.restoreDefault)
        self.restoreDefaultButton.setEnabled(self.option.default != None)
        self.restoreDefaultButton.setToolTip('Restore default value')
        self.layout.addWidget(self.restoreDefaultButton)

        if option.comment:
            main_widget.setToolTip(option.comment)

        # Set displayed value if possible
        try:
            self.option.get()
        except KeyError:
            return

        # No actual change has happened, so prevent the new value from being written to config
        self.onlywidget = True
        self.updateDisplay()
        self.onlywidget = False

    def validate(self, value):
        """Check if the entered value is valid accoring to the spec"""
        value = str(value) # Start with a normal string
        if self.option.type.endswith('list'):
            value = [x.strip() for x in value.split(',')]
        try:
            self.option.check(value, *self.option.args, **self.option.kwargs)
        except Exception as e:
            self.isValidIcon.setToolTip(str(e))
            self.isValidIcon.show()
            return
        self.isValidIcon.hide()

    def myconnect(self, signal, func):
        """Helper to conenct to both new and old-style signals"""
        #~ print('myconnect')
        if isinstance(signal, str):
            #~ QtCore.QObject.connect(self.main_widget, QtCore.SIGNAL(signal), func)
            #~ signal = QtCore.SIGNAL(signal)
            #~ self.main_widget.signal.connect(func)
            print(repr(signal))
            #~ print(str)
            #~ pass
        else:
            signal.connect(func)

    def setIsDefault(self):
        """Tell widget that it represents a default value"""
        style = ''
        for widget in ['QCheckBox', 'QSpinBox', 'QDoubleSpinBox', 'QComboBox', 'QLineEdit']:
            style += '%s {color: gray; font-size: %fpt; font-style: italic}\n'% (widget, gfont.pointSizeF())
        self.main_widget.setStyleSheet(style)
        self.restoreDefaultButton.setEnabled(False)

    def unsetIsDefault(self):
        """Tell widget that it no longer represents a default value"""
        style = ''
        for widget in ['QCheckBox', 'QSpinBox', 'QDoubleSpinBox', 'QComboBox', 'QLineEdit']:
            style += '%s {font-size: %fpt; }\n'% (widget, gfont.pointSizeF())
        self.main_widget.setStyleSheet(style)
        # ~ self.main_widget.setStyleSheet('')
        self.restoreDefaultButton.setEnabled(self.option.default != None)

    def restoreDefault(self):
        """Reset option to default value"""
        try:
            self.option.restoreDefault()
        except KeyError:
            return

        self.onlywidget = True
        self.updateDisplay()
        self.onlywidget = False

        self.setIsDefault()
        self.optionChanged.emit(self.option)

    def updateDisplay(self):
        """Update widget after a change in the options"""
        if self.option.isDefault():
            self.setIsDefault()

    optionChanged = QtCore.pyqtSignal(Option)

    def setValue(self, value):
        """Set option value to value"""
        if not self.onlywidget:
            self.option.set(value)
            self.optionChanged.emit(self.option)
            self.unsetIsDefault()

# Validator to check string length
#~ class LengthValidator(QtGui.QValidator):
    #~ """Validator which enforces string lenght limits"""
    #~ def __init__(self, min=0, max=None, parent = None):
        #~ QtGui.QValidator.__init__(self, parent)
        #~ self.min = min
        #~ self.max = max
    #~ def fixup(self, inp):
        #~ if self.min and len(inp) < self.min:
            #~ inp = inp.ljust(self.min)
        #~ elif self.max and input.length() > self.max:
            #~ inp = inp[:self.max]
    #~ def validate(self, inp, pos):
        #~ print(type(inp))
        #~ print(repr(inp))
        #~ inp = QtCore.QString(inp)
        #~ if self.min and len(inp) < self.min:
            #~ print('smaller than min')
            #~ return (QtGui.QValidator.Invalid, pos)
        #~ elif self.max and len(inp) > self.max:
            #~ print('bigger than max')
            #~ return (QtGui.QValidator.Invalid, pos)
        #~ else:
            #~ print('acceptable. pos is %s %s' % (type(pos), repr(pos)))
            #~ return (QtGui.QValidator.Acceptable, pos)
            #~ return QtGui.QValidator.Acceptable



class MyLineEdit(MyWidget):
    """Widget representing a text-like option"""
    def __init__(self, option, min = None, max = None, parent = None):
        MyWidget.__init__(self, option, parent)
        main_widget = QtWidgets.QLineEdit(self)

        if min != None:
            min = int(min)
        if max != None:
            max = int(max)
        #~ main_widget.setValidator(LengthValidator(min, max))

        self.init(option, main_widget, main_widget.textChanged)
        #~ print('setvalidator 355')

    def updateDisplay(self):
        MyWidget.updateDisplay(self)
        self.main_widget.setText(str(self.option.get()))
        #~ print('setvalidator 360')
        # ~ print('frickin le update. ', self.main_widget.text())
        # ~ app.processEvents()

class MyIpEdit(MyLineEdit):
    """Widget representing an IP address"""
    def __init__(self, option, parent = None):
        MyLineEdit.__init__(self, option, parent)
        self.main_widget.setInputMask('000.000.000.000')
        if option.get() == option.default: # Seems like a bug in QtGui.QLineEdit. If setInputMask is used, the stylesheet must be set again
            self.setIsDefault()

class MyListEdit(MyWidget):
    """Widget representing a list"""
    def __init__(self, option, min = None, max = None, parent = None):
        MyWidget.__init__(self, option, parent)
        main_widget = QtWidgets.QLineEdit(self)
        self.init(option, main_widget, main_widget.textChanged)
        #~ main_widget = QtGui.QListWidget(self)
        #~ self.init(option, main_widget, main_widget.currentRowChanged)

    def updateDisplay(self):
        MyWidget.updateDisplay(self)
        #~ if type(self.option.get()) is list:
            #~ for item in self.option.get():
                #~ if type(item) is int or type(item) is float:
                    #~ self.main_widget.addItem(repr(item))
                #~ else:
                    #~ self.main_widget.addItem(repr(item))
        self.main_widget.setText(', '.join([str(x) for x in self.option.get()]))

class MyCheckBox(MyWidget):
    """Widget representing a boolean option"""
    def __init__(self, option, parent=None):
        MyWidget.__init__(self, option, parent)
        main_widget = QtWidgets.QCheckBox(self)

        self.init(option, main_widget, main_widget.toggled)

    def updateDisplay(self):
        MyWidget.updateDisplay(self)
        self.main_widget.setChecked(validate.bool_dict[self.option.get()])

class MyComboBox(MyWidget):
    """Widget representing a multiple-choice option"""
    def __init__(self, option, options=[], parent=None):
        MyWidget.__init__(self, option, parent)
        main_widget = QtWidgets.QComboBox(self)
        for value in options:
            main_widget.addItem(str(value))

        # ~ self.init(option, main_widget, 'currentIndexChanged(QString)')
        self.init(option, main_widget, main_widget.currentTextChanged)

    def updateDisplay(self = False):
        MyWidget.updateDisplay(self)
        if self.option.get() != None:
            self.main_widget.setCurrentIndex(self.main_widget.findText(self.option.get()))
        self.main_widget.setCurrentIndex(self.main_widget.findText(self.option.get()))
        # ~ print('self.option.get() ', self.option.get())

class SliderWithLineEdit(QtWidgets.QWidget):
    """Slider which displays its current value in a box next to it"""
    def __init__(self, type, min, max, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        if type == 'float':
            self.decimals = 2
        else:
            self.decimals = 0

        self.type = type

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        if type == 'float':
            min = float(min)*10**self.decimals
            max = float(max)*10**self.decimals
        else:
            min = int(min)
            max = int(max)
        self.slider.setMinimum(min)
        self.slider.setMaximum(max)
        self.layout.addWidget(self.slider)
        self.edit = QtWidgets.QLineEdit(str(self.slider.value()))
        self.edit.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        if type == 'float':
            self.edit.setValidator(QtGui.QDoubleValidator(min, max, self.decimals, None)) # Provide parent explicitly (QtGui.QTBUG-16100)
        else:
            self.edit.setValidator(QtGui.QIntValidator(min, max, None)) # Provide parent explicitly (QtGui.QTBUG-16100)
        self.layout.addWidget(self.edit)
        # ~ metrics = QtGui.QFontMetrics(QtWidgets.QApplication.font())
        metrics = QtGui.QFontMetrics(gfont)
        if type == 'float':
            self.edit.setMaximumWidth(metrics.width(len(str(max))*"8"+"."+"8"))
        else:
            self.edit.setMaximumWidth(metrics.width(len(str(max))*"8"+"8"))
        self.edit.textChanged.connect(self.setSliderValue)
        self.slider.valueChanged.connect(self.setEditValue)

        self.reaction = False

    def setSliderValue(self, s):
        if self.reaction: # Prevent lineedit change from triggering this
            self.reaction = False
            return
        self.reaction = True
        try:
            if self.type == 'float':
                self.slider.setValue((round(float(s)*10**self.decimals)))
            else:
                self.slider.setValue(int(s))
        except TypeError:
            pass
        except ValueError:
            if s == '':
                self.slider.setValue(self.slider.minimum())

    def setEditValue(self, i):
        if self.reaction: # Prevent slider change from triggering this
            self.reaction = False
            return
        self.reaction = True
        if self.type == 'float':
            format = '%.'+str(self.decimals)+'f'
            self.edit.setText(format%(float(i)/float(10**self.decimals)))
        else:
            self.edit.setText(str(i))

    def setValue(self, value):
        self.setSliderValue(str(value))
        self.edit.setText(str(value))


class MySlider(MyWidget):
    """Widget representing a number with min and max specified"""
    def __init__(self, option, min=0, max=100, parent=None):
        MyWidget.__init__(self, option, parent)
        main_widget = SliderWithLineEdit(option.type, min, max)
        self.init(option, main_widget, main_widget.edit.textChanged)

    def updateDisplay(self):
        MyWidget.updateDisplay(self)
        self.main_widget.setValue(self.option.get())
        # ~ print(self.option.get())
        # ~ app.processEvents()

class MySpinBox(MyWidget):
    """Widget representing a number with min or max unspecified"""
    def __init__(self, option, min=None, max=None, parent=None):
        self.decimals = 2
        MyWidget.__init__(self, option, parent)
        if option.type == 'float':
            main_widget = QtWidgets.QDoubleSpinBox()
            main_widget.setDecimals(self.decimals)
            conv = float
        else:
            main_widget = QtWidgets.QSpinBox()
            if option.default != None:
                option.default = int(option.default)
            conv = int

        if option.default != None:
            option.default = conv(option.default)
        if min != None:
            main_widget.setMinimum(conv(min))
        if max != None:
            main_widget.setMaximum(conv(max))

        self.init(option, main_widget, main_widget.valueChanged)

    def updateDisplay(self):
        MyWidget.updateDisplay(self)
        if self.option.get() != None:
            self.main_widget.setValue(self.option.get())

def create_widget_integer(option, min=None, max=None):
    """Create widget for integer option"""
    if min != None and max != None:
        widget = MySlider(option, min, max)
    else:
        widget = MySpinBox(option, min, max)
    return widget

def create_widget_string(option, min=None, max=None):
    """Create widget for string option"""
    widget = MyLineEdit(option, min, max)
    return widget

def create_widget_float(option, min=None, max=None):
    """Create widget for float option"""
    if min != None and max != None:
        widget = MySlider(option, min, max)
    else:
        widget = MySpinBox(option, min, max)
    return widget

def create_widget_ip_addr(option):
    """Create widget for ip_addr option"""
    widget = MyIpEdit(option)
    return widget

def create_widget_boolean(option):
    """Create widget for boolean option"""
    widget = MyCheckBox(option)
    return widget

def create_widget_option(option, *options):
    """Create widget for option option"""
    widget = MyComboBox(option, options)
    return widget

def create_widget_list(option, min=None, max=None):
    """Create widget for any kind of list option"""
    widget = MyListEdit(option, min, max)
    return widget

validator = validate.Validator()

#~ class ConfigWindow(QtWidgets.QMainWindow):
class ConfigWindow(QtWidgets.QWidget):
    """Window which contains controls for making changes to a ConfigObj"""

    APPLY_IMMEDIATELY = 1 # GNOME style, apply settings immediately
    APPLY_OK = 2 # KDE style, apply settings when OK is pressed
    type_mapping = {'integer':(create_widget_integer, validator.functions['integer']),
            'float':(create_widget_float, validator.functions['float']),
            'boolean':(create_widget_boolean, validator.functions['boolean']),
            'string':(create_widget_string, validator.functions['string']),
            'ip_addr':(create_widget_ip_addr, validator.functions['ip_addr']),
            'list':(create_widget_list, validator.functions['list']),
            'force_list':(create_widget_list, validator.functions['force_list']),
            'tuple':(create_widget_list, validator.functions['tuple']),
            'int_list':(create_widget_list, validator.functions['int_list']),
            'float_list':(create_widget_list, validator.functions['float_list']),
            'bool_list':(create_widget_list, validator.functions['bool_list']),
            'string_list':(create_widget_list, validator.functions['string_list']),
            'ip_addr_list':(create_widget_list, validator.functions['ip_addr_list']),
            'mixed_list':(create_widget_list, validator.functions['mixed_list']),
            'pass':(create_widget_string, validator.functions['pass']), # BUG: This will lead to a string always being saved back
            'option':(create_widget_option, validator.functions['option'])}

    def __init__(self, conf, spec, title = 'Configure', when_apply = APPLY_IMMEDIATELY, debug = False, 
                 type_mapping=None, parent = None, fontsize = 12.):
        #~ QtWidgets.QMainWindow.__init__(self, parent)
        super(ConfigWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Dialog)
        
        self.when_apply = when_apply
        self.type_mapping = ConfigWindow.type_mapping
        if type_mapping != None:
            self.type_mapping.update(type_mapping)


        # try to change default font size
        #~ font = QtGui.QFont
        #~ font.setFamily(self.font());
        font = self.font()
        font.setPointSizeF(fontsize)
        
        self.setFont(font)
        
        global gfont
        gfont = font
        
        style = 'QWidget { font-size: %fpt;} \n' % font.pointSizeF()
        style += 'QToolTip { font-size: %fpt;} ' % font.pointSizeF()
        
        self.setStyleSheet(style )

        self.validator = validate.Validator()
        res = conf.validate(self.validator, preserve_errors=True)

        # Make changes to a copy of the original conf if needed
        if when_apply != ConfigWindow.APPLY_IMMEDIATELY:
            self.original_conf = conf
            conf = copy.deepcopy(conf)
        else:
            self.original_conf = conf

        self.conf = conf

        self.setWindowTitle(title)
        options = merge_spec(conf, spec, self.type_mapping)
        self.options = options
        #~ main = QtWidgets.QWidget()
        #~ layout = QtWidgets.QVBoxLayout(main)
        layout = QtWidgets.QVBoxLayout()
        #~ self.setCentralWidget(main)

        splitter = QtWidgets.QSplitter()
        layout.addWidget(splitter)
        self.splitter = splitter
        browser = SectionBrowser(conf, self.validator, font = font)
        browser.currentItemChanged.connect(self.changePage)
        browser.pageAdded.connect(self.addPage)
        browser.pageRemoved.connect(self.removePage)

        if when_apply == ConfigWindow.APPLY_IMMEDIATELY: 
            browser.sectionAdded.connect(self.sectionAdded.emit)
            browser.sectionRemoved.connect(self.sectionRemoved.emit)

        if spec.sections != []: # Sections are possible
            splitter.addWidget(browser)

        if when_apply == ConfigWindow.APPLY_IMMEDIATELY:
            buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.RestoreDefaults)
        elif when_apply == ConfigWindow.APPLY_OK:
            buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.RestoreDefaults)
        buttons.button(QtWidgets.QDialogButtonBox.RestoreDefaults).clicked.connect(self.resetAll)
        buttons.button(QtWidgets.QDialogButtonBox.RestoreDefaults).setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DialogResetButton))

        if debug: # Show button to print current config as seen from outside
            dump_config = QtGui.QPushButton('Dump')
            buttons.addButton(dump_config, QtWidgets.QDialogButtonBox.HelpRole)
            def dump():
                print(self.original_conf)
            dump_config.clicked.connect(dump)

        buttons.accepted.connect(self.close)
        buttons.accepted.connect(self.updateOriginalConf)

        buttons.rejected.connect(self.close)

        layout.addWidget(buttons)

        configArea = MyScrollArea()
        self.configArea = configArea
        splitter.addWidget(configArea)
        splitter.setStretchFactor(1, 3)

        stacked = QtWidgets.QStackedWidget()
        configArea.setWidget(stacked)
        splitter.addWidget(configArea)
        configArea.setWidgetResizable(True)

        self.stacked = stacked

        self.pages = {}
        pages = browser.addSection(options)
        
        self.setLayout(layout)

    optionChanged = QtCore.pyqtSignal(Option)
    sectionAdded = QtCore.pyqtSignal(configobj.Section)
    sectionRemoved = QtCore.pyqtSignal(configobj.Section)

    def changePage(self, newItem):
        index = self.pages[id(newItem)]
        self.stacked.setCurrentIndex(index)

    def updateOriginalConf(self):
        if self.when_apply != ConfigWindow.APPLY_IMMEDIATELY: # Check what has changed
            def update(new, old, newly_added):
                added = [x for x in new.sections if x not in old.sections]
                for section in added:
                    if not newly_added:
                        self.sectionAdded.emit(new[section])
                    old[section] = {}

                removed = [x for x in old.sections if x not in new.conf.sections]
                for section in removed:
                    self.sectionRemoved.emit(new[section])
                    del old[section]

                for scalar in new.scalars:
                    # New section
                    if not scalar in old.scalars:
                        if not new[scalar].isDefault():
                            try:
                                old[scalar] = new[scalar].get()
                                self.optionChanged.emit(new[scalar])
                            except KeyError:
                                continue
                    else: # Old section
                        try:
                            if new[scalar].get() != old[scalar]:
                                self.optionChanged.emit(new[scalar])
                        except KeyError:
                            continue

                        if not new[scalar].isDefault():
                            old[scalar] = new[scalar].get()
                        else:
                            old.restore_default(scalar)

                for section in [x for x in new.sections]:
                    try:
                        update(new[section],old[section], newly_added or section in added)
                    except KeyError: # Section was removed
                        continue

            update(self.options,self.original_conf,False)
            self.original_conf.write()

    def resetAll(self):
        for page in [self.stacked.widget(i) for i in range(self.stacked.count())]:
            page.restoreDefault()

    def addPage(self, page):
        self.pages[id(page.item)] = self.stacked.addWidget(page)
        if self.when_apply == ConfigWindow.APPLY_IMMEDIATELY:
            page.optionChanged.connect(self.optionChanged.emit)

    def removePage(self, page):
        self.pages[page.item] = self.stacked.removeWidget(page)
        del self.pages[page.item]

def merge_spec(config, spec, type_mapping):
    """Combine config and spec into one tree in the form of Option objects"""
    combined = configobj.ConfigObj()

    combined.optional = '__many__' in spec.parent and spec != spec.parent
    combined.many = '__many__' in spec

    # Store origial conf and spec
    combined.conf = config
    combined.spec = spec

    # Recursively combine sections
    for section in config.sections:
        if section in spec:
            combined[section] = merge_spec(config[section], spec[section], type_mapping)
        elif '__many__' in spec:
            combined[section] = merge_spec(config[section], spec['__many__'], type_mapping)

        combined[section].name = section
        combined[section].parent = combined

    # Combine individual options
    for option in spec.scalars:
        comment = spec.inline_comments[option]
        if comment and comment.startswith('#'):
            comment = comment[1:].strip()
        fun_name, fun_args, fun_kwargs, default = validate.Validator()._parse_with_caching(spec[option]) # WARNING: Uses unoffical method!
        #~ print('fun_name, fun_args, fun_kwargs, default is ', fun_name, fun_args, fun_kwargs, default)
        combined[option] = Option(option, config, fun_name, fun_args, fun_kwargs, default, comment, type_mapping[fun_name][0], type_mapping[fun_name][1])

    return combined

def configure_externally(config, spec):
    """Launch a ConfigWindow in an external process"""
    import pickle, subprocess, time
    path = __file__
    if path.endswith('.pyc'):
        path = path[:-1]
    proc = subprocess.Popen([path], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    newconf = pickle.loads(proc.communicate(pickle.dumps((config, spec)))[0])
    newconf.write(sys.stdout)

if __name__ == '__main__':
    import pickle
    #~ conf, spec = pickle.loads(sys.stdin.read())
    spec = configobj.ConfigObj('examples/spec.txt', list_values=False)
    conf = configobj.ConfigObj('examples/config.txt', configspec=spec)
    app = QtWidgets.QApplication(sys.argv)
    # ~ wnd = ConfigWindow(conf, spec)
    wnd = ConfigWindow(conf, spec, when_apply=ConfigWindow.APPLY_OK)
    wnd.show()
    app.exec_()
    print(pickle.dumps(conf), end=' ')

