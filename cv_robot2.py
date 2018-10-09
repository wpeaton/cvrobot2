 
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtCore import (QDir, Qt, QTimer, QRectF, QPointF, QLineF, 
                          QSize, QObject)
from PyQt5.QtGui import ( QImage, QPainter, QPalette, QPixmap, QColor, 
                          QPen, QFont, QPageLayout)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
        QRadioButton, QTableWidgetItem, QCheckBox, QGroupBox, QSpinBox,
        QDoubleSpinBox, QLineEdit, QButtonGroup, QWidget,
        QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy,
        QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, 
        QGraphicsRectItem, QGraphicsEllipseItem, QGridLayout, QHBoxLayout,
        QVBoxLayout)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
import numpy as np
import configparser

running  = False #  flags that determine different program modes
training = False #  (i.e. running, training, and inspecting 

form_class = uic.loadUiType('cvr2b.ui')[0]

from plugins import *
import inspect

import threading
import time
import cv2 as cv
import sys

frame = None




# ~ if sys.version_info[0] < 3:
    # ~ import Queue
    # ~ q = Queue.Queue()
# ~ else:
    # ~ import queue
    # ~ q = queue.Queue()



# ~ inspect  = False #

capture_thread = None


font = cv.FONT_HERSHEY_SIMPLEX

capture = None





# ~ def grab(cam, queue, width, height, fps):
    # ~ global running
    # ~ global frame

    
    # ~ cap = cv.VideoCapture(0)

    # ~ while(running):

        
        # ~ ret, frame = cap.read()

        # ~ if queue.qsize() < 10:
            # ~ queue.put(frame)
        # ~ else:
            # ~ #print(queue.qsize())
            # ~ pass





# ~ class MyWindowClass(QtWidgets.QMainWindow, form_class):
    # ~ def __init__(self, parent=None):
        # ~ QtWidgets.QMainWindow.__init__(self, parent)
        # ~ self.setupUi(self)


class Robot(QtWidgets.QMainWindow, form_class):
    def __init__(self, parent=None):
        
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        # ~ super(ImageViewer, self).__init__()

        self.printer = QPrinter()
        self.scaleFactor = 0.0

        scene = QGraphicsScene()
        self.graphicsView.setScene(scene)
        # ~ self.graphicsView = QGraphicsView(self.scene)
        self.graphicsView.setBackgroundRole(QPalette.Base)
        self.graphicsView.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # ~ self.graphicsView.setScaledContents(True)
        
        self.editingLstScript = False  # flag that controls lstScript behavior
                                  
        
        self.statusbar.showMessage('')
        self.EventFilterWidget = None
        
        self.img = None
        self.imageItem = None # this is the QGraphicsPixmapItem version of self.img
        self.targetShape = None
        self.patchSize = 31
        
        
        self.lstCommands.clear()
        self.lstScript.clear()
        
        x = inspect.getmembers(plugins, inspect.ismodule)
        
        #delete 'plugins'
        for i, item in enumerate(x):
            if item[0] == 'plugins':
                del(x[i])
        
        self.pluginNames = [a[0] for a in x]
        self.pluginObjects = [a[1] for a in x]
                    
        self.scriptList = []
        self.lastWidget = self.dummyWidget
        
        self.lstCommands.addItems(self.pluginNames)
        
        self.createActions()
        self.createMenus()

        self.setWindowTitle("CV Robot")
        # ~ self.resize(500, 400)

        parameters = ['threshold']
        values = [ 0.6]
        maxes = [1.0]
        mins  = [0.0]
        stepsizes = [0.1]
        
        self.playing = False
        
        self.openScript(False, 'last_used.scr')
        
    def closeEvent(self, *args, **kwargs):
        #
        # Stuff I want to do when program closes
        
        self.saveScript(False, 'last_used.scr')
        
        print('closing now')
        
        global running
        running = False
        self.playing = False
               
   
    @QtCore.pyqtSlot(int)
    def on_chckEqualize_stateChanged(self, state):
        self.tgt = cv.imread('target.png') # , 0 is grayscale
        
        if True:
            print(self.tgt.shape[:2])
            span = self.tgt.shape[0]
            # ~ self.mask = np.zeros((span, span, 3), np.uint8)
            # ~ cv.circle( self.mask, center = (int(span/2), int(span/2)), 
                       # ~ radius = int(span/2), color = 255, thickness = -1)
            # invert the mask to see what happens
            self.mask = np.ones((span, span, 3), np.uint8)*255
            cv.circle( self.mask, center = (int(span/2), int(span/2)), 
                       radius = int(span/2), color = 0, thickness = -1)
        
        if self.tgt is None:
            print('None emmer effer')
            from shutil import copyfile
            copyfile('target_backup.png', 'target.png')
            self.tgt = cv.imread('target.png') # , 0 is grayscale
            
            if self.tgt is None:
                self.close()
            
        if self.chkEqualize.isChecked():
            # ~ clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            # ~ img = clahe.apply(img)
            if len(self.tgt.shape) == 3:  # assume BGR color image
                self.tgt = cv.cvtColor(self.tgt, cv.COLOR_BGR2YUV)
                split = cv.split(self.tgt)

                clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                split[0] = clahe.apply(split[0]) 

                self.tgt = cv.merge(split)
                self.tgt = cv.cvtColor(self.tgt, cv.COLOR_YUV2BGR)
            else:
                clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                self.tgt = clahe.apply(self.tgt) 
    
    @QtCore.pyqtSlot()
    def on_btnMoveLeft_clicked(self):
        print('move left')
        idx = self.lstScript.currentRow()
        # ~ self.lstScript.takeItem(idx, 0)
        self.lstScript.removeRow(idx)
        if len(self.scriptList) > 0:
            del self.scriptList[idx]
    
    @QtCore.pyqtSlot()
    def on_btnDelete_clicked(self):
        # ~ print('delete')
        self.on_btnMoveLeft_clicked()
        

    @QtCore.pyqtSlot()
    def on_btnMoveBottom_clicked(self):
        # ~ print('move bottom')
        sidx = self.lstScript.currentRow()
        last = len(self.scriptList) - 1
        if sidx < last :
            self.editingLstScript = True
            item1 = self.lstScript.takeItem(sidx, 0)
            item2 = self.lstScript.takeItem(last, 0)
            print('took item')
            # ~ self.lstScript.insertItem(last, item)
            self.lstScript.setItem(sidx, 0, item2)
            self.lstScript.setItem(last, 0, item1)
            self.editingLstScript = False
            item = self.scriptList.pop(sidx)
            self.scriptList.insert(last, item)
            # ~ self.lstScript.setCurrentRow(last)        
            self.lstScript.setCurrentCell(last, 0)

    
    @QtCore.pyqtSlot()
    def on_btnMoveDown_clicked(self):
        # ~ print('move down')
        sidx = self.lstScript.currentRow()
        
        if sidx < len(self.scriptList) -1 :
            self.editingLstScript = True
            item1 = self.lstScript.takeItem(sidx,   0)
            item2 = self.lstScript.takeItem(sidx+1, 0)
            print('took item')
            self.lstScript.setItem(sidx,   0, item2)
            self.lstScript.setItem(sidx+1, 0, item1)
            self.editingLstScript = False
            item = self.scriptList.pop(sidx)
            self.scriptList.insert(sidx+1, item)
            
            self.lstScript.setCurrentCell(sidx+1, 0)
            # ~ self.lstScript.setCurrentRow(sidx-1)
    
    
    @QtCore.pyqtSlot()
    def on_btnMoveRight_clicked(self):
        # ~ print('move right')
        
        self.editingLstScript = True
        
        idx = self.lstCommands.currentRow()
        sidx = self.lstScript.currentRow()
        last = self.lstScript.rowCount() - 1
        print('sidx ', sidx)
        
        #need to increase row count, right?
        self.lstScript.setRowCount(self.lstScript.rowCount() + 1)
        # ~ print('sidx ', sidx, '(self.lstScript.rowCount()-4) ', (self.lstScript.rowCount()-4))
        # ~ print('sidx < (self.lstScript.rowCount()-4) ', sidx < (self.lstScript.rowCount()-4))
        # ~ print('sidx ', sidx, ' last ', last)
        if sidx < last:
            # we're not at the bottom. need to move other stuff down
            # ~ print('not at bottom')
            for i in range(last, sidx, -1):
                item = self.lstScript.takeItem(i, 0)
                self.lstScript.setItem(i+1, 0, item)
                
        
        # ~ self.lstScript.insertItem(sidx+1, self.pluginNames[idx])
        # ~ self.lstScript.insertItem(sidx+1,format(sidx+2))
        self.lstScript.setItem(sidx+1, 0, QTableWidgetItem(self.pluginNames[idx]))
        # ~ self.lstScript.setItem(sidx+1, 1, QTableWidgetItem(format(sidx+2)))
        
        self.editingLstScript = False
        
        widget = self.pluginObjects[idx].getInstance()
        if widget.needsGraphicsView:
            widget.graphicsView = self.graphicsView
        widget.inputRow = sidx + 2
        # append the pluginObject and its widget
        # ~ self.scriptList.append((self.pluginObjects[idx],widget))
        self.scriptList.insert(sidx+1, (self.pluginObjects[idx],widget))
        
        #now set CurrentRow for  lstScript
        # ~ sidx = len(self.scriptList) - 1
        # ~ print(sidx)
        # ~ self.lstScript.setCurrentRow(sidx+1)
        self.lstScript.setCurrentCell(sidx+1,0)
        

    @QtCore.pyqtSlot()
    def on_btnMoveTop_clicked(self):
        print('move up')
        sidx = self.lstScript.currentRow()
        
        if sidx > 0:
            self.editingLstScript = True
            item1 = self.lstScript.takeItem(sidx, 0)
            item2 = self.lstScript.takeItem(   0, 0)
            print('took item')
            # ~ self.lstScript.insertItem(0, item)
            self.lstScript.setItem(   0, 0, item1) 
            self.lstScript.setItem(sidx, 0, item2) 
            self.editingLstScript = False
            item = self.scriptList.pop(sidx)
            self.scriptList.insert(0, item)
            # ~ self.lstScript.setCurrentRow(0)
            self.lstScript.setCurrentCell(0, 0)
        
    
    @QtCore.pyqtSlot()
    def on_btnMoveUp_clicked(self):
        print('move up')
        sidx = self.lstScript.currentRow()
        
        if sidx > 0:
            self.editingLstScript = True
            item1 = self.lstScript.takeItem(sidx,   0)
            item2 = self.lstScript.takeItem(sidx-1, 0)
            print('took item')
            self.lstScript.setItem(sidx,   0, item2)
            self.lstScript.setItem(sidx-1, 0, item1)
            # ~ self.lstScript.insertItem(sidx-1, item)
            self.editingLstScript = False
            item = self.scriptList.pop(sidx)
            self.scriptList.insert(sidx-1, item)
            
            self.lstScript.setCurrentCell(sidx-1, 0)
            
            # ~ self.lstScript.setCurrentRow(sidx-1)
            
    @QtCore.pyqtSlot(int)
    def on_lstCommands_currentRowChanged(self, row):
        # ~ print('current row is ', row)
        self.statusbar.showMessage(self.pluginObjects[row].statusbar_message)

    
    @QtCore.pyqtSlot(int, int, int, int)
    def on_lstScript_currentCellChanged(self, row, column, previousRow, previousColumn):
    # ~ def on_lstScript_currentRowChanged(self, row):
        
        
        if self.editingLstScript == False:
            # ~ print('lstScript_currentRowChanged  ', row)
            widget = self.scriptList[row][1]
            pluginObject = self.scriptList[row][0]
            self.statusbar.showMessage(pluginObject.statusbar_message)
        
            self.grpParameters.layout().removeWidget(self.lastWidget)

            self.lastWidget.setParent(None)
            # ~ app.processEvents()
            self.grpParameters.layout().addWidget(widget)
            self.lastWidget = widget
            
                    
            # ~ if (self.playing == False) and (widget.needsEventFilter):
            if (widget.needsEventFilter):
                # register events with the pluginObject
                # ~ print('installing eventFilter')
                self.EventFilterWidget = widget
                app.installEventFilter(widget)
            else:
                # need to remove eventFilter somehow
                if self.EventFilterWidget is not None:
                    app.removeEventFilter(self.EventFilterWidget)
                    # ~ print('removed eventFilter')
                    self.EventFilterWidget = None
            self.spinSource.setMaximum(row)
            self.spinSource.setValue(widget.inputRow)
            # ~ print('self.spinSource.maximum() ', self.spinSource.maximum())
            # ~ print('widget.inputRow ', widget.inputRow)
            
            app.processEvents()
            
            self.resizeEvent() #need resize event every time widget is switch
                               # otherwise it can get pretty sticky. maybe we
                               # could resize all widgets inside scriptList?
        
        
    @QtCore.pyqtSlot()
    def on_btnBrowseFile_clicked(self):
        idx = self.lstScript.currentRow()
        pluginObject = self.scriptList[idx][0]
        fname, _filter = QFileDialog.getOpenFileName(self, 'Select Image File', 
                        QDir.currentPath(), pluginObject.fileFilter)
        print(fname)
        self.txtFile.setText(fname)  # on cancel fname is empty string so no need to wrap it in if statement
    
       
    @QtCore.pyqtSlot(bool)
    def on_btnPlay_clicked(self, checked):
        
        if checked:
            self.playing = True
            # ~ self.editingLstScript = False
            
            # first some housekeeping. if we have a specify_target widget active
            # it could still be hogging the EventFilter. 
            if self.EventFilterWidget is not None:
                app.removeEventFilter(self.EventFilterWidget)
                self.EventFilterWidget = None
                
            self.playLoop()
        else:
            self.playing = False
            self.editingLstScript = False
            
    @QtCore.pyqtSlot(int)
    def on_spinSource_valueChanged(self, value):
        row = self.lstScript.currentRow()
        widget = self.scriptList[row][1]
        widget.inputRow = value

        print('widget.objectName() ', widget.objectName())
        print('value ', value)
    
    def playLoop(self):
            
        while self.playing:
            self.playOne()
        
        # do playOne once more to shut off image acquisition
        self.playOne()
            
    def playOne(self):
        ''' 
        go through the script one iteration, stopping at the
        currently selected row
        '''
        
        startTime = time.time()
        for row in range(self.lstScript.currentRow() + 1):
            widget = self.scriptList[row][1]
            pluginObject = self.scriptList[row][0]
            
            if row > 0:
                # we expect load_image to be first operation in script
                # for that, we don't want to preload inputImg
                                
                # ~ widget.inputImg = self.img
                
                inrow = widget.inputRow
                # ~ print('inrow ', inrow)
                widget.inputImg = self.scriptList[inrow-1][1].outputImg
            
            lastrow = row == self.lstScript.currentRow()
            
            if lastrow:
                self.graphicsView.scene().clear()
            
            # ~ if lastrow and widget.objectName() == 'show_graphics_items':
                # show first and mainFunc later
                # ~ self.graphicsView.scene().clear()
                # ~ self.showImg(widget.inputImg)
                
            widget.mainFunc(self.playing, self.scriptList, row)
            
            # ~ self.img = widget.outputImg
            
            # ~ if lastrow and not widget.needsGraphicsView:
            # ~ if lastrow and widget.objectName() != 'show_graphics_items':
            if lastrow:
                # only display last operation in script
                # ~ if widget.objectName() != 'imgLoader':
                self.showImg(widget.outputImg)
                # ~ print('tried to show image')
        
        
        deltaTime = time.time() - startTime
        # as a first approximation, assume fps = 1/deltaTime
        if deltaTime > 0:
            fstring = 'fps %.2f' % (1/deltaTime)
            self.statusbar.showMessage(fstring)
            
        if self.imageItem is not None:
            try:
                self.graphicsView.fitInView(self.imageItem.boundingRect(), Qt.KeepAspectRatio)
            except RuntimeError as e:
                print('RuntimeError in playOne')
                print(e)
        app.processEvents()
        
            
    def startStopThread(self, start = False):
        global running
        global capture_thread
        
        if start:
            self.on_chckEqualize_stateChanged(self.chkEqualize.checkState())
            
            #~ self.binarize(self.tgt)
            #~ self.tgt = cv.cvtColor(self.tgt, cv.COLOR_BGR2RGB)
            self.patchSize = np.loadtxt('patchSize', dtype = np.int32)[0]
            running = True
            capture_thread = threading.Thread(target=grab, args = (0, q, 1920, 1080, 30))
            capture_thread.start()
            print('started thread')
        else:
            running = False    
            
    def showImg(self, img):
        if img is not None:
            # ~ print(img.ndim)
            # ~ print(img.shape)
            if len(img.shape) == 3:
                # ~ img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                height, width, bpc = img.shape
                bpl = bpc * width
                image = QImage(img.data, width, height, bpl, QImage.Format_RGB888)
            else:
                height, width = img.shape
                bpc = 1
                bpl = bpc*width
                image = QImage(img.data, width, height, bpl, QImage.Format_Grayscale8)
            
            try:
                self.graphicsView.scene().removeItem(self.imageItem)
            except RuntimeError:
                pass
            # ~ try:
                # ~ self.graphicsView.scene().removeItem(self.imageItem)
            # ~ except Exception e:
                # ~ print(e)
            
            self.imageItem = QGraphicsPixmapItem(QPixmap.fromImage(image))
            self.imageItem.setZValue(0)
            
            
            # ~ self.graphicsView.scene().clear()
                
            self.graphicsView.scene().addItem(self.imageItem)
    
    def update_frame(self):
        # ~ print('update frame ', time.time())
        #~ if not q.empty():
        if frame is not None:
            # ~ print('not q.empty() ', time.time())
            # ~ self.startButton.setText('Camera is live')
            #~ frame = q.get()
            #~ frame = frame.copy()
            # ~ img = frame["img"]
            img = frame.copy()
            

            # ~ img_height, img_width, img_colors = img.shape
            # ~ scale_w = float(self.window_width) / float(img_width)
            # ~ scale_h = float(self.window_height) / float(img_height)
            # ~ scale_w = float(self.graphicsView.width()) / float(img_width)
            # ~ scale_h = float(self.graphicsView.height()) / float(img_height)
            # ~ scale = min([scale_w, scale_h])

            # ~ if scale == 0:
                # ~ scale = 1
            if img is not None:
                startTime = time.time()
                
                if self.chkEqualize.isChecked():
                    # ~ clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                    # ~ img = clahe.apply(img)
                    if len(img.shape) == 3:  # assume BGR color image
                        img = cv.cvtColor(img, cv.COLOR_BGR2YUV)
                        split = cv.split(img)

                        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                        split[0] = clahe.apply(split[0]) 

                        img = cv.merge(split)
                        img = cv.cvtColor(img, cv.COLOR_YUV2BGR)
                    else:
                        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                        img = clahe.apply(img) 
                    
                self.img = img
                
                # ~ self.findMatch()
                # ~ self.findCircles()
                max_val = self.findTemplate()
                
                
                self.img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                
                if len(self.img.shape) == 3:
                    height, width, bpc = self.img.shape
                    bpl = bpc * width
                    image = QImage(self.img.data, width, height, bpl, QImage.Format_RGB888)
                else:
                    height, width = self.img.shape
                    image = QImage(self.img.data, width, height, QImage.Format_Grayscale8)
                # ~ self.ImgWidget.setImage(image)
                
                self.imageItem = QGraphicsPixmapItem(QPixmap.fromImage(image))
                self.graphicsView.scene().clear()
                self.graphicsView.scene().addItem(self.imageItem)
                
                deltaTime = time.time() - startTime
                # as a first approximation, assume fps = 1/deltaTime
                self.statusbar.showMessage('fps %.2f.  score %.4e' % (1/deltaTime, max_val))
                
                # ~ self.graphicsView.setImage(image)

    def preferences_(self):
        import os
        #~ from PyQt4 import QtGui
        #~ from PyQt5 import QtWidgets
        import configobj
        import configobj_gui_5
        import validate
        
        #~ datadir = os.path.dirname(__file__)
        inidir = os.path.expanduser('~') # cross platform way to get user directory
        inidir = os.path.join(inidir, '.tsim')  # ini files are in .tsim directory
        # ~ specfile = os.path.join(inidir,'senssetngs.spec')
        # ~ conffile = os.path.join(inidir,'senssetngs.ini')
        specfile = 'inspector2.spec'
        conffile = 'inspector2.ini'

        spec = configobj.ConfigObj(specfile, list_values=False)
        config = configobj.ConfigObj(conffile, configspec=spec)

        validator = validate.Validator()

        self.wnd = configobj_gui_5.ConfigWindow(config, spec, when_apply=configobj_gui_5.ConfigWindow.APPLY_OK, 
                                           type_mapping={'mytype':(configobj_gui_5.create_widget_string, validate.is_integer)},
                                           fontsize = 14.)
        #~ self.wnd.setModal(True)
        #~ self.wnd.windowModality = Qt.ApplicationModal
        self.wnd.show()
    
    def print_(self):

        dialog = QPrintPreviewDialog()
        # ~ printer = dialog.printer(QPrinter.HighResolution)
        printer = dialog.printer()
        print(printer.supportedResolutions())
        printer.setResolution(600)
        printer.setOrientation(QPrinter.Landscape)
        printer.setPageMargins( 0.75, 0.75, 0.75, 0.75, QPrinter.Inch )
        # ~ dialog.printer().setFullPage(True)
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()

    def handlePaintRequest(self, printer):
        pwidth_inch = 11.-2.*.75 # assume 11 in wide page and 0.75 inch margins
        pheight_inch = 8.5-2.*.75
        
        screenshot = self.grab()
        res = printer.resolution()
        print(res)
        ar = screenshot.width()/screenshot.height()
        ar_page = pwidth_inch/pheight_inch
        if ar < ar_page:
            screenshot = screenshot.scaledToHeight( pheight_inch*res, Qt.SmoothTransformation )
        else:
            screenshot = screenshot.scaledToWidth( pwidth_inch*res, Qt.SmoothTransformation )
            
        painter = QtGui.QPainter()
        painter.begin(printer)
        painter.drawPixmap(0,0, screenshot)
        painter.end()
        # ~ screenshot.render(QtGui.QPainter(printer))
        # ~ self.render(QtGui.QPainter(printer))
    
    def saveScreen(self):

        import datetime
        
        dname = 'cvr_' + '{:%y%m%d-%H%M%S}'.format(datetime.datetime.now()) + '.png'
        fname, _ = QFileDialog.getSaveFileName(self, 
                          'Specify File Name for Screenshot', dname, 
                          'Portable Network Graphics (*.png)')
        if fname:
            screenshot = self.grab()
            screenshot.save(fname)
            self.statusbar.showMessage('file %s saved.' % fname)
    
    def saveScript(self, bool_var, fname = None):
        # ~ print('saveScript fname is ', fname)
        if fname is None:
            fname, _ = QFileDialog.getSaveFileName(self, 
                          'Specify File Name for Script', '', 
                          'Script File (*.scr)')
        if fname:
            config = configparser.ConfigParser()
            config.optionxform = str
            # ~ print('there are %d items in scriptList' % len(self.scriptList))
            for idx, item in enumerate(self.scriptList):
                widget = item[1]
                # ~ print(widget.getParams())
                config[str(idx)] = widget.getParams()
            f = open(fname, 'w')
            config.write(f)
            f.close()

    def openScript(self, bool_var, fname = None):
        if fname is None:
            fname, _ = QFileDialog.getOpenFileName(self, 
                                QDir.currentPath(),
                                "Open Script", 'Script File (*.scr)')
        if fname:
            config = configparser.ConfigParser()
            config.optionxform = str
            config.read(fname)
            
            self.lstScript.clear()
            self.scriptList = [] # clear the list of widgets, etc.
                                 # presumably all of the objects get
                                 # garbage collected
            self.lstScript.setRowCount( len(config.sections()) )
            
            for section in config.sections():
                # ~ print('section ', section)
                plugin_name = config[section]['plugin_name']
                idx = self.pluginNames.index(plugin_name)
                
                sidx = self.lstScript.currentRow()
                self.editingLstScript = True

                self.lstScript.setItem(sidx+1, 0, QTableWidgetItem(self.pluginNames[idx]))
                
                widget = self.pluginObjects[idx].getInstance()
                if widget.needsGraphicsView:
                    widget.graphicsView = self.graphicsView
                # append the pluginObject and its widget
                # ~ self.scriptList.append((self.pluginObjects[idx],widget))
                self.scriptList.insert(sidx+1, (self.pluginObjects[idx],widget))
                                
                # now try to set all of the widgets
                widget.setParams(dict(config[section].items()))

                  
                self.lstScript.setCurrentCell(sidx+1,0)
                self.spinSource.setValue(widget.inputRow)
            self.editingLstScript = False
            #on_lstScript_currentCellChanged(self, row, column, previousRow, previousColumn)
            self.on_lstScript_currentCellChanged(len(config.sections())-1, 0, 0, 0)
                

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.graphicsView.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def about(self):
        QMessageBox.about(self, "About Image Viewer",
                "<p>The <b>Image Viewer</b> example shows how to combine "
                "QLabel and QScrollArea to display an image. QLabel is "
                "typically used for displaying text, but it can also display "
                "an image. QScrollArea provides a scrolling view around "
                "another widget. If the child widget exceeds the size of the "
                "frame, QScrollArea automatically provides scroll bars.</p>"
                "<p>The example demonstrates how QLabel's ability to scale "
                "its contents (QLabel.scaledContents), and QScrollArea's "
                "ability to automatically resize its contents "
                "(QScrollArea.widgetResizable), can be used to implement "
                "zooming and scaling features.</p>"
                "<p>In addition the example shows how to use QPainter to "
                "print an image.</p>")

    def createActions(self):
        self.openAct = QAction("&Open Script...", self, shortcut="Ctrl+O",
                enabled=True, triggered=self.openScript)

        self.printAct = QAction("&Print...", self, shortcut="Ctrl+P",
                enabled=True, triggered=self.print_)
        
        self.saveScriptAct = QAction("&Save Script...", self, shortcut="Ctrl+S",
                enabled=True, triggered=self.saveScript)
                
        self.saveScreenAct = QAction("&Save Screenshot...", self,
                enabled=True, triggered=self.saveScreen)
                
        self.preferencesAct = QAction("&Preferences...", self,
                enabled=True, triggered=self.preferences_)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++",
                enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-",
                enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QAction("&Normal Size", self, 
                enabled=True, triggered=self.showNormal)#self.normalSize)
                
        self.fullScreenAct = QAction("F&ull Screen", self, 
                enabled=True, triggered=self.showFullScreen)

        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False,
                checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)

        self.aboutAct = QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addAction(self.saveScriptAct)
        self.fileMenu.addAction(self.saveScreenAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        
        self.editMenu = QMenu("&Edit", self)
        self.editMenu.addAction(self.preferencesAct)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addAction(self.fullScreenAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.editMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        #~ self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
        #~ self.normalSizeAct.setEnabled(True)
        #~ self.fullScreenAct.setEnabled(True)
        
    def resizeEvent(self, event = 0):
        #~ print('resize')
        # ~ sfh = float(self.centralWidget().height())/float(self.centralWidget().minimumHeight())
        # ~ sfw = float(self.centralWidget().width())/float(self.centralWidget().minimumWidth())
        # ~ sf = min(sfh,sfw)
        
        fs = 8   # font size
        isize = 16.0   # indicator size for checkboxes, radioboxes and spinboxes
        
        
        
        #~ print('resize')
        sfh = float(self.centralWidget().height())/float(self.centralWidget().minimumHeight())
        sfw = float(self.centralWidget().width())/float(self.centralWidget().minimumWidth())
        sf = min(sfh,sfw)
        # ~ print('sf is %f' % sf)
 
 
        font = QFont("DejaVu Sans", fs)  # this font comes with Linux and is installed
                                          # on Windows with LibreOffice
        font.setPointSizeF(sf*fs)
        
        # this next bit may not work so well for more complicated
        # forms where there is a fancy style sheet controlling colors, fonts,
        # border widths, etc. since it will clobber the existing style sheet.
        self.setStyleSheet('QToolTip { font-size: %fpt;}' % fs)
        
        for widget in self.findChildren((QtWidgets.QLineEdit, 
            QtWidgets.QComboBox, QtWidgets.QGroupBox, QtWidgets.QPushButton, 
            QtWidgets.QTableView, QtWidgets.QLabel, QtWidgets.QStatusBar,
            QtWidgets.QCheckBox, QtWidgets.QRadioButton, QtWidgets.QListWidget,
            QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox, QtWidgets.QMenu, 
            QtWidgets.QMenuBar, QtWidgets.QToolTip  )):
            #~ print(widget.objectName())
            widget.setFont(font)
            # ~ if 'View' in widget.objectName():
                # ~ widget.verticalHeader().setDefaultSectionSize(25.*sf)
        
        for widget in self.findChildren((QtWidgets.QPushButton,)):
            if widget.icon() is not None:
                ind = int(sf*isize)
                widget.setIconSize(QSize(ind, ind))
                widget.setMinimumSize(QSize(ind, ind))
        
        for widget in self.findChildren((QtWidgets.QCheckBox)):
            #~ print(widget.objectName())
            ind = str(sf*isize) # 
            style = 'QCheckBox::indicator {\n     width: ' + ind + 'px;\n     height: ' + ind + 'px;\n}'
            widget.setStyleSheet(style)
        
        for widget in self.findChildren((QtWidgets.QRadioButton)):
            #~ print(widget.objectName())
            ind = str(sf*isize) # 
            style = 'QRadioButton::indicator {\n     width: ' + ind + 'px;\n     height: ' + ind + 'px;\n}'
            widget.setStyleSheet(style)
            
        for widget in self.findChildren((QtWidgets.QSlider)):
            #~ print(widget.objectName())
            ind = str(sf*isize) # 16 is default size
            style = 'QSlider::indicator {\n     width: ' + ind + 'px;\n     height: ' + ind + 'px;\n}'
            widget.setStyleSheet(style)
            
        for widget in self.findChildren((QtWidgets.QDoubleSpinBox)):
            #~ print(widget.objectName())
            ind = str(sf*isize) # 
            style  = 'QDoubleSpinBox::up-button, QDoubleSpinBox::down-button\n {\n     min-width: ' + ind + 'px;\n     min-height: ' + ind + 'px;\n}'
            # ~ style += 'QDoubleSpinBox::down-button {\n     width: ' + ind + 'px;\n     height: ' + ind + 'px;\n}'
            widget.setStyleSheet(style)
            widget.setMinimumHeight(40.*sf) 
            
        for widget in self.findChildren((QtWidgets.QSpinBox)):
            # ~ print(widget.objectName())
            ind = str(sf*isize*1.4) # 
            if widget.objectName() == 'spinSource':
                ind = str(24.*sf) # 
                style = '''
                QSpinBox::up-button,QSpinBox::down-button{
                     min-width: indpx;
                     min-height:indpx;
                }
                QSpinBox::down-button{
                    subcontrol-origin: border;
                    subcontrol-position: top left;
                }
                QSpinBox::up-button{
                    subcontrol-origin: border;
                    subcontrol-position:top right;
                }
                '''
                style = style.replace('ind', ind)
                # ~ print('spinSource style: ', style)
                widget.setMinimumHeight(24.*sf)
            else:
                style  = 'QSpinBox::up-button, QSpinBox::down-button\n {\n     min-width: ' + ind + 'px;\n     min-height: ' + ind + 'px;\n}'
                # ~ style += 'QDoubleSpinBox::down-button {\n     width: ' + ind + 'px;\n     height: ' + ind + 'px;\n}'
                widget.setMinimumHeight(40.*sf)
            # ~ print(style)
            widget.setStyleSheet(style)

        
        
        
        
        
        #~ self.graphicsView.fitInView(self.graphicsView.scene().sceneRect(), Qt.KeepAspectRatio)
        if self.imageItem is not None:
            try:
                self.graphicsView.fitInView(self.imageItem.boundingRect(), Qt.KeepAspectRatio)
            except RuntimeError as e:
                print('RuntimeError in resizeEvent')
                print(e)
                
            # ~ print('image bounding rect', self.imageItem.boundingRect())
            # ~ print('scene bounding rect', self.graphicsView.scene().sceneRect())
            # ~ print('viewport margin ', self.graphicsView.viewport().viewportMargins())
            # ~ print('viewport rect ', self.graphicsView.viewport().rect())
            
        app.processEvents()
        # ~ print('resize ', time.time())
        
        

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.graphicsView.resize(self.scaleFactor * self.graphicsView.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))


# ~ if __name__ == '__main__':

capture_thread = None


app = QApplication(sys.argv)
robot = Robot(None)

app_icon = QtGui.QIcon()
app_icon.addFile('eye16.png', QtCore.QSize(16,16))
app_icon.addFile('eye24.png', QtCore.QSize(24,24))
app_icon.addFile('eye32.png', QtCore.QSize(32,32))
app_icon.addFile('eye48.png', QtCore.QSize(48,48))
app_icon.addFile('eye64.png', QtCore.QSize(64,64))
app_icon.addFile('eye128.png', QtCore.QSize(128,128))
app_icon.addFile('eye256.png', QtCore.QSize(256,256))


robot.setWindowIcon(app_icon)

import platform
if platform.system()=='Windows':
    import ctypes
    myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)




robot.show()
# ~ inspector.showFullScreen()
# ~ app.installEventFilter(robot)
sys.exit(app.exec_())
# ~ app.exec_()

# ~ app = QtWidgets.QApplication(sys.argv)
# ~ w = MyWindowClass(None)
# ~ w.setWindowTitle('Kurokesu PyQT OpenCV USB camera test panel')
# ~ w.show()
# ~ app.exec_()

