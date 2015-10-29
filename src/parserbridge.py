# -*- coding: utf-8 -*-
"""
Created on Fri Jan  2 15:24:20 2015

@author: derChris
"""

from PyQt5 import QtCore
from edi_parser import Document
#################
### VARIABLES
#################

        
    
    
######################
### MODULE FUNCTIONS
######################

class Bridge(QtCore.QObject):
    def __init__(self):
        self.__document = Document('')
    
    
    def document_changed(self,  position, text, length):
        self.__document.add_content(position, text, length)
        
        return self.__document.get_decorated()
