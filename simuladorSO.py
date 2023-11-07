import math

class Process: #no momento o código, os dados e o 'PCB' tão todos juntos aqui, mas provavelmente faz sentido separar dps
    def __init__(self, _name, _state):
        self.name = _name
        self.data = []
        self.state = _state

class Memory: #memoria por emqto é só uma lista de processos com tamanho finito
    def __init__(self, _size):
        self.size = _size
        self.images = []

    def addProcess(self,p): #adiciona um processo novo à memória
        if(len(self.images)<=self.size):
            self.images.append(p)
        else:
            print('Not enough space in memory!')
            #E provavelmente agente vai ter que fazer alguma coisa de paginação aq,
            #tipo colocar o algoritmo d substituição
   
    def printMemory(self): #dá um display de como está a memória no momento atual
        print(' Printing Memory:')
        for p in self.images:
            print("",p.name) 
    

class Simulator: #classe 'principal' do sistema, que pega o input da professora e simula ele instrução por instrução
                 #criando os respectivos processos, executando cada instrução, e td mais q um kernel deve ter q fzr

    def __init__(self, mainMemory):
        self.PC = 0
        self.MP = mainMemory

    def simulate(self,input):
        while(self.PC<len(input.instructions)):
            self.runInstruction(input.instructions[self.PC]) #roda a instrução atual
            self.PC += 1

    def runInstruction(self,instruction):
        instructionParts = instruction.split(' ') 
        
        #Toda instrução do input é dividida em várias partes no exemplo dela,  (e aq uso o split para separa-las) 
        #com a primeira parte sendo qual o processo que a instrução faz parte
        #a segunda parte sendo qual o name da instrução
        #e a terceira e/ou quarta complementos a instrução, com função determinada pela instrução executada
        #(por exemplo, uma instr de escrita no P1 tem partes ['P1','W','address da escrita','o que será escrito'])
        
        correspondingProcess = self.getProcess(instructionParts[0])
        correspondingInstruction = instructionParts[1]

        if(correspondingInstruction == 'C'): #o código de cada instrução pode estar aqui
            self.createProcess(instructionParts[0],instructionParts[2])
        else:
            self.executeProcess(correspondingProcess) #coloca o processo no estado 'executando'

        #Aqui, o código verifica qual instrução é, e executa a função da instrução em questão
        #Provavelmente seria melhor fzr com um switch-case, mas 6 ifs tbm servem por emqto
                    
        if(correspondingInstruction == 'R'): #o código de cada instrução pode estar aqui
            self.readFromMemory(correspondingProcess,instructionParts[2])
        elif(correspondingInstruction == 'W'): #o código de cada instrução pode estar aqui
            self.writeToMemory(correspondingProcess,instructionParts[2],instructionParts[3])
        elif(correspondingInstruction == 'P'): #o código de cada instrução pode estar aqui
            self.runCPUinst(correspondingProcess,instructionParts[2])
        elif(correspondingInstruction == 'I'): #o código de cada instrução pode estar aqui
            self.runIOinst(correspondingProcess,instructionParts[2])
        elif(correspondingInstruction == 'T'): #o código de cada instrução pode estar aqui
            self.endProcess(correspondingProcess,instructionParts[2])

    def getProcess(self,processname):
        for process in self.MP.images:
            if(process.name == processname):
                return process
        print(' Process not found in memory!')
        #aqui provavelmente seria um page fault ou algo assim 
        return None


    #Funções a seguir são chamadas para executar cada instrução do input, como tá lá no docs da profa

    def createProcess(self, processName, desiredSize): #instrução C  
        print(' Creating process',processName,"with size",desiredSize,"bytes","...")
        p = Process(processName,'New')
        self.MP.addProcess(p)

    def readFromMemory(self, process, virtualAddress):  #instrução R
        print(' Reading from memory at virtual address',virtualAddress,"by process",process.name,"...")
        self.blockProcess(process) #nn sei se leitura na mem bloqueia ou nn na verdade 

    def writeToMemory(self, process, virtualAddress, data): #instrução W
        print(" Writing",data,"to memory at virtual address",virtualAddress,"by process",process.name,"...")
        self.blockProcess(process)

    def runCPUinst(self, process,virtualAddress): #instrução P
        print(' Running CPU instruction at virtual adress',virtualAddress,"by process",process.name,"...")
    
    def runIOinst(self, process, virtualAdress): #instrução I
        print(' Running I/O instruction at virtual adress',virtualAdress,"by process",process.name,"...")
        self.blockProcess(process)
        #temos também que criar alguma coisa relacionada ao dma provavelmente

    def endProcess(self, process): #instrução T
        print(' Ending Process',process.name)


    #funções a seguir servem para mudar o estado de processo, de acordo com aquele diagrama d estados lá

    def blockProcess(self,process):
        process.state = 'blocked'
        #fazer código para ativar DMA ou alguma coisa assim?

    def suspendProcess(self,process):
        process.state = 'blocked'
        #fazer código para tirar da MP 
    
    def executeProcess(self,process):
        for p in self.MP.images:
            if(p.state == 'executing'):  #assuming aqui que sistema tem só 1 processador
                p.state = 'ready'   #e que só tem, em um dado momento, 1 processo executando
        process.state = 'executing' #mas tem grande chance disso tar errado, ent sla


    #função q pega o nome de um processo e busca os dados do processo na MP

    def getProcess(self,processname): 
        for process in self.MP.images:
            if(process.name == processname):
                return process
        print(' Process not found in memory!')
        #aqui provavelmente seria um page fault ou algo assim 
        return None
    
class Input:
    def __init__(self, _instructions):
        self.instructions = _instructions

def readInputFromFile(filePath):
    #ainda temos que fazer a parte de ler o input
    i = Input(['P1 C 250','P1 R 10 20', 'P1 W 20 30','P2 C 140'])#input teste
    return i


#testes:
p = Process(0,'New')
p.data.append('test: hello world!')
print(p.data[0])

#testes do simulador
m = Memory(256) #size pode ser em bits, bytes ou paginas, ainda nn sei qual a melhor forma
                #mas isso está ligado a configuração do sistema q vamos ver dps
s = Simulator(m)
input = readInputFromFile('input.txt') #no momento ainda nn le de um arquivo
s.simulate(input)
s.MP.printMemory()
