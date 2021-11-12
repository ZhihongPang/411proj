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
            temp = IntRegister(_id=f"R{i}")
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
        if _id[0] == 'R':
            return self.IntRegs[index]
    
    # takes a register ID and writes data to that register
    def write_to(self, _id="", _data=0):
        temp = self.retrieve(_id)
        temp.set_data(_data)
    
    # prints all of the FP registers
    def print_all_FP(self):
        print("All FP Registers")
        # print(f"Register: {i}\tData: {i.get_data()}" for i in self.FPRegs)
        print(i for i in self.FPRegs)
    # prints all Int registers
    def print_all_Int(self):
        print("All Int Registers")
        # print(f"Register: {i}\tData: {i.get_data()}" for i in self.IntRegs)
        print(i for i in self.IntRegs)
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
    def retrieve_index(self, _index):
        offset = _index % self.length_
        return self.memory_[offset] # the data at given memory address+offset
    
    def set_data_at(self, _index, _data):
        offset = _index % self.length_
        self.memory_[offset] = _data
    
    def print_all_memory(self):
        print(f"Memory at location: {i}\tData: {self.memory_[i]}" for i in range(self.length_))


#####################################################################################################
# each line of code becomes an instruction class
# probably needs a parser function to parse the instruction line before passing it to the class
class Instruction:
    def __init__(self, _instruction) -> None:
        self.instruction_ = _instruction # highly simplified
        self.is_loop = False
        # these two variables are controlled by the predictor
        self.last_taken = True
        self.current_outcome = None 

        self.if_ = 0
        self.id_ = 0
        self.ex_ = []
        self.mem_ = []
        self.wb_ = 0
    
    # if a label is found, then this function is called
    def predictor(self):
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


    

