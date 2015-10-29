# -*- coding: utf-8 -*-
"""
Created on Sat Dec 20 17:48:12 2014

@author: derChris
"""

import sys
import codecs
from pydispatch import dispatcher
 
from PyQt5 import QtWidgets, QtGui, QtCore,  QtSvg

from undostack import UndoStack
from parserbridge import Bridge
#from matplotlib.backends.qt_compat import QtWidgets

app = QtWidgets.QApplication(sys.argv)

    
       
class Edith(QtWidgets.QTextEdit, QtWidgets.QFrame):
    def __init__(self, parent):
        super(Edith, self).__init__()
        
        self.parent = parent
        self._defaul_font_size = 12
        self._zoom = 1
        
        self.undostack = UndoStack()
        
        #self.setStyleSheet('font-family: \'Calibri\'; background-color: #FFFFFF')
        self.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)

        self._test_str = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghim'
        self.setStyleSheet('font-size: %.3fpt;font-family: \'Calibri\'; background-color: #FFFFFF' % (self._zoom * 12))
            
        metric = QtGui.QFontMetrics(QtGui.QFont('Calibri', 12))
        self._text_width = metric.boundingRect(self._test_str).width()
        self.setFixedWidth(1.1 * self._text_width)
            
        self.document().setDocumentMargin(0.05 * self._text_width)
        
        super().setFixedHeight(self._text_width/2)
        
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        
        self.bridge = Bridge()
        
        # setup frame
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setLineWidth(1)
        
        # eventlistening
        self.document().contentsChange.connect(self.update_parser)
        self.cursorPositionChanged.connect(self.cursor_position_changed)
        
    @QtCore.pyqtSlot()
    def cursor_position_changed(self):
        self.undostack.push(self.toPlainText())
        
        
    @QtCore.pyqtSlot(int,int,int)
    def update_parser(self, position, chars_removed, chars_added):
        
        new_text = self.toPlainText()[position:position+chars_added]
        
        decorated = self.bridge.document_changed(position,  new_text,  chars_removed)
        decorated = '<span style="white-space: pre-wrap;">' + decorated + '</span>'
        
        self.document().blockSignals(True)
        self.document().setHtml(decorated)
        self.document().blockSignals(False)
        
        self.setFixedHeight(self.document().size().height())
    
    def setFixedHeight(self, height):
        #print(self.cursorRect())
        super().setFixedHeight(max([height, self._text_width/2]))
            
    @QtCore.pyqtSlot()
    def openDialog(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(scrollArea,
                                             caption= 'Open File',
                                             filter='Edith\'s Files (*.efi)')
        
        if filename != ('',''):
            with codecs.open(filename, 'r', 'utf-8') as file:
                
                text = ''.join(file.readlines())
                
                self.setPlainText(text)
                file.close()
                self.setFocus()
        
    @QtCore.pyqtSlot()
    def clearEdith(self):
        
        self.clear()
        
        
    def wheelEvent(self, event):
        
        if event.modifiers() & QtCore.Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                 
                
                if self._defaul_font_size * self._zoom < 30:
                    self._zoom += 0.1
                    
            else:
                 
                if self._defaul_font_size * self._zoom > 5:
                    self._zoom -= 0.1
            
            self.setStyleSheet('font-size: %.3fpt;font-family: \'Calibri\'; background-color: #FFFFFF' % (self._zoom * 12))
            metric = QtGui.QFontMetrics(self.font())
            self._text_width = metric.boundingRect(self._test_str).width()
            self.setFixedWidth(1.1 * self._text_width)
                
            self.document().setDocumentMargin(0.05 * self._text_width)
            
        else:
            super(Edith, self).wheelEvent(event)
        
class EdithsMenuButton(QtWidgets.QPushButton):
    def __init__(self, file):
        super(EdithsMenuButton, self).__init__()
        
        self.setFlat(True)
        self.__icon = QtSvg.QSvgWidget('./pix/' + file + '.svg', self)
        
        self.setFixedSize(50,50)
        
        
        
    def enterEvent(self, event):
        dropshadow = QtWidgets.QGraphicsDropShadowEffect()
        dropshadow.setOffset(2,1)
        
        self.__icon.setGraphicsEffect(dropshadow)
        
    def leaveEvent(self, event):
        self.__icon.setGraphicsEffect(None)
        
    def paintEvent(self, event):
        None
        
        

            
            
            
###################
### constants
###################






###################
### scroll area
###################

main = QtWidgets.QMainWindow()
main.setGeometry(100,100, 1000, 600)

scrollArea = QtWidgets.QScrollArea()
scrollArea.setWidgetResizable(True)
scrollArea.viewport().setStyleSheet('background-color:#545454;') #F3F5EB
main.setCentralWidget(scrollArea)
main.setWindowTitle('laTextile')
### main window


### window
# no widget, no scroll!
window = QtWidgets.QWidget()

scrollArea.setWidget(window)

####################
### text edit
####################
# edith
edith = Edith(window)
shadow = QtWidgets.QGraphicsDropShadowEffect()
shadow.setBlurRadius(5)
shadow.setOffset(6,6)
shadow.setColor(QtGui.QColor('#505050'))
edith.setGraphicsEffect(shadow)

#######################
### Window
#######################
# build box layout
wLayout = QtWidgets.QHBoxLayout()
# wLayout.addWidget(lWidget)
wLayout.addSpacing(20)
wLayout.addStretch(1)
wLayout.addWidget(edith)
wLayout.addStretch(1)
wLayout.addSpacing(20)

wLayout.setAlignment(edith, QtCore.Qt.AlignTop)
wLayout.setContentsMargins(0, 20, 0, 20)

window.setLayout(wLayout)

#########################
### menubar
#########################

class MenuBar(QtWidgets.QMenuBar):
    def __init__(self):
        
        super(MenuBar, self).__init__()
        
        ### FILE
        file = self.addMenu('File')
        file.addAction('New').triggered.connect(edith.clearEdith)
        file.addAction('Open File..').triggered.connect(edith.openDialog)
        file.addSeparator()
        file.addAction('Exit').triggered.connect(app.quit)
        
        ### EDIT
        edit = self.addMenu('Edit')
        
        self.edit_undo = edit.addAction('Undo')
        self.edit_undo.setEnabled(False)
        dispatcher.connect(self.set_edit_undo_enable, signal=UndoStack.UNDO_POSSIBLE)

        self.edit_redo = edit.addAction('Redo')
        self.edit_redo.setEnabled(False)
        dispatcher.connect(self.set_edit_redo_enable, signal=UndoStack.REDO_POSSIBLE)

    def set_edit_undo_enable(self, sender, value):
        
        self.edit_undo.setEnabled(value)

    def set_edit_redo_enable(self, sender, value):
        
        self.edit_redo.setEnabled(value)


main.setMenuBar(MenuBar())

# scroll area start
main.show()
edith.setFocus(QtCore.Qt.ActiveWindowFocusReason)

sys.exit(app.exec_())

