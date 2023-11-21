import sys
import os
import random
from typing import Callable
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

class ProcessInfo: # classe com informações sobre um processo
    class PageTableEntry:
        def __init__(self, entry: str):
            self.pBit = int(entry.split(" ")[0])
            self.mBit = int(entry.split(" ")[1])
            self.value = int(entry.split(" ")[2])
            
    def __init__(self, name: str, state: str, size: int, pageTableMS: list[str], pageTableMP: list[str]):
        self.name = name
        self.state = state
        self.size = size
        self.pageTableMS = [self.PageTableEntry(entry) for entry in pageTableMS]
        self.pageTableMP = [self.PageTableEntry(entry) for entry in pageTableMP]
        self.color = QColor(random.randint(150,255),random.randint(150,255),random.randint(150,255))

    def __eq__(self, other): 
        if not isinstance(other, ProcessInfo):
            return NotImplemented

        return self.name == other.name

class InputWidget(QWidget): # entrada de configuracoes
    def __init__(self, nomeLabel: str):
        super().__init__()

        input_layout = QVBoxLayout(self)

        self.input_label = QLabel(self)
        self.input_label.setText(nomeLabel)
        self.input_label.setAlignment(Qt.AlignLeft)

        self.input_line_edit = QLineEdit()
        self.input_line_edit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)

        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line_edit)
        input_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(input_layout)

    def getValue(self) -> int:
        return int(self.input_line_edit.text())
    
    def setValue(self, value: int) -> None:
        self.input_line_edit.setText(str(value))

class SettingsMenu(QWidget): # menu de configuracoes
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tam_mp_input = InputWidget("Tamanho da MP")
        self.tam_ms_input = InputWidget("Tamanho da MS")
        self.tam_pag_input = InputWidget("Tamanho da página")
        self.tam_end_input = InputWidget("Tamanho do end. lógico")

        config_bts_layout = QHBoxLayout()
        self.config_cancel_btn = QPushButton("CANCELAR")
        self.config_save_btn = QPushButton("SALVAR")
        config_bts_layout.addWidget(self.config_cancel_btn)
        config_bts_layout.addWidget(self.config_save_btn)

        layout.addWidget(self.tam_mp_input)
        layout.addWidget(self.tam_ms_input)
        layout.addWidget(self.tam_pag_input)
        layout.addWidget(self.tam_end_input)
        layout.addLayout(config_bts_layout)

        self.setLayout(layout)

    def connectButtons(self, cancelPressFunc: Callable, savePressFunc: Callable):
        self.config_cancel_btn.clicked.connect(cancelPressFunc)
        self.config_save_btn.clicked.connect(savePressFunc)

    def setValues(self, tam_mp: int, tam_ms: int, tam_pag: int, tam_end: int) -> None:
        self.tam_mp_input.setValue(tam_mp)
        self.tam_ms_input.setValue(tam_ms)
        self.tam_pag_input.setValue(tam_pag)
        self.tam_end_input.setValue(tam_end)

class ControlButtonsWidget(QWidget): # botoes de controle de execucao
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        playIcon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        backIcon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward)
        nextIcon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward)

        self.back_btn = QPushButton(objectName="button")
        self.back_btn.setIcon(backIcon)
        self.back_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.play_btn = QPushButton(objectName="button")
        self.play_btn.setIcon(playIcon)
        self.play_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.next_btn = QPushButton(objectName="button")
        self.next_btn.setIcon(nextIcon)
        self.next_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        layout.addWidget(self.back_btn)
        layout.addWidget(self.play_btn)
        layout.addWidget(self.next_btn)

        self.setLayout(layout)

    def connectButtons(self, onBackPress: Callable, onPlayPress: Callable, onNextPress: Callable):
        self.back_btn.clicked.connect(onBackPress)
        self.play_btn.clicked.connect(onPlayPress)
        self.next_btn.clicked.connect(onNextPress)

class FileSelectorWidget(QWidget): # selecionador de arquivo
    def __init__(self, selectorLabel: str):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignRight)

        self.fileSelectLabel = QLabel(self)
        self.fileSelectLabel.setText(selectorLabel)
        self.fileSelectLabel.setAlignment(Qt.AlignCenter)
        self.fileSelectLabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)

        self.fileSelect = QComboBox(self)
        self.fileSelect.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self.fileOpenBtn = QPushButton("ABRIR")
        self.fileOpenBtn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        layout.addWidget(self.fileSelectLabel)
        layout.addWidget(self.fileSelect)
        layout.addWidget(self.fileOpenBtn)

        self.setLayout(layout)

    def connectButton(self, function: Callable):
        self.fileOpenBtn.clicked.connect(function)

    def getFiles(self, directoryPath: str):
        text_files = [f for f in os.listdir(directoryPath) if f.endswith('.txt')]
        self.fileSelect.addItems(text_files)

    def getSelectedText(self) -> str:
        return self.fileSelect.currentText()

class TerminalWidget(QWidget): # terminal com visualizador e input
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.commands: list[str] = []
        self.highlightedCmdInd: int = -1

        self.terminalLabel = QLabel(self)
        self.terminalLabel.setText("Terminal")
        self.terminalLabel.setAlignment(Qt.AlignCenter)
        self.terminalLabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        layout.addWidget(self.terminalLabel)

        self.textOutput = QTextEdit(self)
        self.textOutput.setReadOnly(True)
        self.textOutput.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        layout.addWidget(self.textOutput)
        

        self.inputBar = QLineEdit(self)
        self.inputBar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        layout.addWidget(self.inputBar)

        self.setLayout(layout)

    def connectInput(self, inputFunc: Callable):
        self.inputBar.returnPressed.connect(inputFunc)

    def appendCommand(self, command: str):
        self.commands.append(f"• {command}")
        self.textOutput.append(f"• {command}")
        self.updateWindow()

    def highlightCommand(self, command: str):
        for i,cmd in enumerate(self.commands):
            if cmd[2:] == command:
                self.commands[i] = f"> {cmd[2:]}"
                self.highlightedCmdInd = i
            else:
                self.commands[i] = f"• {cmd[2:]}"
        self.updateWindow()

    def highlightNext(self):
        if self.highlightedCmdInd < len(self.commands)-1:
            self.highlightCommand(self.commands[self.highlightedCmdInd+1][2:])

    def highlightLast(self):
        if self.highlightedCmdInd > 0:
            self.highlightCommand(self.commands[self.highlightedCmdInd-1][2:])
        else:
            self.highlightedCmdInd = -1
            self.highlightCommand("")

    def updateWindow(self):
        self.textOutput.clear()
        for cmd in self.commands:
            self.textOutput.append(cmd)

    def resetWindow(self):
        self.commands = []
        self.highlightedCmdInd = -1
        self.updateWindow()
        
class ProcessInfoWindowWidget(QWidget): # janela com status do processo escolhido
    def __init__(self, titleLabel: str):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.statusWindowLabel = QLabel(self)
        self.statusWindowLabel.setText(titleLabel)
        self.statusWindowLabel.setAlignment(Qt.AlignCenter)
        self.statusWindowLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setVisible(False)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["M", "P", "Quadro"])
        self.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.tableWidget.setMaximumHeight(400)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setSectionsClickable(False)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

        self.mainLabel = QLabel(self)

        self.mainLabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)

        layout.addWidget(self.statusWindowLabel)
        layout.addWidget(self.mainLabel)
        layout.addWidget(self.tableWidget)

        self.setLayout(layout)

    def update(self, processInfo: ProcessInfo):
        self.mainLabel.setText(f"Nome: {processInfo.name}\nEstado atual: {processInfo.state}\nTamanho: {processInfo.size}B\nTabela de páginas:")
        self.setPalette(processInfo.color)
        self.setAutoFillBackground(True)
        self.updateTable(processInfo.pageTableMP)
        self.tableWidget.setVisible(True)

    def clear(self):
        self.mainLabel.setText("")
        self.setAutoFillBackground(False)
        self.tableWidget.clearContents()
        self.tableWidget.setVisible(False)

    def updateTable(self, pageTable: list[ProcessInfo.PageTableEntry]):
        self.tableWidget.setRowCount(len(pageTable))
        rowHeight = 10

        for row, entry in enumerate(pageTable):
            self.tableWidget.setRowHeight(row, rowHeight)
            modification_bit_item = QTableWidgetItem(str(entry.mBit))
            modification_bit_item.setFlags(modification_bit_item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            modification_bit_item.setTextAlignment(Qt.AlignCenter)
            presence_bit_item = QTableWidgetItem(str(entry.pBit))
            presence_bit_item.setFlags(presence_bit_item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            presence_bit_item.setTextAlignment(Qt.AlignCenter)
            frame_number_item = QTableWidgetItem(str(entry.value))
            frame_number_item.setFlags(frame_number_item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            frame_number_item.setTextAlignment(Qt.AlignCenter)

            self.tableWidget.setItem(row, 0, modification_bit_item)
            self.tableWidget.setItem(row, 1, presence_bit_item)
            self.tableWidget.setItem(row, 2, frame_number_item)

        self.tableWidget.resizeColumnsToContents()

class StatusWindowWidget(QWidget): # janela com status de atualizações do simulador
    def __init__(self, titleLabel: str):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.updateWindowLabel = QLabel(self)
        self.updateWindowLabel.setText(titleLabel)
        self.updateWindowLabel.setAlignment(Qt.AlignCenter)
        self.updateWindowLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self.mainLabel = QTextEdit(self)
        self.mainLabel.setReadOnly(True)
        self.mainLabel.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        self.mainLabel.setMaximumWidth(150)

        layout.addWidget(self.updateWindowLabel)
        layout.addWidget(self.mainLabel)

        self.setLayout(layout)

    def update(self, text: str):
        self.mainLabel.clear()
        self.mainLabel.setText(text)

class MemoryTableWidget(QWidget): # unidade de memoria feita usando uma tabela
    def __init__(self, nameLabel: str, pageNumber: int, pageSize: int, lineSize: int):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop)

        self.memTable = QTableWidget()

        self.label = QLabel(self)
        self.label.setText(nameLabel)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)

        MAX_HEIGHT = pageNumber * lineSize + 2
        self.memTable.setMaximumHeight(MAX_HEIGHT)
        self.memTable.setMaximumWidth(120)
        #mem.setColumnWidth(0, 100)
        self.memTable.verticalHeader().setVisible(True)
        self.memTable.verticalHeader().setSectionsClickable(False)
        self.memTable.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.memTable.horizontalHeader().setVisible(False)
        
        self.memTable.setRowCount(pageNumber)
        self.memTable.setColumnCount(1)
        self.memTable.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        self.memTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        

        for row in range(pageNumber):
            item = QTableWidgetItem(f"P{row}")
            item.setFlags(item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            item.setTextAlignment(Qt.AlignCenter)
            self.memTable.setItem(row, 0, item)
            self.memTable.setRowHeight(row, lineSize)
            self.updatePage(row)

            headerWidget = QTableWidgetItem(str(pageSize*row))
            headerWidget.setText(str(row * pageSize))
            headerWidget.setFlags(item.flags() & ~Qt.ItemIsEditable)
            headerWidget.setTextAlignment(Qt.AlignTop | Qt.AlignRight)
            self.memTable.setVerticalHeaderItem(row, headerWidget)

            verticalHeaderFont = headerWidget.font()
            verticalHeaderFont.setPointSize(7)
            headerWidget.setFont(verticalHeaderFont)

        layout.addWidget(self.label)
        layout.addWidget(self.memTable)

        self.setLayout(layout)

    def updatePage(self, rowIndex: int, processName: str = None, color: QColor = QColor(255, 255, 255)):
        item = self.memTable.item(rowIndex, 0)
        if (processName == None):
            item.setText("")
            item.setBackground(QColor(150, 150, 150))
        else:
            item.setText(processName)
            item.setBackground(color)

    def connectTable(self, inputFunc: Callable):
        self.memTable.itemClicked.connect(inputFunc)

class Separator(QFrame): # linha para separar elementos
    def __init__(self, orientation: str):
        super().__init__()

        if orientation == 'H':
            self.setFrameShape(QFrame.HLine)
        elif orientation == 'V':
            self.setFrameShape(QFrame.VLine)

        self.setFrameShadow(QFrame.Sunken)
