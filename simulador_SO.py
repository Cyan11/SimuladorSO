import decimal
import math
from typing import Any

# Classes abaixo são referentes à memória virtual/paginação


class ProcessData:
    def __init__(self, name, size, configuration):
        self.name = name
        self.size = size
        self.configuration = configuration

    def get_name(self):
        return self.name

    def get_size(self):
        return self.size


class PCB:
    def __init__(self):
        self.process_state = 'New'  # Inicializa o estado do processo como 'New' por padrão

    def get_state(self):
        return self.process_state  # Retorna o estado atual do processo

    def set_state(self, state):
        self.process_state = state  # Define o estado do processo


class Process:
    def __init__(self, name, state, sizeInInts, configuration):
        self.name = name
        self.state = state
        self.size = sizeInInts
        self.configuration = configuration
        # Cria as páginas do processo ao ser instanciado
        self.pageTable = self.createPages()

    def createPages(self):
        pt = PageTable()  # Inicializa a tabela de páginas
        amount_of_pages_needed = math.ceil(
            self.size / self.configuration.numberOfIntsPerFrame)
        # Calcula a quantidade de páginas necessárias para o processo

        print('\nCreating ' + str(amount_of_pages_needed) +
              ' pages for ' + self.name + '...')
        for i in range(amount_of_pages_needed):
            p = Page(self.configuration.numberOfIntsPerFrame,
                     self, i + 1)  # Cria uma nova página
            address = self.configuration.MP.allocatePage(
                p)  # Aloca a página na memória principal
            print('Allocated page at memory address ' + str(address))
            pt.insertPage(p, address)  # Insere a página na tabela de páginas
        print('\n<<Process ' + self.name + ' occupies a total of ' +
              str(amount_of_pages_needed) + ' frames>>')
        return pt  # Retorna a tabela de páginas do processo

    def endProcess(self):
        for p in self.pageTable.pageTable:
            pageFrame = self.pageTable.getFrame(p, config.MP)
            if not (pageFrame == None):  # (Se estava na MP )
                pageFrame.liberatePage()
                self.pageTable.removePageFromMP(p)
            else:
                self.config.MP.handlePageFaultById(p)
                # fazer código para remover em MS também


class Page:
    inMainMemory = False
    dirty = False #dirty verdadeiro se alguma operação se write é feita e página está na MP
                  #qdo a pagina sair da MP, este bit dirty indica se é nescessário reescrever o contéudo da página para a MS

    def __init__(self, _size, _process, _id):  # dado um array data and a int size
        self.size = _size
        self.process = _process
        # inicializa um array vazio com tamanho até _size
        self.data = [None]*_size
        self.id = _id

    def insertNewData(self, _data):  # on top of old data
        j = 0
        for i in range(len(self.data)):
            if (self.data[i] != None):
                self.data[i] = _data[j]
                j += 1
                if (j == len(_data)):
                    break

    def fillWithNewData(self, _data):  # on top of old data
        self.data = [None]*self.size
        for i in range(len(_data)):
            self.data[i] = _data[i]

    def toString(self):
        return (self.process.name + '-(' + str(self.id) + ')')
    
    def toStringFull(self):
        return (self.process.name + '-(' + str(self.id) + ')  ->Data: ' + str(self.data).replace('None','_').replace(',',''))


class PageTable:  # apge table é um dicionario que associa a página desejada a sua localização na MP
    def __init__(self):
        self.pages = []  # remover essa lista depois, pois a page table não guarda o contéudo das páginas em si
        self.pageTable = {}

    def insertPage(self, page, adress):
        self.pages.append(page)
        self.pageTable[page.id] = adress
        # essa linha adiciona uma entry no dicionario que associa
        # o id da página em questão ao seu adress na MP

    def changePageAdress(self, page, newAdress):
        self.pageTable[page.id] = newAdress

    def removePageFromMP(self, pageId):
        self.pageTable[pageId] = None

    def checkIfPageInMP(self, pageId):
        if (self.pageTable[pageId] == None):
            return False
        return True

    def get_MP_Adress_For_Page(self, pageId):
        return self.pageTable[pageId+1]

    def getFrame(self, pageId, MP):
        return MP.frames[(self.pageTable[pageId])]

    def getPage(self, pageId, MP):
        desiredPage = MP.frames[(self.pageTable[pageId])].page
        if(desiredPage == None):
            return MP.handlePageFaultById(pageId)
        else:
            return desiredPage

    def isPageInMemory(self, page_id):
        # Verifica se a página com o ID especificado está na memória principal.
        if self.pageTable.get(page_id) is not None:
            return True
        return False


class Frame:
    def __init__(self, sizeInInts, memAddress):
        self.page = None
        self.size = sizeInInts
        self.memoryAdress = memAddress

    def assignPage(self, _page):
        self.page = _page

    def liberatePage(self):
        self.page = None

    def isOccupied(self):
        if (self.page == None):
            return False
        return True


class Memory:
    def __init__(self, _size, _pageQuantity, _pageSizeInInts, _pageTable):
        # Inicialização da memória com parâmetros recebidos
        self.size = _size
        self.frames = []
        # Criação dos quadros de memória (frames)
        for i in range(_pageQuantity):
            self.frames.append(Frame(_pageSizeInInts, i))
        # Exibição de informações sobre a criação da memória
        print('Creating memory...')
        print('Size: '+str(len(self.frames)) + ' frames.')
        # Configuração de quantidade de páginas e tamanho por quadro
        self.pageQuantity = _pageQuantity
        self.pageSizeInInts = _pageSizeInInts
        # Referência para a tabela de páginas
        self.pageTable = _pageTable
        # Inicialização dos tempos de acesso para cada página como 0
        self.access_times = {}
        for frame in self.frames:
            if frame.page is not None:
                self.access_times[frame.page.id] = 0

    def allocatePage(self, p):
        # Exibição da alocação de uma página específica
        print('\nAllocating Page ' + p.toString() + '...')
        self.printMemoryStatus()

        # Contagem de quadros usados
        used_frames = sum(1 for frame in self.frames if frame.isOccupied())

        if used_frames == len(self.frames):
            # Memória está cheia, vamos tratar a criação de uma nova página

            # Verifica se a página já está na mp
            if p.inMainMemory:
                return  # Se a página já estiver na memória, não há necessidade de fazer nada

            # Cria uma nova página
            new_page = Page(self.pageSizeInInts, None, None)

            # Encontre um quadro livre na mp
            free_frame_address = self.findFreeFrameAndAssignPage(new_page)

            if free_frame_address is None:
                # Se não há espaço na mp, realiza a lógica de substituição LRU
                least_recently_used_page = self.findLeastRecentlyUsedPage()
                self.loadPageFromSecondaryMemory(
                    least_recently_used_page, new_page)
            else:
                # Atualiza os tempos de acesso para refletir a recente utilização da nova página
                self.access_times[new_page.id] = max(
                    self.access_times.values(), default=0) + 1
        else:
            # Se há espaço disponível na memória, procura um quadro livre ou trata a falta de página
            for frame in self.frames:
                if not frame.isOccupied():
                    # Quadro livre encontrado, atribui a página
                    print('Found a free frame!')
                    frame.assignPage(p)
                    p.inMainMemory = True
                    # Atualiza tempo de acesso se a página não estiver presente
                    if p.id not in self.access_times:
                        self.access_times[p.id] = 0
                    return frame.memoryAdress

            # Se não há quadros livres, trata a falta de página
            self.triggerPageFault(p)

    def triggerPageFault(self, p):
        # Verifica se a página não está na mp
        if not p.inMainMemory:
            # Imprime uma mensagem informando que a página não está na mp
            print(f'Page {p.toString()} is not in main memory.')
            # Chama a função para lidar com a falta de página
            self.handlePageFault(p)

    def handlePageFault(self, p):
        missing_page_id = p.id

        # Verifica se a página está ausente na mp utilizando a tabela de páginas
        if not self.pageTable.isPageInMemory(missing_page_id):
            print(f'Page {missing_page_id} is missing.')

            # Verifica e identifica a página menos recentemente utilizada (LRU)
            least_recently_used_page = self.findLeastRecentlyUsedPage()

            # Carrega a página da ms para a mp
            self.loadPageFromSecondaryMemory(least_recently_used_page, p)

    def handlePageFaultById(self, pageId):
        missing_page_id = pageId

        # Verifica se a página está ausente na mp utilizando a tabela de páginas
        if not self.pageTable.isPageInMemory(missing_page_id):
            print(f'Page {missing_page_id} is missing.')

            # Verifica e identifica a página menos recentemente utilizada (LRU)
            least_recently_used_page = self.findLeastRecentlyUsedPage()

            if(least_recently_used_page.dirty):
                print('Page is dirty, writing data to MS...')
            # Carrega a página da ms para a mp
            self.loadPageFromSecondaryMemory(
                least_recently_used_page, missing_page_id)

    def findLeastRecentlyUsedPage(self):
        # Encontra a página menos recentemente utilizada (LRU) usando o registro de tempo de acesso
        # Encontra a página que tem o menor tempo de acesso
        least_recently_used_page = min(
            self.access_times, key=self.access_times.get)
        # Retorna a página menos recentemente utilizada
        return least_recently_used_page

    def loadPageFromSecondaryMemory(self, new_page, another_arg):
        least_recently_used_page = self.findLeastRecentlyUsedPage()  # Encontra a página LRU

        if least_recently_used_page in self.access_times:
            # Remove a página LRU da MP e atualiza os tempos de acesso
            self.pageTable.removePageFromMP(least_recently_used_page)
            del self.access_times[least_recently_used_page]

        # Verifica se há espaço na mp para alocar a nova página
        free_frame_address = self.findFreeFrameAndAssignPage(new_page)
        if free_frame_address is None:
            # Se não há espaço na mp, realiza a lógica de substituição LRU
            least_recently_used_page = self.findLeastRecentlyUsedPage()
            self.loadPageFromSecondaryMemory(
                least_recently_used_page, new_page)
        else:
            # Atualiza os tempos de acesso para refletir a recente utilização da nova página
            self.access_times[new_page.id] = max(
                self.access_times.values(), default=0) + 1

    def findFreeFrameAndAssignPage(self, new_page):
        # Itera sobre os quadros na memória
        for frame in self.frames:
            # Verifica se o quadro não está ocupado
            if not frame.isOccupied():
                # Se encontrou um quadro livre, atribui a nova página a esse quadro
                print('Found a free frame!')
                frame.assignPage(new_page)
                # Marca a nova página como presente na memória principal
                new_page.inMainMemory = True
                # Retorna o endereço de memória do quadro que foi atribuído à nova página
                return frame.memoryAdress

    def printMemory(self):  # dá um display de como está a memória no momento atual
        print('\n Printing Memory:')
        i = 0
        for p in self.frames:
            i += 1
            if (p.isOccupied()):
                print(" --Frame " + str(i) + " holds page " + p.page.toStringFull())
            else:
                print(" --Frame " + str(i)+" holds no page")

    def printMemoryStatus(self):
        usedFrames = 0
        for p in self.frames:
            if (p.isOccupied()):
                usedFrames += 1
        print('Out of ' + str(len(self.frames)) +
              ' frames, '+str(usedFrames) + ' are used.')


class SecondaryMemory:
    def __init__(self, _size, _pageQuanitity, _pageSizeInInts):
        self.size = _size
        self.frames = []
        for i in range(_pageQuanitity):
            self.frames.append(Frame(_pageSizeInInts, i))
        print('Creating secondary memory...')
        print('Size: '+str(len(self.frames)) + ' frames.')
        self.pageQuantity = _pageQuanitity
        self.pageSizeInInts = _pageSizeInInts
        pageQuantity = self.size/self.pageSizeInInts

    def allocatePage(self, p):
        # versão que não funciona perfeitamente:
        for f in self.frames:
            if not (f.isOccupied()):
                # Nesse caso como é memoria secundaria nn deve mudar bit de presença na MP nem lugar na TP eu acho
                f.assignPage(p)
        # talvez tenha que ter um check pra garantir que um processo não é maior que a MS? algm ve isso dps

class ioDevice():
    def __init__(self,_id, _ioTime):
        self.id = _id
        self.completed = False
        self.ioTime = _ioTime
        print('Connecting device ' + str(self.id) +'...')

    def passTime(self):
        self.timeSinceLastIO +=1
        if(self.timeSinceLastIO > self.ioTime): #if has finished
            self.completed = True
            self.timeSinceLastIO = 0
            print('\nIO operation finished, so ' + self.tiedProcess.name + ' is now ready again!')
            self.tiedProcess.state = 'ready'
            for inst in self.tiedProcess.configuration.simulator.instructionBacklog:
                if(inst.process_name == self.tiedProcess.name): #Libera instruções do processo bloqueado (e manda p/ fila d prioridade)
                    self.tiedProcess.configuration.simulator.priorityInstructions.append(inst)
            
                if(inst.action == 'I'):
                    if(int(inst.args[0]) == self.id):
                        self.tiedProcess.configuration.simulator.priorityInstructions.append(inst)
                        self.tiedProcess.configuration.simulator.getProcess(inst.process_name).state = 'ready'

    def beginDeviceUse(self, process):
        print('Beggining use of device ' + str(self.id))
        self.tiedProcess = process
        self.timeSinceLastIO = 0
        self.completed = False


# Classes abaixo são referentes ao simulador/escalonador

class Simulator:  # classe 'principal' do sistema, que pega o input da professora e simula ele instrução por instrução
    # criando os respectivos processos, executando cada instrução, e td mais q um kernel deve ter q fzr

    def __init__(self, _configuration):
        self.PC = 0
        self.configuration = _configuration
        self.configuration.setSimulation(self)
        self.MP = _configuration.MP
        self.MS = _configuration.MS
        self.images = []
        self.ioDevices = []
        self.instructionBacklog = []
        self.priorityInstructions = []
        self.timeSinceStart = 0

    # percorre o arquivo linearmente, e para cada instrução, chama a função 'runInstruction' nela
    def simulate(self, input):
        self.PC = 0
        self.inputInsts = input
        while (self.PC < len(input.instructions)):
            # roda a instrução atual
            self.timeSinceStart+=1 #aumenta a variável referente ao tempo

            #if else de determinar se proxima instrução sera será da fila de prioridade ou não
            if(len(self.priorityInstructions) == 0):#se não for:
                print('\n Running instruction ' + self.inputInsts.instructions[self.PC].toString() )
                instructionBlocked = not self.runInstruction(self.inputInsts.instructions[self.PC])

                if not(instructionBlocked):
                 #após concluir u.t atual, atualiza os dispositivos para ver se algum IO acabou
                    self.passTimeForAllRunningDevices()
                else: #if instruction was blocked
                    self.instructionBacklog.append(self.inputInsts.instructions[self.PC])
                self.PC += 1
            else: #se for de prioridade (ou seja, uma instrução que havia sido bloqueada foi escolhida)
                print('\n Running instruction ' + self.priorityInstructions[0].toString() +' with priority.')
                instructionBlocked = not self.runInstruction(self.priorityInstructions[0])
                temp = self.priorityInstructions.remove(self.priorityInstructions[0])
                if not(instructionBlocked):
                #após concluir u.t atual, atualiza os dispositivos para ver se algum IO acabou
                    self.instructionBacklog.remove(temp)
                    self.passTimeForAllRunningDevices()
                else: #if instruction was blocked
                    self.instructionBacklog.append(temp)
        if(len(self.instructionBacklog)+len(self.priorityInstructions)>0): #se ainda falta instruções pra executar qdo normalmente teria acabado
            print('\n---No ready processes to execute---')
            print('---OS on hold while waiting for I/O to finish.---\n')
            self.passTimeForAllRunningDevices()
            newInput = []
            for ins in self.priorityInstructions:
                newInput.append(ins)
            for ins in self.instructionBacklog:
                if(ins not in newInput):    
                    newInput.append(ins)
            self.priorityInstructions = []
            self.instructionBacklog = []
            inp = Input(newInput)
            print('Instructions still waiting to finish: ' + inp.toString())
            self.simulate(inp) #re inicia a função de simulação só com as que faltam executar
    
    def passTimeForAllRunningDevices(self):
        for device in self.ioDevices:
            if not(device.completed):
                device.passTime()
    def runInstruction(self, instruction):  # código que processa cada instrução

        # Toda instrução do input é dividida em várias partes no exemplo dela,  (e aq uso o split para separa-las)
        # com a primeira parte sendo qual o processo que a instrução faz parte
        # a segunda parte sendo qual o name da instrução
        # e a terceira e/ou quarta complementos a instrução, com função determinada pela instrução executada
        # (por exemplo, uma instr de escrita no P1 tem partes ['P1','W','address da escrita','o que será escrito'])

        correspondingProcess = self.getProcess(instruction.process_name)
        correspondingInstruction = instruction.action

        if (correspondingInstruction == 'C'):  # o código de cada instrução pode estar aqui
            self.createProcess(instruction.process_name, instruction.args[0])
        else:
            # coloca o processo no estado 'executando' se não bloqueado
            
            if correspondingProcess.state == 'blocked' or correspondingProcess.state == 'suspended':
                print(' '+ instruction.toString() + ' was put on hold due to process being blocked due to I/O operation.' )
                return False
            self.executeProcess(correspondingProcess)

        # Aqui, o código verifica qual instrução é, e executa a função da instrução em questão
        # Provavelmente seria melhor fzr com um switch-case, mas 6 ifs tbm servem por emqto

        if (correspondingInstruction == 'R'):  # o código de cada instrução pode estar aqui
            self.readFromMemory(correspondingProcess, instruction.args[0])
        elif (correspondingInstruction == 'W'):  # o código de cada instrução pode estar aqui
            self.writeToMemory(correspondingProcess,
                               instruction.args[0],instruction.args[1])
        elif (correspondingInstruction == 'P'):  # o código de cada instrução pode estar aqui
            self.runCPUinst(correspondingProcess, instruction.args[0])
        elif (correspondingInstruction == 'I'):  # o código de cada instrução pode estar aqui
            deviceId = instruction.args[0]
            for device in self.ioDevices: #testa se dispostivo que quer acessar já está em uso
                if(device.id == int(deviceId) and not device.completed): #e bloquea a instrução se estiver
                    print(' '+ instruction.toString() + ' was put on hold due to device being on use already. Corresponding process now blocked.' )
                    correspondingProcess.state = 'blocked'
                    return False
            self.runIOinst(correspondingProcess, instruction.args[0])
        elif (correspondingInstruction == 'T'):  # o código de cada instrução pode estar aqui
            self.endProcess(correspondingProcess)

        return True

    def getProcess(self, processname):  # tenho q atualizar
        for process in self.images:
            if (process.name == processname):
                return process
        print(' Process not found in memory yet.')
        return None

    # Funções a seguir são chamadas para executar cada instrução do input, como tá lá no docs da profa
    def createProcess(self, processName, desiredSize):  # instrução C
        print(' Creating new process...')
        # processo de alocaçõa é feito automaticamente na criação de um objeto Process()
        p = Process(processName, 'New', int(desiredSize), self.configuration)
        self.images.append(p)

    def readFromMemory(self, process, virtualAddress):  # instrução R
        print(' Reading from memory at virtual address',
              virtualAddress, "by process", process.name, "...")
        pageNo = int(virtualAddress)//self.configuration.numberOfIntsPerFrame
        offset = int(virtualAddress)%self.configuration.numberOfIntsPerFrame
        print(' Data found at page ' + process.name + '-(' + str(pageNo+1) +"), with offset " + str(offset))
        page = process.pageTable.getPage(pageNo+1, self.configuration.MP)
        if(page!=None):
            print(' Page found in MP: ' + page.toString())
            requestedData = page.data[offset] 
            print(' Requested data is: <<' + str(requestedData) +'>>')
        else:
            print('Page fault')
            self.configuration.MP.triggerPageFaultById(pageNo,self.configuration.MP) #acho que ainda não funciona muito bem isso
            
    def writeToMemory(self, process, virtualAddress, data):  # instrução W
        print(" Writing", data, "to memory at virtual address",
              virtualAddress, "by process", process.name, "...")
        pageNo = int(virtualAddress)//self.configuration.numberOfIntsPerFrame
        offset = int(virtualAddress)%self.configuration.numberOfIntsPerFrame
        print(' Data found at page ' + process.name + '-(' + str(pageNo+1) +"), with offset " + str(offset))
        page = process.pageTable.getPage(pageNo+1, self.configuration.MP)
        if(page!=None):
            page.dirty = True
            page.data[offset] = int(data)
            print(' Page found in MP: ' + page.toString()) 
            print(' Performing write operation in that adress...')
            print(' Write operation in virtual adress ' + str(virtualAddress) + ' finished. Page is now "Dirty"')
        else:
            print('Page fault')
            self.configuration.MP.triggerPageFaultById(pageNo,self.configuration.MP)

    def runCPUinst(self, process, virtualAddress):  # instrução P
        print(' Running CPU instruction at virtual adress',
              virtualAddress, "by process", process.name, "...")
        pageNo = int(virtualAddress)//self.configuration.numberOfIntsPerFrame
        offset = int(virtualAddress)%self.configuration.numberOfIntsPerFrame
        print(' Data found at page ' + process.name + '-(' + str(pageNo+1) +"), with offset " + str(offset))
        page = process.pageTable.getPage(pageNo+1, self.configuration.MP)
        if(page!=None):
            print(' Page found in MP: ' + page.toString()) 
            print(' Performing CPU operation in that adress...')
            print(' CPU operation in virtual adress...' + str(virtualAddress) + ' finished.')
        else:
            print('Page fault')
            self.configuration.MP.triggerPageFaultById(pageNo,self.configuration.MP)

    def runIOinst(self, process, deviceId):  # instrução I
        print(' Running I/O instruction at device',
              deviceId, "by process", process.name, "...")
        print(' Process '+process.name +' has been blocked until device ' + str(deviceId) + ' finishes I/O. Should last 3 u.t')
        self.blockProcess(process)
        deviceExists = False #código que verifica se dispostivo já existe
        for device in self.ioDevices:
            if(device.id == int(deviceId)):
                deviceExists = True
                targetDevice = device 
        if(deviceExists):
            targetDevice.beginDeviceUse(process)
        else:
            targetDevice = ioDevice(int(deviceId),self.configuration.averageIOTime)
            targetDevice.beginDeviceUse(process)
            self.ioDevices.append(targetDevice)
        # temos também que criar alguma coisa relacionada ao dma provavelmente

    def endProcess(self, process):  # instrução T
        self.images.remove(process)
        process.endProcess()
        print(' Ending Process', process.name)

    # funções a seguir servem para mudar o estado de processo, de acordo com aquele diagrama d estados lá
    def blockProcess(self, process):
        process.state = 'blocked'
        # fazer código para ativar DMA ou alguma coisa assim?

    def suspendProcess(self, process):
        process.state = 'blocked'
        # seguindo a logica do endprocess para retirar da mp
        for p in self.pageTable.pageTable:
            pageFrame = self.pageTable.getFrame(p, config.MP)
            if not (pageFrame == None): 
                pageFrame.liberatePage()
                self.pageTable.removePageFromMP(p)

    def executeProcess(self, process):
        for p in self.images:
            if (p.state == 'executing'):  # assumindo aqui que sistema tem só 1 processador
                p.state = 'ready'  # e que só tem, em um dado momento, 1 processo executando
        process.state = 'executing'  # mas tem grande chance disso tar errado, ent sla

    def getProcess(self, processname): # função q pega o nome de um processo e busca os dados do processo 
        for process in self.images:
            if (process.name == processname):
                return process
        print(' Process not found in memory!')
        return None


class Input:
    def __init__(self, _instructions):
        self.instructions = _instructions

    def toString(self):
        s = ''
        for i in self.instructions:
            s+= i.toString() + '; '
        return s

class Configuration:

    
    def __init__(self, _memorySizeInInts, _numberOfFramesInMemory, _secondaryMemoryScalingFactor):
        self.memorySizeInInts = _memorySizeInInts
        self.numberOfFramesInMemory = _numberOfFramesInMemory
        self.averageIOTime = 3 #in u.t
        self.logicalAdressSize = 1 #In this case, means one int. It could be less or more though, but one makes it more convenient.
        self.numberOfIntsPerFrame = math.ceil(
            _memorySizeInInts/_numberOfFramesInMemory)  # arrendonda pra cima

        self.pageTable = PageTable()  # Aqui você instancia a tabela de páginas
        self.MP = Memory(_memorySizeInInts, _numberOfFramesInMemory,
                         self.numberOfIntsPerFrame, self.pageTable)

        self.MS = SecondaryMemory(_memorySizeInInts*_secondaryMemoryScalingFactor,
                                  _numberOfFramesInMemory*_secondaryMemoryScalingFactor, self.numberOfIntsPerFrame)

    def setSimulation(self, _simulator):
        self.simulator = _simulator


class Instruction:
    def __init__(self, process_name, action, *args):
        self.process_name = process_name
        self.action = action
        self.args = args

    def toString(self):
        s=  self.process_name + ' ' + self.action 
        for k in self.args:
            s+= ' ' + k
        return s


class FileReader:
    def readInputFromFile(self, encoding='utf-16'):
        instructions = []

        try:
            # Abre o arquivo no caminho especificado
            with open(self.filePath, 'r') as file:
                # Lê todas as linhas do arquivo
                lines = file.readlines()

                # Para cada linha no arquivo
                for line in lines:
                    # Divide a linha em partes com base nos espaços em branco
                    parts = line.strip().split(' ')
                    if len(parts) >= 2:
                        # Extrai as partes da instrução
                        process_name = parts[0]
                        action = parts[1]
                        args = parts[2:] if len(parts) > 2 else []
                        # Cria uma instância de Instruction com os dados extraídos
                        instruction = Instruction(process_name, action, *args)
                        instructions.append(instruction)
                    else:
                        # Se o formato da instrução for inválido, imprime uma mensagem de erro
                        print("Invalid instruction format:", line)

        except FileNotFoundError:
            # Se o arquivo não for encontrado, imprime uma mensagem de erro
            print("File not found:", self.filePath)

        return Input(instructions)

    def __init__(self):
        # Caminho do arquivo, relativo ao diretório atual onde o script está sendo executado
        self.filePath = 'input.txt'

    def printInput(self, instrucoes):
        # Exibindo as instruções lidas
        for instrucao in instrucoes:
            print("Processo:" + instrucao.process_name + ", Ação:" +
                  instrucao.action + " Argumentos: " + instrucao.args)


config = Configuration(128, 16, 8)
print('\nMP Size In Ints: ' + str(config.MP.size) + ' Ints')
print('Amount of Frames In MP: ' + str(config.MP.pageQuantity) + ' Frames')
print('Size of a Page: '+str(config.MP.frames[0].size) + ' Ints')


def runPagingTest():
    p1 = Process('P1', 'New', 16, config)
    p2 = Process('P2', 'New', 16, config)
    p3 = Process('P3', 'New', 17, config)
    p3 = Process('P4', 'New', 32, config)
    p3 = Process('P5', 'New', 32, config)
    p3 = Process('P6', 'New', 8, config)
    p2.endProcess()
    p3 = Process('P7', 'New', 8, config)
    p3 = Process('P8', 'New', 8, config)
    #p3 = Process('P9', 'New', 8, config)
    config.MP.printMemory()
    print('\nPaging/Virtual Memory test concluded succesfully.\n\n---\n')

def runSimulatorTest():
    print('Beggining Simulator test.\n')
    #inputInstructions = Input([Instruction('P1','C','32'),Instruction('P2','C','64'),Instruction('P3','C','16'),Instruction('P1','R','31')])
    simulator = Simulator(config)
    fileReader = FileReader()
    inputInstructions = fileReader.readInputFromFile()
    print('Chosen Instructions:', inputInstructions.toString(), '\n')
    simulator.simulate(inputInstructions)
    config.MP.printMemory()
    config.MP.printMemoryStatus()
    print('\nSimulator test concluded succesfully.\n\n---\n')

#Testes do sistema:
#runPagingTest()  # Rodem um teste ou outro, mas nn os dois pfvr
runSimulatorTest()

