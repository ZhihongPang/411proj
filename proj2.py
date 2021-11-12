## CMSC 411 Project 2 ###

# a simple register
class Register:
    def __init__(self, _data=0, _id=""):
        self.data_ = _data
        self.id_ = _id
        self.being_used_ = False
    
    # prints out the register informations
    def __str__(self):
        return f"Register: {self.id_}\tData: {self.data_}\tBeing used: {self.being_used_}"
        
    # data setter for the register
    # NO TYPE CHECKING!
    def set_data(self, _data=0):
        self.data_ = _data
    
    def get_data(self):
        return self.data_

    def get_id(self):
        return self.id_

# for now, there's basically no differece between the two types of registers
class FPRegister(Register):
    def __init__(self, _data=0.0, _id=""):
        super().__init__(_data=_data, _id=_id)
    
    def get_type(self):
        return "FP"
class IntRegister(Register):
    def __init__(self, _data=0, _id=""):
        super().__init__(_data=_data, _id=_id)
    
    def get_type(self):
        return "Int"

# not to be confused with the Register class
# makes it easier to use the registers
class Registers:
    def __init__(self) -> None:
        self.FPRegs = []
        self.IntRegs = []

        # initializes the 32 FP/Int registers inside of this class
        for i in range(32):
            temp = FPRegister(_id=f"F{i}")
            self.FPRegs.append(temp)
            temp = IntRegister(_id=f"${i}")
            self.IntRegs.append(temp)
    
    # it accepts register names in the format of F0-F31 or r0-r31
    # returns a register object
    # NO PARAMETER CHECKING, ALL _id's PASSED TO IT IS ASSUME TO BE VALID
    def retrieve(self, _id=""):
        index = 0
        if len(_id) == 2:
            index = int(_id[1])
        if len(_id) > 2:
            index = int(f"{_id[1]}{_id[2]}") # weird looking code
            
        if _id[0] == 'F':
            return self.FPRegs[index]
        if _id[0] == '$':
            return self.IntRegs[index]
    
    # takes a register ID and writes data to that register
    def write_to(self, _id="", _data=0):
        temp = self.retrieve(_id)
        temp.set_data(_data)
    
    # prints all of the FP registers
    def print_all_FP(self):
        print("\nAll FP Registers")
        for i in range(len(self.FPRegs)):
            print(f"Register: {self.FPRegs[i].get_id()}\tData: {self.FPRegs[i].get_data()}")
    # prints all Int registers
    def print_all_Int(self):
        print("\nAll Int Registers")
        for i in range(len(self.IntRegs)):
            print(f"Register: {self.IntRegs[i].get_id()}\tData: {self.IntRegs[i].get_data()}")
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
        self.being_used = False
    
    # when retrieving from memory, add both address # and offset together as index
    # index mod by length of memory will make mem circular
    def retrieve_index(self, _offset):
        index = _offset % self.length_
        return self.memory_[index] # the data at given memory address+offset
    
    def set_data_at(self, _offset, _data):
        index = _offset % self.length_
        self.memory_[index] = _data
    
    def print_all_memory(self):
        print("\nAll memory location and data")
        for i in range(self.length_):
            print(f"Memory at location: {i}\tData: {self.memory_[i]}")


#####################################################################################################
# each line of code becomes an instruction class
# probably needs a parser function to parse the instruction line before passing it to the class
class Instruction:
    def __init__(self, _instruction, _clockCycle, _dest, _opOne, _opTwo="", _label="") -> None:
        self.instruction_ = _instruction # highly simplified
        self.label = _label
        self.opOne = _opOne
        self.opTwo = _opTwo
        self.dest = _dest
        self.is_loop = False
        self.is_done = False
        
        

        self.if_ = IF(_instruction, _clockCycle,  _dest, _opOne, _opTwo="", _label="")
        self.id_ 
        self.ex_ 
        self.mem_
        self.wb_ 
    
    # if a label is found, then this function is called
    def predictor(self):
        pass

    def get_is_done(self):
        return self.is_done
        
class IF:
    def __init__(self, _instruction,  _dest, _opOne, _opTwo="", _label="") -> None:
        self.instruction = _instruction
        self.clockCycle = {}
        self.isDone = False
        self.isStalled = False 

class ID:
    def __init__(self, _instruction,  _dest, _opOne, _opTwo="", _label="") -> None:
        self.instruction = _instruction
        self.clockCycle = {}
        self.isDone = False
        self.isStalled = False 

class EX:
    def __init__(self, _instruction,   _dest, _opOne, _opTwo="", _label="") -> None:
        # these two variables are controlled by the predictor
        self.last_taken = True
        self.current_outcome = None
        self.clockCycle = {}
        self.instruction = _instruction
    def execute(self):
        if(self.instruction == "ADD"):
            
            pass

class Pipeline:
    def __init__(self, _fileName):
        self.instruction = []
        self.instExecuted = []
        self.registers = Register()
        self.memory = Memory()

        #parse through file and load instructions list

        self.instruction.append("stuff")

        pass

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
        



class Cache:
    def __init__(self):
        self.being_used = False
        self.set1 = None
        self.set2 = None 
        self.set3 = None 
        self.set4 = None

if __name__ == '__main__':
    registers = Registers() # all registers
    memory = Memory() # all memory
    registers.print_all_registers()
    memory.print_all_memory()


    filename = ""
    pipe = Pipeline(filename)



    

