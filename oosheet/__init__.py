# -*- coding: utf-8 -*-

import uno, re, sys, os, zipfile
from datetime import datetime, timedelta

# http://codesnippets.services.openoffice.org/Office/Office.MessageBoxWithTheUNOBasedToolkit.snip
from com.sun.star.awt import WindowDescriptor
from com.sun.star.awt.WindowClass import MODALTOP
from com.sun.star.awt.VclWindowPeerAttribute import OK

class OODoc(object):

    @property
    def model(self):
        localContext = uno.getComponentContext()
        if sys.modules.get('pythonscript'):
            # We're inside openoffice macro
            ctx = localContext
        else:
            # We have to connect by socket
            resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext)
            ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
            
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
            
        return desktop.getCurrentComponent()

    @property
    def dispatcher(self):
        localContext = uno.getComponentContext()
        if sys.modules.get('pythonscript'):
            ctx = localContext
        else:
            resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext)
            ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )

        smgr = ctx.ServiceManager
        return smgr.createInstanceWithContext( "com.sun.star.frame.DispatchHelper", ctx)

    def args(self, *args):
        uno_struct = []

        for i, arg in enumerate(args):
            struct = uno.createUnoStruct('com.sun.star.beans.PropertyValue')
            struct.Name = arg[0]
            struct.Value = arg[1]
            uno_struct.append(struct)

        return tuple(uno_struct)

    def dispatch(self, cmd, *args):
        if args:
            args = self.args(*args)

        self.dispatcher.executeDispatch(self.model.getCurrentController(),
                                        cmd, '', 0, args)
        

    def alert(self, msg, title = u'Atenção'):
        parentWin = self.model.CurrentController.Frame.ContainerWindow

        aDescriptor = WindowDescriptor()
	aDescriptor.Type = MODALTOP
	aDescriptor.WindowServiceName = 'messbox'
	aDescriptor.ParentIndex = -1
	aDescriptor.Parent = parentWin
	aDescriptor.WindowAttributes = OK

        tk = parentWin.getToolkit()
        box = tk.createWindow(aDescriptor)

        box.setMessageText(msg)
        
        if title:
            box.setCaptionText(title)

        box.execute()

    
class OOSheet(OODoc):

    def __init__(self, selector = None):
        if not selector:
            return
        
        try:
            sheet_name, cells = selector.split('.')
            self.sheet = self.model.Sheets.getByName(sheet_name)
        except ValueError:
            self.sheet = self.model.Sheets.getByIndex(0)
            cells = selector
        cells.replace('$', '')
        cells = cells.upper()

        if ':' in cells:
            (start, end) = cells.split(':')
            if not re.match('^[A-Z]', end):
                col, row = self._position(start)
                end = ''.join([self._col_name(col), end])
            cells = ':'.join([start, end])
            self.range = cells
            self.cell = None
        else:
            col, row = self._position(cells)
            self.cell = self.sheet.getCellByPosition(col, row)
            self.range = None

        self.cells = cells

    def __repr__(self):
        return self.selector

    @property
    def selector(self):
        return '.'.join([self.sheet.Name, self.cells])
    
    def _position(self, descriptor):
        col = re.findall('^([A-Z]+)', descriptor)[0]
        row = descriptor[len(col):]
            
        col = self._col_index(col)
        row = int(row) - 1

        return col, row

    def _col_index(self, name):
        letters = [ l for l in name ]
        letters.reverse()
        index = 0
        power = 0
        for letter in letters:
            index += (1 + ord(letter) - ord('A')) * pow(ord('Z') - ord('A') + 1, power)
            power += 1
        return index - 1

    def _col_name(self, index):
        name = []
        letters = [ chr(ord('A')+i) for i in range(26) ]
        
        while index > 0:
            i = index % 26
            index = int(index/26) - 1
            name.append(letters[i])

        if index == 0:
            name.append('A')
        return ''.join(name)            

    @property
    def basedate(self):
        return datetime(1899, 12, 30)

    @property
    def value(self):
        assert self.cell is not None
        return self.cell.getValue()

    @value.setter
    def value(self, value):
        assert self.cell is not None
        self.cell.setValue(value)

    @property
    def formula(self):
        assert self.cell is not None
        return self.cell.getFormula()

    @formula.setter
    def formula(self, formula):
        assert self.cell is not None
        if not formula.startswith('='):
            formula = '=%s' % formula
        self.cell.setFormula(formula)

    @property
    def string(self):
        assert self.cell is not None
        return self.cell.getString()

    @string.setter
    def string(self, string):
        assert self.cell is not None
        self.cell.setString(string)

    @property
    def date(self):
        assert self.cell is not None
        return self.basedate + timedelta(self.value)

    @date.setter
    def date(self, date):
        assert self.cell is not None
        delta = date - self.basedate
        self.value = delta.days

    def focus(self):
        self.dispatch('.uno:GoToCell', ('ToPoint', self.selector))

    def drag_to(self, destiny):

        if '.' in destiny:
            sheet_name, destiny = destiny.split('.')
            assert sheet_name == self.sheet.Name
            
        self.focus()
        self.dispatch('.uno:AutoFill', ('EndCell', '%s.%s' % (self.sheet.Name, destiny)))

    def delete_rows(self):
        self.focus()
        self.dispatch('.uno:DeleteRows')

    def delete_columns(self):
        self.focus()
        self.dispatch('.uno:DeleteColumns')

    def insert_row(self):
        self.focus()
        self.dispatch('.uno:InsertRows')

    def insert_column(self):
        self.focus()
        self.dispatch('.uno:InsertColumns')

    def find_last_column(self):
        if ':' not in self.cells:
            cells = self.cells
            end_row = None
        else:
            (start, end) = self.cells.split(':')
            start_col, start_row = self._position(start)
            end_col, end_row = self._position(end)
            assert start_col == end_col
            cells = start

        col, row = self._position(cells)
        while True:
            col += 1
            cell = self.sheet.getCellByPosition(col, row)
            if cell.getValue() == 0 and cell.getString() == '' and cell.getFormula() == '':
                col -= 1
                break
            
        cells = '%s%d' % (self._col_name(col), row+1)
        if end_row is not None:
            cells += ':%d' % (end_row+1)
        selector = '.'.join([self.sheet.Name, cells])
        return OOSheet(selector)

    def find_last_row(self):
        if ':' not in self.cells:
            cells = self.cells
            end_col = None
        else:
            (start, end) = self.cells.split(':')
            start_col, start_row = self._position(start)
            end_col, end_row = self._position(end)
            assert start_row == end_row
            cells = start

        col, row = self._position(cells)
        while True:
            row += 1
            cell = self.sheet.getCellByPosition(col, row)
            if cell.getValue() == 0 and cell.getString() == '' and cell.getFormula() == '':
                row -= 1
                break

        cells = '%s%d' % (self._col_name(col), row+1)
        if end_col is not None:
            cells += ':%s%d' % (self._col_name(end_col), row+1)
        selector = '.'.join([self.sheet.Name, cells])
        return OOSheet(selector)

    def copy(self):
        self.focus()
        self.dispatch('.uno:Copy')

    def cut(self):
        self.focus()
        self.dispatch('.uno:Cut')

    def paste(self):
        self.focus()
        self.dispatch('.uno:Paste')

    def delete(self):
        self.focus()
        self.dispatch('.uno:Delete', ('Flags', 'A'))

    def format_as(self, selector):
        OOSheet(selector).copy()
        self.focus()
        self.dispatch('.uno:InsertContents',
                      ('Flags', 'T'),
                      ('FormulaCommand', 0),
                      ('SkipEmptyCells', False),
                      ('Transpose', False),
                      ('AsLink', False),
                      ('MoveMode', 4),
                      )

        self.dispatch('.uno:TerminateInplaceActivation')
        self.dispatch('.uno:Cancel')

    def undo(self):
        self.dispatch('.uno:Undo')

    def redo(self):
        self.dispatch('.uno:Redo')

    def save_as(self, filename):
        if not filename.startswith('/'):
            filename = os.path.join(os.environ['PWD'], filename)
            
        self.dispatch('.uno:SaveAs', ('URL', 'file://%s' % filename), ('FilterName', 'calc8'))
        
    def quit(self):
        self.dispatch('.uno:Quit')


class OOMerger():

    def __init__(self, ods, script):
        self.ods = zipfile.ZipFile(ods, 'a')
        self.script = script

        assert os.path.exists(script)

    @property
    def script_name(self):
        return self.script.rpartition('/')[2]

    def manifest_add(self, path):
        manifest = []
        for line in self.ods.open('META-INF/manifest.xml'):
            if '</manifest:manifest>' in line:
                manifest.append(' <manifest:file-entry manifest:media-type="application/binary" manifest:full-path="%s"/>' % path)
            elif ('full-path:"%s"' % path) in line:
                return
            
            manifest.append(line)

        self.ods.writestr('META-INF/manifest.xml', ''.join(manifest))
        

    def merge(self):
        self.ods.write(self.script, 'Scripts/python/%s' % self.script_name)
        
        self.manifest_add('Scripts/')
        self.manifest_add('Scripts/python/')
        self.manifest_add('Scripts/python/%s' % self.script_name)

        self.ods.close()

def merge():
    print "Hello"
        
        

        
        



