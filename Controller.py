import sys
from enum import Enum, auto
from UserInterface import MainWindow, InterfaceMessage, Snapshot, ProcessInfo
from simulador_SO import Simulator, Configuration, Process#, SimulatorMessage
from PySide6.QtWidgets import QApplication

#deve ser implementada no simulador
class SimulatorMessage():
  """Mensagem p/ o controlador com informações sobre atualizações no simulador
  \n Criar instância e depois preencher as variáveis necessarias"""
  class Flag(Enum):
    EXECUTION = auto()
    IO = auto()
    CREATION = auto()
    READ = auto()
    WRITE = auto()
    TERMINATION = auto()
    INVALID = auto()

  def __init__(self, MESSAGE_FLAG: Flag, listaProcessos: list[Process], processoAlterado: Process):
    self.MESSAGE_FLAG = MESSAGE_FLAG
    self.processoAlterado = processoAlterado
    # lista com informação sobre cada processo
    # p/ cada processo: tabela de págs. da MP e MS, nome, estado, tamanho
    self.listaProcessos = listaProcessos

    # possíveis informações a serem passadas
    self.faltaDePagina: bool = False #caso de EXECUTION, READ ou WRITE
    self.enderecoAcessado: int = None #caso de EXECUTION, READ ou WRITE
    self.instrucaoExecutada: str = None #caso de EXECUTION
    self.valorLido: int = None #caso de READ
    self.valorEscrito: int = None #caso de WRITE
    self.dispositivo: str = None #caso de IO
    self.tamanhoEmString: str = None #caso de CREATION
    self.invalidMessage: str = None #caso de INVALID


class Controller():
  def __init__(self):
    self.ADD_SIZE = 512
    self.PAGE_SIZE = 128
    self.SEC_SIZE = 2048
    self.SEC_PAGES = self.SEC_SIZE // self.PAGE_SIZE
    self.PRI_SIZE = 512
    self.PRI_PAGES = self.PRI_SIZE // self.PAGE_SIZE

    self.config = Configuration(self.PRI_SIZE, self.PRI_PAGES, self.SEC_SIZE)
    self.sim = Simulator(self.config)

    self.app = QApplication(sys.argv)
    self.window = MainWindow(self.PRI_SIZE, self.SEC_SIZE, self.PAGE_SIZE, self.ADD_SIZE)

    self.window.connectFunction(self.interfaceEvent)
    #self.sim.connectFunction(self.simulatorEvent)
    
    
  def interfaceEvent(self, msg: InterfaceMessage):
    """
    - Chamada quando ocorre um evento na interface (ex: nova config. salva).
    - Recebe uma mensagem com informações sobre a mudança na interface.
    - O controlador passa as mudanças para o Simulador.
    """
    if (msg.MESSAGE_TYPE == InterfaceMessage.Flag.COMMAND):
      #TODO: teste da função, apagar depois, ela é chamada somente pelo simulador
      #self.sim.runInstruction(msg.command)
      self.simulatorEvent(None)

    # na mudança de configuração, cria outro Simulador e reseta a interface
    elif (msg.MESSAGE_TYPE == InterfaceMessage.Flag.CONFIG_CHANGE):
      self.ADD_SIZE = msg.log_add_size
      self.PAGE_SIZE = msg.page_size
      self.SEC_SIZE = msg.sec_size
      self.SEC_PAGES = self.SEC_SIZE // self.PAGE_SIZE
      self.PRI_SIZE = msg.pri_size
      self.PRI_PAGES = self.PRI_SIZE // self.PAGE_SIZE

      self.config = Configuration(self.PRI_SIZE, self.PRI_PAGES, self.SEC_SIZE)
      self.sim = Simulator(self.config)
      self.sim.connectFunction(self.simulatorEvent)

      self.window.resetInterface()

    else:
      print("Error: Invalid message.")


  def simulatorEvent(self, msg: SimulatorMessage):
    """
    - Chamada quando o simulador é atualizado.
    - Recebe uma mensagem com informações sobre a mudança no simulador.
    - O controlador passa as mudanças para a interface.
    """

    #TODO: teste, apagar depois
    plist = []
    plist.append(ProcessInfo("P1", "Executando",64, ["0 0 0","0 0 1","0 0 2","0 0 3"], ["0 0 0","0 0 1","0 0 3"]))
    plist.append(ProcessInfo("P2", "Pronto",64, ["0 0 4","0 0 5"], ["0 0 2"]))
    plist.append(ProcessInfo("P3", "Bloqueado",64, ["0 0 6","0 0 7","0 0 8"], []))
    snapshot = Snapshot(plist, f"Processo P1 sofreu falta de página ao tentar acessar o endereço 1000. A página será pega na memória secundária.\n\nProcesso P1 escreveu o valor '100' no endereço 1000.")
    self.window.recordSnapshot(snapshot)
    self.window.loadSnapshot(snapshot) #aplica alteração mais recente
    return
    '''
    #atualizar lista de processInfo
    newList: list[ProcessInfo] = []
    for process in msg.listaProcessos:
      processInfo = ProcessInfo(process.name, process.state, process.pageTable, process.pageTable)
      newList.append(processInfo)

    #atualizar janela de status com mensagem sobre o que ocorreu
    text: str = ""
    if (msg.MESSAGE_FLAG == SimulatorMessage.Flag.INVALID):
      text = f"Comando inválido: {msg.invalidMessage}"

    elif (msg.MESSAGE_FLAG == SimulatorMessage.Flag.CREATION):
      text = f"Processo {msg.processoAlterado.name} foi criado.\nTamanho: {msg.tamanhoEmString}"

    elif (msg.MESSAGE_FLAG == SimulatorMessage.Flag.IO):
      text = f"Processo {msg.processoAlterado.name} iniciou uma operação de E/S em {msg.dispositivo}. \n\nO processo passou para o estado {msg.processoAlterado.state}"

    elif (msg.MESSAGE_FLAG == SimulatorMessage.Flag.TERMINATION):
      text = f"Processo {msg.processoAlterado.name} foi terminado."

    elif (msg.MESSAGE_FLAG == SimulatorMessage.Flag.EXECUTION):
      if (msg.faltaDePagina): text += f"Processo {msg.processoAlterado.name} sofreu falta de página ao tentar acessar o endereço {msg.enderecoAcessado}. A página será pega na memória secundária."
      text += f"\n\nProcesso {msg.processoAlterado.name} acessou o endereço {msg.enderecoAcessado} e executou a instrução '{msg.instrucaoExecutada}'"
    
    elif (msg.MESSAGE_FLAG == SimulatorMessage.Flag.READ):
      if (msg.faltaDePagina): text += f"Processo {msg.processoAlterado.name} sofreu falta de página ao tentar acessar o endereço {msg.enderecoAcessado}. A página será pega na memória secundária."
      text += f"\n\nProcesso {msg.processoAlterado.name} leu o valor '{msg.valorLido} do endereço {msg.enderecoAcessado}."
    
    elif (msg.MESSAGE_FLAG == SimulatorMessage.Flag.EXECUTION):
      if (msg.faltaDePagina): text += f"Processo {msg.processoAlterado.name} sofreu falta de página ao tentar acessar o endereço {msg.enderecoAcessado}. A página será pega na memória secundária."
      text += f"\n\nProcesso {msg.processoAlterado.name} escreveu o valor '{msg.valorEscrito}' no endereço {msg.enderecoAcessado}."

    else:
      print("Error: Invalid message.")

    #salva as alterações no histórico
    snapshot = Snapshot(newList, text)
    self.window.recordSnapshot(snapshot)
    self.window.loadSnapshot(snapshot) #aplica alteração mais recente
    '''

controller = Controller()
controller.window.show()

controller.app.exec_()
