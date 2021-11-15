## CMSC 411 Project 2 ###
import sys

# not to be confused with the Register class
# oversees all of the registers
class Registers:
    # a simple register
    class Register:
        def __init__(self, _data=0, _id=""):
            self.data_ = _data
            self.id_ = _id
            self.being_used_ = False
        
        # a string representation of the Register object
        def __str__(self):
            return f"Register: {self.id_}\tData: {self.data_}\t\tBeing used: {self.being_used_}"
            
        # setter and getter for the register
        def set_data(self, _data=0):
            self.data_ = _data
        def get_data(self):
            return self.data_
        def get_id(self):
            return self.id_
        
        # when a register is being used/is done being used, invert being_used variable
        def invert_use_status(self):
            self.being_used_ = not self.being_used_

    # the two types of registers
    class FPRegister(Register):
        def __init__(self, _data=0.0, _id=""):
            super().__init__(_data=_data, _id=_id)
        def set_data(self, _data=0.0):
            self.data_ = float(_data) # rudimentary type checking 
        def get_type(self):
            return "FP"
    class IntRegister(Register):
        def __init__(self, _data=0, _id=""):
            super().__init__(_data=_data, _id=_id)
        def set_data(self, _data=0):
            self.data_ = int(_data)
        def get_type(self):
            return "Int"

    # the init function for Registers class
    def __init__(self) -> None:
        self.FPRegs_ = [] # the two lists of Register objects
        self.IntRegs_ = []

        # initializes the 32 FP/Int registers inside of this class
        for i in range(32):
            temp = Registers.FPRegister(_id=f"F{i}")
            self.FPRegs_.append(temp)
            temp = Registers.IntRegister(_id=f"${i}")
            self.IntRegs_.append(temp)
    
    # it accepts register names in the format of F0-F31 or r0-r31
    # returns a register object
    def retrieve(self, _id=""):
        index = 0
        if len(_id) == 2:
            index = int(_id[1])
        if len(_id) == 3 :
            index = int(f"{_id[1]}{_id[2]}") # weird looking code
        
        # registers that doesn't start with F or $, or index 32+, or length of name doesn't match
        if index > 31 or _id[0] not in ['F', '$'] or (len(_id) not in [2,3]):
            raise Exception # when retrieving an invalid register name

        if _id[0] == 'F':
            return self.FPRegs_[index]
        if _id[0] == '$':
            return self.IntRegs_[index]
    
    # takes a register ID and writes data to that register
    def write_to(self, _id="", _data=0):
        try: temp = self.retrieve(_id)
        except Exception: 
            print(f"\"{_id}\" is not a valid register!")
        else:
            temp.set_data(_data)
    
    # prints all FP Register objects
    def print_all_FP(self):
        print("\nAll FP Registers")
        for i in self.FPRegs_:
            print(i)
    # prints all Int register objects
    def print_all_Int(self):
        print("\nAll Int Registers")
        for i in self.IntRegs_:
            print(i)
    # prints all registers
    def print_all_registers(self):
        self.print_all_FP()
        self.print_all_Int()

# memory simulation, literally just a class with a list in it
# if no data set specified, then it will use preset values
class Memory:
    def __init__(self, data_set=[45,12,0,92,10,135,254,127,18,4,55,8,2,98,13,5,233,158,167]):
        self.memory_ = data_set
        self.length_ = len(self.memory_)
        self.being_used_ = False
    
    # when retrieving from memory, add both address # and offset value together as _offset
    # index mod by length of memory will make mem circular
    def retrieve_index(self, _offset):
        index = _offset % self.length_
        return self.memory_[index] # the data at given memory address+offset
    
    def set_data_at(self, _offset, _data):
        index = _offset % self.length_
        self.memory_[index] = _data
    
    def is_being_used(self):
        return self.being_used_

    def print_all_memory(self):
        print("\nAll memory location and data")
        for i in range(self.length_):
            print(f"Memory location: {i}\tData: {self.memory_[i]}")

#####################################################################################################
# each line of code becomes an instruction class
# _instruction is a list of lists of instructions parsed from the file by the parser function
class Instruction:
    class IF:
        def __init__(self, _clockCycle, _opcode, _dest, _opOne, _opTwo="", _label="") -> None:
            self.opcode_ = _opcode
            self.clock = {}
            self.isDone = False
            self.isStalled = False 

    class ID:
        def __init__(self, _clockCycle, _opcode, _dest, _opOne, _opTwo="", _label="") -> None:
            self.instruction = _opcode
            self.clockCycle = {}
            self.isDone = False
            self.isStalled = False 

    class EX:
        def __init__(self, _clockCycle, _opcode, _dest, _opOne, _opTwo="", _label="") -> None:
            # these two variables are controlled by the predictor
            self.last_taken = True
            self.current_outcome = None
            self.clockCycle = {}
            self.instruction = _opcode
        def execute(self):
            if(self.instruction == "ADD"):
                pass
    
    class MEM:
        def __init__(self, _clockCycle, _opcode, _dest, _opOne, _opTwo="", _label="") -> None:
            pass
    
    class WB:
        def __init__(self, _clockCycle, _opcode, _dest, _opOne, _opTwo="", _label="") -> None:
            pass

    def __init__(self, _clockCycle, _opcode, _dest, _opOne, _opTwo="", _label="") -> None:
        self.opcode_ = _opcode
        self.label = _label
        self.opOne = _opOne
        self.opTwo = _opTwo
        self.dest = _dest
        self.is_loop = False
        self.is_done = False
        
        
        # the idea is that each instruction line keeps track of its own stages, which are also classes
        self.if_ = Instruction.IF(_clockCycle, _opcode, _dest, _opOne, _opTwo="", _label="")
        self.id_ 
        self.ex_ 
        self.mem_
        self.wb_ 
    
    # if a label is found, then this function is called
    def predictor(self):
        pass

    def get_is_done(self):
        return self.is_done
        
class Cache:
    def __init__(self):
        self.being_used = False
        self.set1 = None
        self.set2 = None 
        self.set3 = None 
        self.set4 = None

    def hit_or_miss(self, _address):
        pass

class Pipeline:
    def __init__(self, _fileName):
        self.instruction = []
        self.instExecuted = []
        self.registers = Registers()
        self.memory = Memory()

        #parse through file and load instructions list
        self.instruction.append("stuff")

    def simulate(self):
        #simulate pipeline
        clockCycle = 0

        while(not self.instruction[-1].get_is_done()):
            clockCycle+=1
            pass
        pass

    def writeExcel(self, _fileName):
        #write to excel file
        pass

# just take the filename and do something with it
# takes a MIPS file, returns a list of instruction lists
def parser(_filename="test.txt"):
    instructions = []
    with open(_filename, 'r', encode='utc-8', error='ignore') as file:
        lines = file.readlines()
        # parses the instruction line by ',' and '\n'
        # the delim ':' is maintained for label recognition
        for line in lines:
            line = line.replace(',', ' ').replace('\n', ' ').replace('\xa0')
            line = line.split(' ')
            line = [i for i in line if i] # cleans all empty space in the parsed instruction line
            instructions.append(line)    
    return instructions

if __name__ == '__main__':
    registers = Registers() # all registers
    memory = Memory() # all memory
    # registers.print_all_registers()
    # memory.print_all_memory()

    # filename = ""
    # pipe = Pipeline(filename)

    print(parser())


    
