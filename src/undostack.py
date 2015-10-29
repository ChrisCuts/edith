# -*- coding: utf-8 -*-
'''
Created on 02.08.2015

@author: derChris
'''

from pydispatch import dispatcher 


class UndoStack(object):
    
    UNDO_POSSIBLE = 'UNDO_POSSIBLE'
    REDO_POSSIBLE = 'REDO_POSSIBLE'
    
    def __init__(self, depth = 50):
        
        self._depth = 50
        
        self._stack = []
        self._redo = []
        
    def push(self, item):
        
        if len(self._stack) < self._depth:
            
            self._stack.append(item)
            
        else:
            self._stack[1:].append(item)
        
        self._redo.clear()
                
        dispatcher.send(self.UNDO_POSSIBLE, self, value=True)
        dispatcher.send(self.REDO_POSSIBLE, self, value=False)
        
    def pop(self):
        
        if len(self._stack) == 1:
            dispatcher.send(self.UNDO_POSSIBLE, self, value=False)
        
        if not self._stack:
            return []
        
        self._redo.append(self._stack.pop())
        dispatcher.send(self.REDO_POSSIBLE, self, value=True)
        
        return self._redo[-1]  
    
    def is_undo_possible(self):
        
        return len(self._stack) > 0
    
    