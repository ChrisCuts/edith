# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 15:32:25 2015

@author: derChris
"""


###############
### CLASSES
###############

    
### block class:
#
# top level keys:
# - configuration.
# - document.
#
# keys:
# - section.
# - ...

import re


##############
## INIT
##############

keys = [
    r'\*',
    r'[A-Za-z][A-Za-z1-9]*\.\s'
    ]

keys_joined = re.compile('|'.join(keys))

class Transpiler:
    def __init__(self, header = '', footer = ''):
        
        self.header = header
        self.footer = footer
        
class Modifier:
    def __init__(self, header, footer, EOB_regex, EOB_inclusion=False):
        self.header = header
        self.footer = footer
        # EOB: end of block
        self.EOB_regex = EOB_regex
        self.EOB_inclusion = EOB_inclusion
        
        self.transpiler = {}
        
    def add_transpiler(self, language, transpiler):
        self.transpiler.update({language : transpiler})
        
modifier = {
    '*': Modifier('*', '*', '\*', EOB_inclusion=True),
    'section. ': Modifier('section. ', '\n', '\n')
}

modifier['*'].add_transpiler('deco', Transpiler('<b>', '</b>'))
modifier['section. '].add_transpiler('deco', Transpiler('<span style="font-size:x-large; font-weight:600;">', '</span>'))

EOBs = []
for mod in modifier.values():
    EOBs.append(mod.EOB_regex)
 
EOBs = re.compile('|'.join(EOBs))

class DocumentBlock:
    def __init__(self, position):
        
        self._position = position
        
        self._plain = ''

    def text_changed(self, plain, start, end=0):
        pass
    
    def __len__(self):
        return len(self._plain)
    
    def __contains__(self, position):
        
        return position >= self._position and position <= self._position + len(self)

    def get_plain(self):
        return self._plain
    def get_decorated(self):
        return self._decorated    
    def is_ancestor(self, node):
        
        if 'parent' in dir(self):
            return self.parent == node or self.parent.is_ancestor(node)
        else:
            return False
    def dissolve(self, position, text, length):
        
        text = self._plain[:position] + text + self._plain[position+length:]
        
        self.parent.refresh(self, text)
        
        
class TextBlock(DocumentBlock):
    def __init__(self, text, parent = None, position = None):
        
        super(TextBlock, self).__init__(position)
        
        self.parent = parent
        
        self._plain = text
        
    def add_content(self, position, text, length):
        
        self.dissolve(position, text, length)
        
    def is_footer_in_tree(self, footer):
        
        return self.parent.is_footer_in_tree(footer)

    def append_text(self, text):
        
        self._plain += text
    
    def get_decorated(self):
        
        return self._plain#.replace('\n', '<br>')#.replace('\n',  '<p>')
        
class ParentBlock(DocumentBlock):
    def __init__(self, position = 0, head = ''):
        
        super(ParentBlock, self).__init__(position)
        
        # set header
        self.header = head
        self.footer = ''
        self.modifier = None
        self.children = []
        
        self._decorated = ''
        
        
    def addBlock(self, Block, child_position = None):
        
        if child_position != None and child_position < len(self.children):
            if Block.__class__.__name__ == 'TextBlock' \
            and self.children[child_position].__class__.__name__ == 'TextBlock':
                # insert in existing TextBlock
                Block.append_text(self.children[child_position]._plain)
                self.children[child_position] = Block
                
            else:
                self.children.insert(child_position, Block)
                
            Block._position = 0
            for i in range(child_position):
                Block._position += len(self.children[i])
        else:
            if len(self.children) > 0 \
            and Block.__class__.__name__ == 'TextBlock' \
            and self.children[-1].__class__.__name__ == 'TextBlock':
                # insert in existing TextBlock
                self.children[-1].append_text(Block._plain)
                
            else:
                self.children.append(Block)
                
                Block._position = len(self)
    
        Block.parent = self
        
        self.update_plain()
    
    def add_content(self, position, text, length = 0):
        
        if position < 0:
            # error
            print('error')
        elif position < len(self.header):
            # somewhere in header --> dissolve
            self.dissolve(position, text, length)
        
        elif self.children and position <= self.children[-1]._position + len(self.children[-1]):
            # somewhere in children
            for child in self.children:
                # scoop for changing children
                if position in child:
                    if position + length in child:
                        child.add_content(position - child._position, text, length)
                        break
                    else:
                        self.dissolve(position, text, length)
                        break
                    
        elif position <= len(self):
            # somewhere in footer --> dissolve
            self.dissolve(position, text, length)
            
        elif position == len(self):
            # append at the end
            PARSER.create_tree(text, self)
        else:
            # error
            print('error')
        
    def refresh(self, node, text):
        
        for i in range(len(self.children)):
            if self.children[i] == node:
                del(self.children[i])
                
                PARSER.create_tree(text, self, i)
                return
                

class HeaderBlock(ParentBlock):
    def __init__(self, head, parent = None, position = None):
        
        super(HeaderBlock, self).__init__(position, head)
        
        self.parent = parent
        
            
        self._plain = head
        
    def append(self, Block):
        
        super(HeaderBlock, self).append(Block)
        
        self.parent.update_plain()
    
    def append_footer(self, footer):
        self.footer = footer
        
        self.update_plain()
    
    def dissolve_from(self, children_position):
        
        if children_position == None:
            return ''
            
        text = ''        
        while children_position < len(self.children):
            text += self.children[children_position]._plain
            del(self.children[children_position])
            
        
        return text
            
    
    def update_plain(self):
        
        text = self.header
        decorated = self.modifier.transpiler['deco'].header + self.header
        
        for child in self.children:
            child._position = len(text)
            text += child.get_plain()
            decorated += child.get_decorated()
            
        text += self.footer
        decorated += self.footer + self.modifier.transpiler['deco'].footer#.replace('\n',  '<p>')
        
        self._plain = text
        self._decorated = decorated
        
        self.parent.update_plain()
        
    def is_footer_in_tree(self, footer):
        
        return self.modifier.footer == footer or self.parent.is_footer_in_tree(footer)

### top level block
class Document(ParentBlock):
    def __init__(self, text):
    
        super(Document, self).__init__()
        
        if text:
            self.add_content(0, text)
    
    def update_plain(self):
        
        text = ''
        decorated = ''
        
        for child in self.children:
            child._position = len(text)
            text += child.get_plain()
            decorated += child.get_decorated()
            
        self._plain = text
    
        self._decorated = decorated
        
    def is_footer_in_tree(self, footer):
        
        return False
    
    def dissolve(self, position, text, length):
        
        text = self._plain[:position] + text + self._plain[position+length:]
        
        super(Document, self).__init__()
        PARSER.create_tree(text, self)
        #self.add_content(0, text)
    
#################
### PARSER
#################
class PARSER:
    def __init__(self, owner):
        self.owner = owner
        
        self.modifier_stack = []
        
    @classmethod
    def detect_next_header(cls, text):
        
        match = re.search(keys_joined, text)
        
        if match:    
            
            while match and match.group() not in modifier.keys():
                match = keys_joined.search(text, match.start()+len(match.group()))
                
        return match
            
    @classmethod
    def detect_next_footer(cls, text, node):
        
        match = re.search(EOBs, text)
        
        
        if match and node.is_footer_in_tree(match.group()):
            return match
        else:
            return None
       
    @classmethod     
    def header_priority(cls, header_match, footer_match):
        priority = header_match and not footer_match
            
        if header_match and footer_match:
            priority = header_match.start() < footer_match.start()
        
        return priority
        
    @classmethod
    def create_tree(cls, text, root, child_position = None):
        
        child_relation = root
        
        header_match = PARSER.detect_next_header(text)
        footer_match = PARSER.detect_next_footer(text, root)

        while header_match or footer_match:
            
            
            if PARSER.header_priority(header_match, footer_match):
                ###################
                ### HEADER BLOCK
                ###################
                cursor = header_match.start()
                header = header_match.group()
                
                
                # create new HeaderBlock
                
                # check for remaining text
                if cursor > 0:
                    # create and add TextBlock to actual object
                    if child_relation == root:
                        root.addBlock(TextBlock(text[:cursor]), child_position)
                        if child_position != None:
                            child_position += 1
                    else:
                        root.addBlock(TextBlock(text[:cursor]))
                        
                    # erease text
                    text = text[cursor:]
                    
                
                
                # add HeaderBlock
                newHeaderBlock = HeaderBlock(header)
                
                if child_relation == root:
                    root.addBlock(newHeaderBlock, child_position)
                else:
                    root.addBlock(newHeaderBlock)
                
                root = newHeaderBlock
                root.modifier = modifier[header]
                
                print(text)
                
                text = text[len(header):]
                
            else:
                ###################
                ### FOOTER
                ###################
                
                cursor = footer_match.start()
                footer = footer_match.group()
                
                # check for remaining text
                if cursor > 0:
                    
                    # create and add TextBlock to actual object
                    if child_relation == root:
                        root.addBlock(TextBlock(text[:cursor]), child_position)
                        if child_position != None:
                            child_position += 1
                    else:
                        root.addBlock(TextBlock(text[:cursor]))
                    # erease text
                    text = text[cursor:]
                
                
                # if EOB symbol is in stack, pop until we re there
                while root.is_footer_in_tree(footer) and footer != root.modifier.footer:
                    
                    # dissolve following children
                    if child_relation == root:
                        text += root.dissolve_from(child_position)
                    
                        if child_position != None:
                            for i in range(len(root.parent.children)):
                                if root.parent.children[i] == root:
                                    child_position = i+1
                                    break
                        
                    root = root.parent
                    if not root.is_ancestor(child_relation):
                        child_relation = root
                
                
                if root.is_footer_in_tree(footer) and root.modifier.EOB_inclusion:
                    # add footer
                    root.append_footer(footer)
                    text = text[len(footer):]
                
                text += root.dissolve_from(child_position)
                
                if child_position != None:
                    for i in range(len(root.parent.children)):
                        if root.parent.children[i] == root:
                            child_position = i+1
                            break
                # close actual Block
                
                root = root.parent
                if not root.is_ancestor(child_relation):
                    child_relation = root
                
                
                
            header_match = PARSER.detect_next_header(text)
            footer_match = PARSER.detect_next_footer(text, root)
            
            ### end while header_match or footer_match ###
        
        if text:
            root.addBlock(TextBlock(text), child_position)
        else:
            root.update_plain()


if __name__ == '__main__':
    
    def print_child_info(root, depth = 0, last = False, lines = [], string = ''):
        if root.__class__.__name__ != 'TextBlock':
            if root.__class__.__name__ == 'HeaderBlock':
                for i in range(depth):
                    if i in lines:
                        string += '│   '
                    else:
                        string += '    '
                if last and root.footer == '':
                    string += '└─'
                    if depth in lines:
                        lines.remove(depth)
                else:
                    string += '├─'
                    lines.append(depth)
                
                string += ' HeaderBlock[' + '%i' % root._position + ']: ' + root.header.replace('\n', '\\n') + '\n'
            
            i = 1
            for child in root.children:
                string = print_child_info(child, depth+1, i == len(root.children) and not root.footer, lines, string)
                i += 1
            
            if root.__class__.__name__ == 'HeaderBlock' and root.footer != '':
                for i in range(depth+1):
                    if i in lines:
                        string += '│   '
                    else:
                        string += '    '
                string += '└─ Footer: ' + root.footer + '\n'
                
        else:
            for i in range(depth):
                if i in lines:
                    string += '│   '
                else:
                    string += '    '
            if last:
                string += '└─'
            else:
                string += '├─'
            
            string += u' TextBlock[' + '%i' % root._position + ']: ' + root.get_plain().replace('\n', '\\n') + '\n'
        
        return string

    doc = Document('')

    #x = print_child_info(doc)
    
    doc.add_content(0, 'he*y*')
    doc.add_content(5, 'geht')
    
    x = print_child_info(doc)
    print(x)
    #doc = Document('')
    #doc.add_content(11, 'kn', length=11)
    #doc.add_content(0, 'hey *heya*no')
    print('\n')
    #print(print_child_info(doc))
    print(repr(doc.get_decorated()))
