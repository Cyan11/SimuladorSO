import sys
from enum import Enum, auto
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from CustomWidgets import *

class InterfaceMessage():
    """Mensagem p/ o controlador com informações sobre mudanças na interface
    \n Criar instância e depois preencher as variáveis necessarias"""
    class Flag(Enum):
        COMMAND = auto()
        CONFIG_CHANGE = auto()
                             
    def __init__(self, MESSAGE_TYPE: Flag):
        self.MESSAGE_TYPE = MESSAGE_TYPE

        # possíveis informações a serem passadas
        self.command: str = None #caso de COMMAND
        self.pri_size: int = None #caso de CONFIG_CHANGE
        self.sec_size: int = None #caso de CONFIG_CHANGE
        self.page_size: int = None #caso de CONFIG_CHANGE
        self.log_add_size: int = None #caso de CONFIG_CHANGE

class Snapshot():
  """Info sobre o simulador durante um instante de tempo"""
  def __init__(self, listaProcessos: list[ProcessInfo], statusText: str):
    self.listaProcessos = listaProcessos
    self.statusText = statusText

class MainWindow(QMainWindow):
    """Janela que contém o aplicativo"""
    def __init__(self, PRI_SIZE, SEC_SIZE, PAGE_SIZE, ADD_SIZE):
        super(MainWindow, self).__init__()

        self.ADD_SIZE = ADD_SIZE
        self.PAGE_SIZE = PAGE_SIZE
        self.SEC_SIZE = SEC_SIZE
        self.SEC_PAGES = self.SEC_SIZE // self.PAGE_SIZE
        self.PRI_SIZE = PRI_SIZE
        self.PRI_PAGES = self.PRI_SIZE // self.PAGE_SIZE

        #TODO: implementar abertura de arquivos e salvar comandos
        self.directory = "./arquivos"
        self.commands: list[str] = []
        
        # contém informações sobre os processos em memória
        self.processes: list[ProcessInfo] = []

        # histórico com cada momento da simulação (cada Snapshot tem info de uma mudança feita)
        self.snapshots: list[Snapshot] = []
        self.currentSnapshotIndex: int = 0
        self.snapshots.append(Snapshot(self.processes, "")) #snapshot inicial sem nada na memória

        # funcao utilizada pelo Controlador quando ocorre um evento na interface
        self.eventFunction = None

        self.setWindowTitle("Simulador de Memória Virtual (com paginação)")
        self.setStyleSheet("""
        #menuWidget {
            background: rgb(229, 230, 231);
        }
        .button {
            margin: 0;
            padding: 0;
        }
        """)

        # INFORMAÇÃO BÁSICA
        # cada QBoxLayout é uma caixa que armazena componentes (botões, texto, outros Layouts) em uma estrutura específica
        # cada QWidget é um componente interativo que faz algo (botão, caixa de texto, tabela) ou pode armazenar outros Widgets (.addWidget)
        # QWidget e QLayout são praticamente a mesma coisa (Layout: + fácil de organizar a estrutura | Widget: + fácil de customizar)
        # é possível conectar uma ação de um widget (ex: aperto de um botão) a uma função com .connect(nomeFuncao)
        mainLayout = QHBoxLayout()

        visual = QHBoxLayout()
        visualWidget = QWidget(objectName="visualWidget")
        visualWidget.setLayout(visual)

        menu = QHBoxLayout()
        menuWidget = QWidget(objectName="menuWidget")
        menuWidget.setLayout(menu)
        menuWidget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)

        mainLayout.addWidget(visualWidget)
        mainLayout.addWidget(menuWidget)

        menuColLeft = QVBoxLayout()
        menuColLeft.setAlignment(Qt.AlignTop)
        menuColRight = QVBoxLayout()
        menuColRight.setAlignment(Qt.AlignTop)

        menu.addLayout(menuColLeft)
        menu.addWidget(Separator("V"))
        menu.addLayout(menuColRight)
        menu.setAlignment(Qt.AlignJustify)
        menu.setSpacing(10)

        menuControlButtons = QVBoxLayout()
        menuSelectFile = QVBoxLayout()
        menuCommandViewer = QVBoxLayout()
        menuSettings = QVBoxLayout()
        processInfoWindow = QVBoxLayout()
        menuStatusWindow = QVBoxLayout()

        menuColLeft.addLayout(menuControlButtons)
        menuColLeft.addWidget(Separator("H"))
        menuColLeft.addLayout(menuSelectFile)
        menuColLeft.addWidget(Separator("H"))
        menuColLeft.addLayout(menuCommandViewer)
        menuColRight.addLayout(menuSettings)
        menuColRight.addWidget(Separator("H"))
        menuColRight.addLayout(processInfoWindow)
        menuColRight.addWidget(Separator("H"))
        menuColRight.addLayout(menuStatusWindow)

        self.visualSM = QVBoxLayout()
        self.visualPM = QVBoxLayout()
        self.visualSM.setAlignment(Qt.AlignTop)
        self.visualPM.setAlignment(Qt.AlignTop)

        visual.addLayout(self.visualSM)
        visual.addWidget(Separator("V"))
        visual.addLayout(self.visualPM)
        visual.setAlignment(Qt.AlignCenter)

        # BOTÕES DE CONTROLE DE EXECUÇÃO
        self.controlButtons = ControlButtonsWidget()
        self.controlButtons.connectButtons(self.loadLastSnapshot, self.onPlayBtnPress, self.loadNextSnapshot) # quando os botões são pressionados, chama essas funções
        menuControlButtons.addWidget(self.controlButtons)

        # SELECIONAR ARQUIVOS
        self.fileSelector = FileSelectorWidget("Selecione o arquivo")
        self.fileSelector.getFiles(self.directory)
        self.fileSelector.connectButton(self.openFile)
        menuSelectFile.addWidget(self.fileSelector)

        # CONFIGURAÇÕES DA MEMÓRIA
        self.settingsMenu = SettingsMenu()
        self.settingsMenu.connectButtons(self.onCancelBtnClick, self.onSaveBtnClick) # quando os botões são pressionados, chama essas funções
        menuSettings.addWidget(self.settingsMenu)
        self.onCancelBtnClick() # escreve as configurações nos inputs

        # MINI TERMINAL
        self.commandTerminal = TerminalWidget()
        self.commandTerminal.connectInput(self.onInputEnter) # quando ENTER é pressionado na entrada, chama readInput()
        menuCommandViewer.addWidget(self.commandTerminal)

        # JANELA DE STATUS
        self.processInfoWindow = ProcessInfoWindowWidget("Info do Processo")
        processInfoWindow.addWidget(self.processInfoWindow)

        # JANELA DE ATUALIZAÇÕES
        self.statusWindow = StatusWindowWidget("Status do Simulador")
        menuStatusWindow.addWidget(self.statusWindow)

        # MEMORIA
        self.TAM_LINHA = 30
        self.secMem = MemoryTableWidget("MS", self.SEC_PAGES, self.PAGE_SIZE, self.TAM_LINHA)
        self.priMem = MemoryTableWidget("MP", self.PRI_PAGES, self.PAGE_SIZE, self.TAM_LINHA)
        self.secMem.connectTable(self.onItemClicked)
        self.priMem.connectTable(self.onItemClicked)

        self.visualSM.addWidget(self.secMem)
        self.visualPM.addWidget(self.priMem)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)
    

    def resetInterface(self):
        """Limpa a interface e cria nova memória"""
        self.secMem.setVisible(False)
        self.priMem.setVisible(False)
        self.visualSM.removeWidget(self.secMem)
        self.visualPM.removeWidget(self.priMem)
        self.secMem = MemoryTableWidget("MS", self.SEC_PAGES, self.PAGE_SIZE, self.TAM_LINHA)
        self.priMem = MemoryTableWidget("MP", self.PRI_PAGES, self.PAGE_SIZE, self.TAM_LINHA)
        self.secMem.connectTable(self.onItemClicked)
        self.priMem.connectTable(self.onItemClicked)
        self.visualSM.addWidget(self.secMem)
        self.visualPM.addWidget(self.priMem)

        self.processes = [] # limpa as informações sobre os processos
        self.snapshots = [] # reseta o histórico
        self.currentSnapshotIndex = 0
        self.snapshots.append(Snapshot(self.processes, ""))

        self.commandTerminal.resetWindow()
        self.updateStatusWindow("")

    def updateMemory(self):
        """Atualiza as memórias com páginas dos processos"""
        for i in range(self.SEC_PAGES):
            self.secMem.updatePage(i)
        for i in range(self.PRI_PAGES):
            self.priMem.updatePage(i)

        for p in self.processes:
            for i in range(len(p.pageTableMS)):
                self.secMem.updatePage(p.pageTableMS[i].value, f"{p.name} ({i})", p.color)

            for i in range(len(p.pageTableMP)):
                self.priMem.updatePage(p.pageTableMP[i].value, f"{p.name} ({i})", p.color)        

    def onInputEnter(self):
        """Chamada quando um comando é enviado no terminal"""
        command = self.commandTerminal.inputBar.text()
        parts = command.split(" ")
        if 1 < len(parts) <= 4 and parts[1] in {'P','I','C','R','W','T'}: # checa se o formato está correto
            self.commandTerminal.inputBar.clear()
            self.execCommand(command)
        else:
            self.commandTerminal.inputBar.setText(command)
    
    def onCancelBtnClick(self):
        """Chamada quando o botão de cancelar nas configurações é pressionado"""
        self.settingsMenu.setValues(self.PRI_SIZE, self.SEC_SIZE, self.PAGE_SIZE, self.ADD_SIZE)

    def onSaveBtnClick(self):
        """Chamada quando o botão de salvar nas configurações é pressionado
        \n Atualiza variáveis de configuração com valores das entradas
        \n Envia mensagem para o Controlador"""
        self.PRI_SIZE = self.settingsMenu.tam_mp_input.getValue()
        self.SEC_SIZE = self.settingsMenu.tam_ms_input.getValue()
        self.PAGE_SIZE = self.settingsMenu.tam_pag_input.getValue()
        self.ADD_SIZE = self.settingsMenu.tam_end_input.getValue()
        self.SEC_PAGES = self.SEC_SIZE // self.PAGE_SIZE
        self.PRI_PAGES = self.PRI_SIZE // self.PAGE_SIZE
        self.settingsMenu.setValues(self.PRI_SIZE, self.SEC_SIZE, self.PAGE_SIZE, self.ADD_SIZE)
        
        msg = InterfaceMessage(InterfaceMessage.Flag.CONFIG_CHANGE)
        msg.pri_size = self.PRI_SIZE
        msg.sec_size = self.SEC_SIZE
        msg.page_size = self.PAGE_SIZE
        msg.log_add_size = self.ADD_SIZE
        self.sendMessage(msg)

    def connectFunction(self, function: Callable) -> None:
        self.eventFunction = function

    def sendMessage(self, message: InterfaceMessage) -> None:
        if (self.eventFunction != None): self.eventFunction(message)

    def onItemClicked(self, item: QTableWidgetItem):
        """Chamada quando item na memória é clicado
        \n Acha o processo naquele quadro e atualiza janela de info do processo"""
        processName = item.text().split(" ")[0]
        processInfo = None
        for p in self.processes:
            if p.name == processName: processInfo = p

        if (processInfo == None):
            self.processInfoWindow.clear()
        else:
            self.processInfoWindow.update(processInfo)

    def isProcessInProcessInfoList(self, pName: str) -> int:
        """Retorna o índice de onde está o processo caso exista, -1 caso contrário"""
        for i,p in enumerate(self.processes):
            if p.name == pName: return i
        return -1

    def updateStatusWindow(self, text: str):
        """Atualiza janela com status do simulador"""
        self.statusWindow.update(text)

    def execCommand(self, command: str):
        parts = command.split(" ")
        if not(1 < len(parts) <= 4 and parts[1] in {'P','I','C','R','W','T'}): # checa se o formato está correto
            return
        self.commandTerminal.appendCommand(command)
        self.commandTerminal.highlightCommand(command)

        msg = InterfaceMessage(InterfaceMessage.Flag.COMMAND)
        msg.command = command
        self.sendMessage(msg)

    #funcoes pros botões de voltar, tocar, e avançar
    def loadLastSnapshot(self):
        if self.currentSnapshotIndex > 0:
            self.currentSnapshotIndex -= 1
            self.loadSnapshot(self.snapshots[self.currentSnapshotIndex])
            self.commandTerminal.highlightLast()

    def loadNextSnapshot(self):
        if self.currentSnapshotIndex < len(self.snapshots)-1:
            self.currentSnapshotIndex += 1
            self.loadSnapshot(self.snapshots[self.currentSnapshotIndex])
            self.commandTerminal.highlightNext()
        
        elif len(self.commands) > 0:
            self.execCommand(self.commands.pop(0))

    def onPlayBtnPress(self):
        while (self.currentSnapshotIndex < len(self.snapshots)-1) or len(self.commands) > 0:
            self.loadNextSnapshot()

    def updateProcessInfoList(self, newList: list[ProcessInfo]):
        for el in newList:
            index = self.isProcessInProcessInfoList(el.name)
            if index != -1: el.color = self.processes[index].color
        self.processes = newList

    def loadSnapshot(self, snapshot: Snapshot):
        index = -1
        for i,sn in enumerate(self.snapshots):
            if (sn == snapshot): index = i
        if (index == -1): 
            print("Erro: Snapshot não está no histórico.")
            return
        self.currentSnapshotIndex = index

        #atualizar lista de processInfo
        self.updateProcessInfoList(snapshot.listaProcessos)
        #atualizar memoria e janela de status
        self.updateMemory()
        self.updateStatusWindow(snapshot.statusText)
        self.processInfoWindow.clear()

    def recordSnapshot(self, snapshot: Snapshot):
        self.snapshots.append(snapshot)
        self.currentSnapshotIndex = len(self.snapshots) - 1 # o atual é o ultimo colocado

    def openFile(self):
        with open(f"{self.directory}/{self.fileSelector.getSelectedText()}", "r") as file:
            self.commands = [line.strip() for line in file]
        self.resetInterface()

#app = QApplication(sys.argv)

#window = MainWindow()
#window.show()

#app.exec_()