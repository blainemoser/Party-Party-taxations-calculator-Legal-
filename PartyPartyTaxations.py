'''
WRITTEN BY BLAINE MOSER
(BCom LLB [Wits])
Attorney

+27 72 916 4949

email: blainemoser@yahoo.com

This is a desktop Application that assists taxing masters and cost con-
sultants in preparing allocaturs for party-and-party bills of costs 
during taxation proceedings and/or settlement. The current version uses
tariffs applicable as at 28 May 2017.
The Application caters for both High Court and Magistrates' 
Court matters. 
Taxed-off amounts can be recorded in real time, in any order specified by
the user; to this end flexible editing functionality is provided.
Instances of the Application can be saved and retrieved.

'''


try:
    # for save functions
    import os
    # imports taxations classes
    from TaxationMod import *
    import sys
    # for save functions
    import pickle
    # for the entire app
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    # Converts numbers to Accounting Standard
    from acc_convert import AccConv
    
    import logging
    logging.basicConfig(level = logging.CRITICAL)

except Exception as e:
    logging.critical("Got: {}".format(str(e)))
    print(os.getcwd())

class MainWindow(QMainWindow):

    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)

        ## Main Setup

        QApplication.setStyle(QStyleFactory.create("Cleanlooks"))

        self.form_win =         formWin(self)
        self.setCentralWidget(self.form_win)
        self.setGeometry(250, 150, 1200, 800)

        ## BoilerPlate Operators
        
        self.exitEvent =        QEvent
        quitter =               QAction("&Exit", self)
        quitter.setShortcut("Ctrl+Q")
        quitter.setStatusTip("Exit 'Taxations'")
        quitter.triggered.connect(self.menuCloseEvent)

        self.statusBar()

        new =           QAction("&New Taxation", self)
        new.setShortcut('ctrl+n')
        new.setStatusTip('Create New Taxation')
        new.triggered.connect(self.newTaxationEvent)
        
        saveAs =        QAction("&Save As", self)
        saveAs.setShortcut('ctrl+shift+s')
        saveAs.setStatusTip("Save this Taxation")
        saveAs.triggered.connect(self.file_saveAs)
        
        
        save =          QAction("&Save", self)          
        save.setShortcut('ctrl+s')
        save.setStatusTip('Save Changes')
        save.triggered.connect(self.file_save)
        
        opener =        QAction("&Open", self)
        opener.setShortcut("Ctrl+o")
        opener.setStatusTip("Open Taxation")
        opener.triggered.connect(self.file_open)
        
        ## Create UndoStack
        self.undoStack =        QUndoStack(self)
        self.undoStack.setUndoLimit(200)
        
        undo =          QAction("&Undo", self)
        undo.setShortcut("Ctrl+z")
        undo.setStatusTip("Undo Last")
        undo.triggered.connect(self.undoEvent)
        
        redo =          QAction("&Redo", self)
        redo.setShortcut("Ctrl+y")
        redo.setStatusTip("Redo Last")
        redo.triggered.connect(self.redoEvent)

        mainMenu =      self.menuBar()

        fileMenu =      mainMenu.addMenu("&File")
        fileMenu.addAction(new)
        fileMenu.addAction(opener)
        fileMenu.addAction(save)
        fileMenu.addAction(saveAs)
        fileMenu.addAction(quitter)
        
        editMenu =      mainMenu.addMenu('&Edit')
        editMenu.addAction(undo)
        editMenu.addAction(redo)

        self.show()
        
        ## toggle radio buttons
        self.form_win.left.r1.toggled.connect(self.adder)
        self.form_win.left.r2.toggled.connect(self.adder)
        
        ## RIGHT-Click & Click (Menu) Events - FeesSubs
        self.form_win.topRight.setContextMenuPolicy(Qt.CustomContextMenu)
        self.form_win.topRight.connect(
            self.form_win.topRight,SIGNAL(
                "customContextMenuRequested(QPoint)" ),
            self.subRightClickEvent)

        ## RIGHT-Click & Click (Menu) Events - DisbSubs
        self.form_win.bottomRight.setContextMenuPolicy(Qt.CustomContextMenu)
        self.form_win.bottomRight.connect(
            self.form_win.bottomRight,SIGNAL(
                "customContextMenuRequested(QPoint)" ),
            self.disbRightClickEvent)
        ## SUB-FEES & DISB - FEES Capture
        self.form_win.left.nmf.editingFinished.connect(self.cap_fees)
        self.form_win.left.nmf.textChanged.connect(self.adder)
        self.form_win.left.nmd.editingFinished.connect(self.cap_disb)
        self.form_win.left.nmd.textChanged.connect(self.adder)
        self.form_win.left.nmfs.editingFinished.connect(self.cap_feesSub)
        self.form_win.left.nmds.editingFinished.connect(self.cap_disbSub)
        ## SUB-FEES & DISB - FEES Removal
        self.form_win.topRight.itemDoubleClicked.connect(self.subList_remover)
        self.deleter =          delKeys(self)
        self.form_win.bottomRight.itemDoubleClicked.connect(self.disbList_remover)
        ## SUB-FEES & DISB - FEES Editing -- #NB
        self.form_win.topRight.itemClicked.connect(self.feesListSelector)
        self.form_win.topRight.currentItemChanged.connect(self.feesListChange)
        self.form_win.bottomRight.itemClicked.connect(self.disbListSelector)
        self.form_win.bottomRight.currentItemChanged.connect(self.disbListChange)
        ## INIT - Gross Fees & Disb
        self.grossFees =        self.form_win.left.nmf.text()
        self.grossDisb =        self.form_win.left.nmd.text()
        ## Save Dict (Default) & Whether 'Save As' has been run;
        ## Also whether there are any changes that need saving
        self.saveAsRun =        False
        self.saveDict =         {1:'', 2:'', 3:[], 4:[], 5:True}
        self.changesMade =      False
        ## Save As name - Global 
        self.fileName =         ''
        self.setWindowTitle('Taxations')
        ## Defaults
        self.form_win.left.nmfto.setText('0.00')
        self.form_win.left.nmdto.setText('0.00')
        
### KEY PRESS

    def keyPressEvent(self, event):
        if      (event.key() == Qt.Key_Delete or 
                event.key() == Qt.Key_Backspace):
        
            self.subList_remover()
            self.disbList_remover()


### FEES LIST
        
    def cap_fees(self):
        self.grossFeesOld =     self.grossFees
        self.grossFeesNew =     self.form_win.left.nmf.text()
        text_in =               self.form_win.left.nmf
        command =               feesDisbInputs(text_in, self.grossFeesOld,
                                self.grossFeesNew,
                                'gfees {}'.format(text_in.text()))
        self.undoStack.push(command)
        self.form_win.left.nmfs.setFocus()
        self.grossFees =        self.form_win.left.nmf.text()
        self.adder()

    def cap_feesSub(self):
        ## No action = no trigger
        inList =        self.form_win.topRight
        text_in =       self.form_win.left.nmfs
        new =           text_in.text()
        if inList.currentItem() == None:
            self.cap_feesSubNewItem(new)
        else:
            original =  inList.currentItem().text()
            self.feesListEditor(new)
        inList.setCurrentItem(None)
        text_in.setText(None)

    def cap_feesSubNewItem(self, new):
        inList =        self.form_win.topRight
        text_in =       self.form_win.left.nmfs
        Font =          QFont("Arial",12)
        Font.setItalic(False)
        item =          QListWidgetItem()
        item.setFont(Font)
        item.setText(new)
        #row =           inList.currentRow()
        command =       addSubList(inList, text_in,
                         "Add {}".format(text_in))
        self.undoStack.push(command)
        
        text_in.clear()
        self.adder()
             
    def subList_remover(self):
        inList =        self.form_win.topRight
        row =           inList.currentRow()
        text_in =       inList.currentItem()
        command =       commandDelete(inList, row, text_in,
                        "Add {}".format(text_in))
        self.undoStack.push(command)
        inList.setCurrentItem(None)
        self.adder()
        
    def feesListSelector(self):
        inList =        self.form_win.topRight
        text_in =       self.form_win.left.nmfs
        Font =          QFont("Arial",12)
        Font.setItalic(False)
        try:
            float(inList.currentItem().text())
            text_in.setText(inList.currentItem().text())
        except ValueError:
            text_in.setText('')
            text_in.setFocus()
            inList.currentItem().setText('editing...')
            
    def feesListEditor(self, new):
        inList =        self.form_win.topRight
        text_in =       self.form_win.left.nmfs
        ## Capture Original Entry. Note: 'new' is the new entry
        original =      inList.currentItem().text()
        try:
            float(original)
            command =   subListEdit(inList, inList.currentRow(), new, 
            original,  "Edit {}".format(original))
            self.undoStack.push(command)
        except ValueError:
            command =   subListEdit(inList, inList.currentRow(), new, 
            original,  "Edit {}".format(original))
            self.undoStack.push(command)
        text_in.clear()
        self.adder()

    def feesListChange(self, current, previous):
        if previous != None and previous.text() == 'editing...':
            previous.setText('blank item - click to edit')
            
    def subRightClickEvent(self, QPos):
        self.listMenu =         QMenu()
        self.menuItem =         self.listMenu.addAction("Add item here:")
        self.form_win.topRight.connect(self.menuItem, 
                        SIGNAL("triggered()"), 
                        self.subMenuItemClicked)
        parentPosition =        self.form_win.topRight.mapToGlobal(QPoint(0, 0))        
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()
        
    def subMenuItemClicked(self):
        listWidget =    self.form_win.topRight
        row =           listWidget.currentRow()
        command =       insertSubList(listWidget, row,
                        "Insert {}".format(str(row)))
        self.undoStack.push(command)
     
### DISBURSEMENTS LIST
     
    def cap_disb(self):
        self.grossDisbOld =     self.grossDisb
        self.grossDisbNew =     self.form_win.left.nmd.text()
        text_in =               self.form_win.left.nmd
        command =               feesDisbInputs(text_in, self.grossDisbOld,
                                self.grossDisbNew,
                                'gdisb {}'.format(text_in.text()))
        self.undoStack.push(command)
        self.form_win.left.nmds.setFocus()
        self.grossDisb =        self.form_win.left.nmd.text()
        self.adder()
        
    def cap_disbSub(self):
        ## No action = no trigger
        inList =        self.form_win.bottomRight
        text_in =       self.form_win.left.nmds
        new =           text_in.text()
        if inList.currentItem() == None:
            self.cap_disbSubNewItem(new)
        else:
            original =  inList.currentItem().text()
            self.disbListEditor(new)
        inList.setCurrentItem(None)
        text_in.setText(None)
          
    def cap_disbSubNewItem(self, new):
        inList =        self.form_win.bottomRight
        text_in =       self.form_win.left.nmds
        Font =          QFont("Arial",12)
        Font.setItalic(False)
        item =          QListWidgetItem()
        item.setFont(Font)
        item.setText(new)
        #row =           inList.currentRow()
        command =       addSubList(inList, text_in,
                         "Add {}".format(text_in))
        self.undoStack.push(command)
        
        text_in.clear()
        self.adder()          

    def disbList_remover(self):
        inList =        self.form_win.bottomRight
        row =           inList.currentRow()
        text_in =       inList.currentItem()
        command =       commandDelete(inList, row, text_in,
                                "Add {}".format(text_in))
        self.undoStack.push(command)
        inList.setCurrentItem(None)
        self.adder()

    def disbListSelector(self):
        inList =        self.form_win.bottomRight
        text_in =       self.form_win.left.nmds
        Font =          QFont("Arial",12)
        Font.setItalic(False)
        try:
            float(inList.currentItem().text())
            text_in.setText(inList.currentItem().text())
        except ValueError:
            text_in.setText('')
            text_in.setFocus()
            inList.currentItem().setText('editing...')

    def disbListEditor(self, new):
        inList =        self.form_win.bottomRight
        text_in =       self.form_win.left.nmds
        ## Capture Original Entry. Note: 'new' is the new entry
        original =      inList.currentItem().text()
        try:
            float(original)
            command =   subListEdit(inList, inList.currentRow(), new, 
            original,  "Edit {}".format(original))
            self.undoStack.push(command)
        except ValueError:
            command =   subListEdit(inList, inList.currentRow(), new, 
            original,  "Edit {}".format(original))
            self.undoStack.push(command)
        text_in.clear()
        self.adder()

    def disbListChange(self, current, previous):
        if previous != None and previous.text() == 'editing...':
            previous.setText('blank item - click to edit')

    def disbRightClickEvent(self, QPos):
        self.listMenu =         QMenu()
        self.menuItem =         self.listMenu.addAction("Add item here:")
        self.form_win.bottomRight.connect(self.menuItem, 
                        SIGNAL("triggered()"), 
                        self.disbMenuItemClicked)
        parentPosition =        self.form_win.bottomRight.mapToGlobal(QPoint(0, 0))        
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()
        
    def disbMenuItemClicked(self):
        listWidget =    self.form_win.bottomRight
        row =           listWidget.currentRow()
        command =       insertSubList(listWidget, row,
                        "Insert {}".format(str(row)))
        self.undoStack.push(command)
        
### MAIN FUNCTION (NUMBER CRUNCHER)

    def adder(self):
        Font = QFont("Arial",12)
        #Fees:
        feesList =              self.form_win.topRight
        grossFees =             self.form_win.left.nmf
        feeTO =                 self.form_win.left.nmfto
        feeItems =              []
        for index in range(feesList.count()):
            feeItems.append(str(feesList.item(index).text()))
        # float value of Fees T/O
        feeResult =             0
        for i in feeItems:
            try:
                feeResult += float(i)
            except ValueError:
                pass
        ## Print Result to Taxed-off fees
        feeTO.setText(AccConv(feeResult))
        netFees =               self.form_win.left.nmfnet
        netFees.setFont(Font)
        try:
            netFees.setText(AccConv(float(grossFees.text())
                                    - feeResult))
        except ValueError:
            netFees.setText('')
        ## disbursements:
        disbList =              self.form_win.bottomRight
        grossDisb =             self.form_win.left.nmd
        disbTO =                self.form_win.left.nmdto
        disbItems =             []
        for index in range(disbList.count()):
            disbItems.append(str(disbList.item(index).text()))
        disbResult =            0
        for i in disbItems:
            try:
                disbResult += float(i)
            except ValueError:
                pass
        ## Print result to taxed-off disbursements
        disbTO.setText(str(AccConv(disbResult)))
        netDisb = self.form_win.left.nmdnet
        netDisb.setFont(Font)
        try:
            netDisb.setText(AccConv(float(grossDisb.text())
                                    - disbResult)) 
        except ValueError:
           netDisb.setText('')
        ## Choose 1 - HC or MC:
        if len(grossDisb.text()) > 0 and len(grossFees.text()) > 0:
                if self.form_win.left.r1.isChecked() == True:
                        self.taxer = HighCourtTaxations(
                        float(grossFees.text()), feeResult, 
                        float(grossDisb.text()), disbResult)
                else: 
                                self.taxer = MagCourtTaxations(
                                float(grossFees.text()), feeResult, 
                                float(grossDisb.text()), disbResult)
                ## Set the Variables
                drawFees =      AccConv(self.taxer.draw_fee)
                subTot1 =       AccConv(self.taxer.subTot1)
                addDisb =       AccConv(self.taxer.addDisb)
                subTot2 =       AccConv(self.taxer.subTot2)
                attendanceFee = AccConv(self.taxer.attendance_fee)
                vat =           AccConv(self.taxer.vat)
                grandTot =      AccConv(self.taxer.grandTot)
                ## Set the spaces
                self.form_win.left.nmdraw.setText(drawFees)
                self.form_win.left.nmst1.setText(subTot1)
                self.form_win.left.nmad.setText(addDisb)
                self.form_win.left.nmst2.setText(subTot2)
                self.form_win.left.nmatt.setText(attendanceFee)
                self.form_win.left.nmvat.setText(vat)
                self.form_win.left.nmtot.setText(grandTot)
        ## Whether a change has been made
        self.changesMade =      True
        
### BoilerPlate Functions
    
    def file_open(self):
        self.saveChangesEvent(self.opener, self.passer)
            
    def opener(self):
        try:
            name =          QFileDialog.getOpenFileName(self, 'Open File')
            file =          open(name,'rb')
            self.fileName = name
            try:
                self.saveDict =         pickle.load(file)
                self.saveAsRun =        True
                self.changesMade =      False
                self.setWindowTitle('Taxations: {}'.format(self.fileName))
                self.openClear()
            except Exception:
                self.statusBar().showMessage(
                """Unable to open the selected file. The data may be corrupted.""",
                                        20000)
            self.restore()
        except Exception:
            pass
    
    def openClear(self):
        self.form_win.left.r1.setChecked(True)
        self.form_win.topRight.clear()
        self.form_win.bottomRight.clear()
        self.form_win.left.nmdraw.clear()
        self.form_win.left.nmst1.clear()
        self.form_win.left.nmad.clear()
        self.form_win.left.nmst2.clear()
        self.form_win.left.nmatt.clear()
        self.form_win.left.nmvat.clear()
        self.form_win.left.nmtot.clear()
        self.form_win.left.nmf.clear()
        self.form_win.left.nmfs.clear()
        self.form_win.left.nmds.clear()
        self.form_win.left.nmfto.setText('0.00')
        self.form_win.left.nmd.clear()
        self.form_win.left.nmdto.setText('0.00')
        self.undoStack.clear()
    
    def restore(self):
        Font =             QFont('Arial', 8)
        Font.setItalic(True)
        self.undoStack.clear()
        try:
            self.form_win.left.nmf.setText(self.saveDict[1])
            self.form_win.left.nmd.setText(self.saveDict[2])
            for i in self.saveDict[3]:
                try:
                    float(i)
                    self.form_win.topRight.addItem(i)
                except ValueError:
                    item =       QListWidgetItem()
                    item.setFont(Font)
                    item.setText(i)
                    self.form_win.topRight.addItem(item)
            for i in self.saveDict[4]:
                 try:
                    float(i)
                    self.form_win.bottomRight.addItem(i)
                 except ValueError:
                    item =       QListWidgetItem()
                    item.setFont(Font)
                    item.setText(i)
                    self.form_win.bottomRight.addItem(item)
            if self.saveDict[5] == True:
                 self.form_win.left.r1.setChecked(True)
            else:
                 self.form_win.left.r2.setChecked(True)  
        except Exception:
            self.statusBar().showMessage(
            """Unable to open the selected file.The Data may be corrupted.""",
                                        20000)
        
    def file_saveAs(self):
        self.updateDict()
        ## Pickle the dict 
        self.fileName =         QFileDialog.getSaveFileName(self, 
                           'Save File')
        file =                  open(self.fileName,'wb')
        pickle.dump(self.saveDict,file)
        file.close()
        self.setWindowTitle('Taxations: {}'.format(self.fileName))
        self.saveAsRun =        True
        self.changesMade =      False
        
    def file_save(self):
        if self.saveAsRun == False:
            self.file_saveAs()
        else:
            self.updateDict()
            file =                  open(self.fileName,'wb')
            pickle.dump(self.saveDict,file)
            file.close()
            self.changesMade =      False
            
    def updateDict(self):
        ## UPDATE save Dict
        self.saveDict[1] =      self.form_win.left.nmf.text()
        self.saveDict[2] =      self.form_win.left.nmd.text()
        feesList =              self.form_win.topRight
        feeItems =              []
        for index in range(feesList.count()):
            feeItems.append(str(feesList.item(index).text()))
        disbList =              self.form_win.bottomRight
        disbItems =             []
        for index in range(disbList.count()):
            disbItems.append(str(disbList.item(index).text()))
        self.saveDict[3] =      feeItems
        self.saveDict[4] =      disbItems
        self.saveDict[5] =      self.form_win.left.r1.isChecked() 

    def saveChangesEvent(self, mainFunction, cancel, event = QEvent):
        if self.saveAsRun == False and self.changesMade == False:
            mainFunction()
        elif self.saveAsRun == False and self.changesMade == True:
            choice =        QMessageBox.question(self, 'Save',
                        "Would you like to save this Taxation?",
                                                QMessageBox.Yes | 
                                                QMessageBox.No |
                                                QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                try:
                    self.file_saveAs()
                    mainFunction()
                except Exception:
                    cancel()
            elif choice == QMessageBox.No:
                mainFunction()
            else:
                cancel()
        elif self.saveAsRun == True and self.changesMade == True:
            choice =        QMessageBox.question(self, 'Save Changes',
                        "Would you like to save the changes you made?",
                                                QMessageBox.Yes | 
                                                QMessageBox.No |
                                                QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                self.file_save()
                mainFunction()
            elif choice == QMessageBox.No:
                mainFunction()
            else:
                cancel()
        else:
            mainFunction()

    def passer(self):
        pass
    
    def newTaxationEvent(self):
        self.saveChangesEvent(self.clearAll, self.passer)
    
    def clearAll(self):
        self.form_win.left.r1.setChecked(True)
        self.form_win.topRight.clear()
        self.form_win.bottomRight.clear()
        self.form_win.left.nmdraw.clear()
        self.form_win.left.nmst1.clear()
        self.form_win.left.nmad.clear()
        self.form_win.left.nmst2.clear()
        self.form_win.left.nmatt.clear()
        self.form_win.left.nmvat.clear()
        self.form_win.left.nmtot.clear()
        self.form_win.left.nmf.clear()
        self.form_win.left.nmfs.clear()
        self.form_win.left.nmds.clear()
        self.form_win.left.nmfto.setText('0.00')
        self.form_win.left.nmd.clear()
        self.form_win.left.nmdto.setText('0.00')
        self.saveAsRun =        False
        self.changesMade =      False
        self.setWindowTitle('Taxations')
        self.undoStack.clear()

    def closeEvent(self, event):
        self.saveChangesEvent(event.accept, event.ignore)

    def menuCloseEvent(self):
        self.saveChangesEvent(sys.exit, self.passer)
        

    def undoEvent(self):
            self.undoStack.undo()
            self.adder()
            
    def redoEvent(self):
            self.undoStack.redo()
            self.adder()


class addSubList(QUndoCommand):

    def __init__(self, listWidget, string, description):
        super(addSubList, self).__init__(description)
        self.listWidget =       listWidget
        self.newRow =           self.listWidget.count() + 2
        self.oldRow =           self.listWidget.count()
        self.string =           string.text()
        
    def redo(self):
        self.listWidget.insertItem(self.newRow, self.string)

    def undo(self):
        item =                  self.listWidget.takeItem(self.oldRow)
        del item
        
 
class insertSubList(QUndoCommand):
        
    def __init__(self, listWidget, row, description):
        super(insertSubList, self).__init__(description)
        self.listWidget =           listWidget
        if row == -1:
            self.row =              0
        else:
            self.row =              row
        self.placeHolder =          QListWidgetItem()
        self.Font =                 QFont("Arial",8)
        self.Font.setItalic(True)
        self.placeHolder.setFont(self.Font)
        self.placeHolder.setText("blank item - click to edit")
        
    def redo(self):
        self.listWidget.insertItem(self.row, self.placeHolder)
        
    def undo(self):
        item =                      self.listWidget.takeItem(self.row)
        del item
        
        
class commandDelete(QUndoCommand):

    def __init__(self, listWidget, row, text_in, description):
        super(commandDelete, self).__init__(description)
        self.listWidget =       listWidget
        self.text_in =          text_in
        self.row =              row

    def redo(self):
        item =                  self.listWidget.takeItem(self.row)
        del item
        self.listWidget.setCurrentRow(self.row)

    def undo(self):
        self.listWidget.insertItem(self.row, self.text_in)
        self.listWidget.setCurrentRow(self.row)


class subListEdit(QUndoCommand):
    
    def __init__(self, listWidget, row, new, original, description):
        super(subListEdit, self).__init__(description)
        self.original =         original
        self.new =              new
        self.listWidget =       listWidget
        self.row =              row
        self.Font =             QFont('Arial', 8)
        self.Font.setItalic(True)
        
    def redo(self):
        item =                  self.listWidget.takeItem(self.row)
        self.listWidget.insertItem(self.row, self.new)
        del item
        self.listWidget.setCurrentRow(self.row)

    def undo(self):
        item =                  self.listWidget.takeItem(self.row)
        del item
        try:
            float(self.original)
            self.listWidget.insertItem(self.row, self.original)
        except ValueError:
            self.placeHolder =  QListWidgetItem()
            self.placeHolder.setFont(self.Font)
            self.placeHolder.setText("blank item - click to edit")
            self.listWidget.insertItem(self.row, self.placeHolder)
        self.listWidget.setCurrentRow(self.row)


class formWin(QWidget):

    def __init__(self, parent = None):
        super(formWin, self).__init__(parent)

        self.hbox =             QHBoxLayout(self)

        self.left =             Frame1(self)
        self.topRightLabel =    QLabel("""Fees' Deductions List:
        Click on an item to edit it
        Double-Click on an item to delete it
        Right-Click on an item to add an item above""")
        self.topRight =         SubList(self)
        self.bottomRightLabel = QLabel("""Disbursements' Deductions List:
        Click on an item to edit it
        Double-Click on an item to delete it
        Right-Click on an item to add an item above""")
        self.bottomRight =      SubList(self)

        self.splitter =         QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.left)

        self.splitter2 =        QSplitter(Qt.Vertical)
        self.splitter2.addWidget(self.topRightLabel)
        self.splitter2.addWidget(self.topRight)
        self.splitter2.addWidget(self.bottomRightLabel)
        self.splitter2.addWidget(self.bottomRight)

        self.splitter.addWidget(self.splitter2)

        self.hbox.addWidget(self.splitter)

        self.setLayout(self.hbox)
 
        
class Frame1(QFrame):

    def __init__(self, parent = None):
        super(Frame1, self).__init__(parent)

        self.fbox =     QFormLayout()
        self.hbox =     QHBoxLayout()
        self.hbox.addStretch()
        
        ## Radio Buttons
        self.fbox.addRow(QLabel("Court:"),self.hbox)
        self.r1 =       QRadioButton("High Court")
        self.r1.setChecked(True)
        self.r2 =       QRadioButton("Magistrates' Court")
        self.hbox.addWidget(self.r1)
        self.hbox.addWidget(self.r2)
        ## Gross Fees
        self.feeTot =   QLabel("Gross Fees:")
        self.nmf =      QLineEdit()
        self.nmf.setPlaceholderText("enter before-taxation fees")
        self.nmf.setValidator(QDoubleValidator())
        self.nmf.setAlignment(Qt.AlignLeft)
        self.nmf.setFont(QFont("Arial",12))
        ## Fees Sub(s)
        self.feeSub =   QLabel('Less:')
        self.feeSub.setIndent(50)
        self.nmfs =     QLineEdit()
        self.nmfs.setPlaceholderText("Less (can enter as individual items)")
        self.nmfs.setValidator(QDoubleValidator())
        self.nmfs.setAlignment(Qt.AlignLeft)
        self.nmfs.setFont(QFont("Arial",12))
        ## Fees Taxed-off
        self.feeTO =    QLabel('Less Total Taxed-off:')
        self.nmfto =    QLineEdit()
        self.nmfto.setAlignment(Qt.AlignLeft)
        self.nmfto.setFont(QFont("Arial",12))
        self.nmfto.setReadOnly(True)
        ## Disb Tot
        self.disbTot = QLabel('Gross Disbursements:')
        self.nmd =      QLineEdit()
        self.nmd.setPlaceholderText("enter before-taxation disbursments")
        self.nmd.setValidator(QDoubleValidator())
        self.nmd.setAlignment(Qt.AlignLeft)
        self.nmd.setFont(QFont("Arial",12))
        ## Disb Sub(s)
        self.disbSub =  QLabel('Less:')
        self.disbSub.setIndent(50)
        self.nmds =     QLineEdit()
        self.nmds.setPlaceholderText("Less (can enter as individual items)")
        self.nmds.setValidator(QDoubleValidator())
        self.nmds.setAlignment(Qt.AlignLeft)
        self.nmds.setFont(QFont("Arial",12))
        ## Disb TO
        self.nmfto =    QLineEdit()
        self.nmfto.setAlignment(Qt.AlignLeft)
        self.nmfto.setFont(QFont("Arial",12))
        self.nmfto.setReadOnly(True)
        ## Splitter - Net Disbursements and Fees
        self.splitter = QSplitter(Qt.Horizontal)
        self.netFees =  QLabel('''SUBTOTAL
(net Fees):''')
        self.netFees.setIndent(8)
        self.netDisb =          QLabel('''SUBTOTAL
(net Disbursements):''')
        self.netDisb.setIndent(15)
        self.nmfnet =           QLineEdit()
        self.nmfnet.setReadOnly(True)
        self.nmdnet =           QLineEdit()
        self.nmdnet.setReadOnly(True)
        self.nmdnet.setAlignment(Qt.AlignLeft)
        self.splitter.addWidget(self.netFees)
        self.splitter.addWidget(self.nmfnet)
        self.splitter.addWidget(self.netDisb)
        self.splitter.addWidget(self.nmdnet)
        ## Disb TO Line
        self.disbTO =           QLabel('Less Total Taxed-off:')
        self.nmdto =            QLineEdit()
        self.nmdto.setAlignment(Qt.AlignLeft)
        self.nmdto.setFont(QFont("Arial",12))
        self.nmdto.setReadOnly(True)
        ## Drawing
        self.drawing =          QLabel('Drawing Fees:')
        self.nmdraw =           QLineEdit()
        self.nmdraw.setFont(QFont("Arial",12))
        self.nmdraw.setReadOnly(True)
        self.nmdraw.setAlignment(Qt.AlignLeft)
        ## Sub Total 1
        self.subt1 =            QLabel('SUBTOTAL:')
        self.nmst1 =            QLineEdit()
        self.nmst1.setFont(QFont("Arial",12))
        self.nmst1.setReadOnly(True)
        ## Add Disbursements
        self.addDisb =          QLabel('Add: Disbursements:')
        self.nmad =             QLineEdit()
        self.nmad.setFont(QFont("Arial",12))
        self.nmad.setReadOnly(True)
        ## Sub Total 2
        self.subt2 =            QLabel('SUBTOTAL:')
        self.nmst2 =            QLineEdit()
        self.nmst2.setFont(QFont("Arial",12))
        self.nmst2.setReadOnly(True)
        ## Add Attending Fee
        self.attending =        QLabel('Attending Fees:')
        self.nmatt =            QLineEdit()
        self.nmatt.setFont(QFont("Arial",12))
        self.nmatt.setReadOnly(True)
        self.nmatt.setAlignment(Qt.AlignLeft)
        ## Add Vat
        self.vat =              QLabel('Add VAT (@ 14%):')
        self.nmvat =            QLineEdit()
        self.nmvat.setFont(QFont("Arial",12))
        self.nmvat.setReadOnly(True)
        self.nmvat.setAlignment(Qt.AlignLeft)
        ## Total
        self.tot =              QLabel('TOTAL:')
        self.nmtot =            QLineEdit()
        self.nmtot.setFont(QFont("Arial",12))
        self.nmtot.setReadOnly(True)
        self.nmtot.setAlignment(Qt.AlignLeft)
        ## LAYOUT
        self.fbox.addRow(self.feeTot,self.nmf)
        self.fbox.addRow(self.feeSub,self.nmfs)
        self.fbox.addRow(self.feeTO,self.nmfto)
        self.fbox.addRow(self.disbTot,self.nmd)
        self.fbox.addRow(self.disbSub,self.nmds)
        self.fbox.addRow(self.disbTO,self.nmdto)
        self.fbox.addRow(self.splitter)
        self.fbox.addRow(self.drawing, self.nmdraw)
        self.fbox.addRow(self.subt1,  self.nmst1)
        self.fbox.addRow(self.addDisb,  self.nmad)
        self.fbox.addRow(self.subt2,  self.nmst2)
        self.fbox.addRow(self.attending, self.nmatt)
        self.fbox.addRow(self.vat, self.nmvat)
        self.fbox.addRow(self.tot, self.nmtot)
        layout = self.setLayout(self.fbox)


class SubList(QListWidget):

    def __init__(self, parent):
        super(SubList, self).__init__(parent)
        self.delSignal =     delKeys(self)       


class delKeys(QObject):
        
        def __init__(self, parent):
            super(delKeys, self).__init__(parent)
            self.delFunct =         pyqtSignal(bool)
                
            
class feesDisbInputs(QUndoCommand):
        
    def __init__(self, text_in, old, new, description):
        super(feesDisbInputs, self).__init__(description)
        self.text_in =          text_in
        self.old =              old
        self.new =              new

    def redo(self):
        self.text_in.setText(self.new)

    def undo(self):
        self.text_in.setText(self.old)
        
def main():
    app =       QApplication(sys.argv)
    GUI =       MainWindow()
    sys.exit(app.exec())
    
if __name__ == '__main__':
    main()
