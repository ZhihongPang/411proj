### CMSC 411 Project 2 ###
import os
from os import error
import sys
import xlwt
import re
from xlwt import Workbook

class Registers:
    """
    This class oversees all registers, when called it will initialize a class that holds two lists, one for each type of registers
    """
    def __init__(self):
        self.FPRegs_ = [] # the two lists of Register objects
        self.IntRegs_ = []

        # initializes the 32 FP/Int registers inside of this class
        for i in range(32):
            temp = Registers.FPRegister(_id=f"F{i}")
            self.FPRegs_.append(temp)
            temp = Registers.IntRegister(_id=f"${i}")
            self.IntRegs_.append(temp)
    
    def retrieve(self, _id=""):
        """
        Takes in a register name as _id, in the format of F0-F31 or $0-$31
        Returns the desired register object from the internal list of register objects
        Note: the = sign in the parameter signifies a default parameter, if no _id is passed to it, it will default to ""
        Note: try not to use this function directly, when testing, use write_to instead to avoid exception interruption
        """
        index = -1
        if len(_id) == 2:
            index = int(_id[1])
        if len(_id) == 3 :
            index = int(f"{_id[1]}{_id[2]}") # weird looking code, casts an f-string with the two _id positions into an int
        
        # registers with index not in range of 0, 31 or ids that doesn't start with F or $ or id length is too long
        if not (0 <= index <= 31) or _id[0] not in ['F', '$'] or (len(_id) not in [2,3]):
            raise Exception # Register.retrieve() received an invalid register name.

        if _id[0] == 'F':
            return self.FPRegs_[index]
        if _id[0] == '$':
            return self.IntRegs_[index]
    
    def write_to(self, _id="", _data=0):
        """
        Takes in a register name (in the form of $1 or F1 etc.) and a data, then writes the data to the given register
        Will catch the exception when an invalid register is passed to it
        """
        try: temp = self.retrieve(_id)
        except Exception:
            print(f"\"{_id}\" is not a valid register!")
        else:
            temp.set_data(_data)
    
    # prints all FP/Int Registers
    def print_all_FP(self):
        print("\nAll FP Registers")
        for i in self.FPRegs_:
            print(i)
    def print_all_Int(self):
        print("\nAll Int Registers")
        for i in self.IntRegs_:
            print(i)
    def print_all_registers(self):
        self.print_all_FP()
        self.print_all_Int()

    class Register:
        """
        Simple register class that stores data, each register class holds their own names as id_
        Each register also has the write to and read from variables, which are the cycles that the registers
        are ok to be read/write to, to prevent data hazards within the pipeline
        """
        def __init__(self, _data=0, _id=""):
            self.data_ = _data
            self.id_ = _id
            self.is_ok_to_write_to = 0
            self.is_ok_to_read_from = 0
        
        def __str__(self) -> str:
            """ A string representation of the register object """
            return f"Register: {self.id_}\tData: {self.data_}\t\tRead/Write cycles: {self.is_ok_to_read_from} {self.is_ok_to_write_to}"
            
        # setters and getters for the register
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
            self.data_ = float(_data) # type checking by type casting lol
        def get_type(self):
            return "FP"
    class IntRegister(Register):
        def __init__(self, _data=0, _id=""):
            super().__init__(_data=_data, _id=_id)
        def set_data(self, _data=0):
            self.data_ = int(_data)
        def get_type(self):
            return "Int"

class Memory:
    """
    Memory Simulation, just a class with a list in it,
    default parameter for the data_set, if no data_set is used then it will use the default
    """
    def __init__(self, data_set=[45,12,0,92,10,135,254,127,18,4,55,8,2,98,13,5,233,158,167]):
        self.memory_ = data_set
        self.length_ = len(self.memory_)
        self.being_used_ = False
    
    def retrieve_at_address(self,  _address, _offset=0):
        """ 
        When using this function, the offset is assumed to be 0 unless another offset is passed to it
        Returns memory at address at given offset
        """
        _address += _offset # adds both together to get the actual address
        _address = _address % self.length_
        return self.memory_[_address]
    
    def set_at_address(self, _data, _address, _offset=0):
        """ Identical to the retrieve at function """
        _address += _offset
        _address = _address % self.length_
        self.memory_[_address] = _data

    # might not actually be necessary
    def is_being_used(self):
        return self.being_used_
    def print_all_memory(self):
        print("\nAll memory location and data")
        for i in range(self.length_):
            print(f"Address: {i}\tData: {self.memory_[i]}")


class Instruction:
    """
    Each instruction object tracks the cycles that they execute each cycles with internal variables
    Ex/Mem/Stall, which have multiple stages will keep track of their cycles using lists
    The stalled cycles will get referenced by the cycle right after, so the instruction after will know which cycles to not use
    The Functional unit functions act as setters that sets the cycles for the stages
    
    Note: predictor stuff
    """
    def __init__(self, _label, _opcode, _op_one, _op_two, _op_three, _workbook, _stalled_cycles=[], _cycle=1) -> None:
        self.cycle_ = _cycle
        self.opcode_ = _opcode
        self.label_ = _label
        self.op_one_ = _op_one # op one is used as dest most of the time
        self.op_two_ = _op_two
        self.op_three_ = _op_three
        
        # the functional units will be kept track of using variables
        self.if_ = 0
        self.id_ = 0
        self.ex_ = []
        self.mem_ = []
        self.wb_ = 0
        self.stalled_cycles = _stalled_cycles

        # internal variables that keeps track of the instruction types
        self.mem_instructions_ = ["L.D", "S.D", "LI", "LW", "SW"]
        self.alu_instructions_ = ["ADD", "ADDI", "ADD.D", "SUB.D", "SUB", "MUL.D", "DIV.D"]
        self.branch_instructions_ = ["BEQ", "BNE", 'J']

        self.is_beginning_of_loop_ = False
        self.is_done_ = False
    
    def __str__(self) -> str:
        if self.op_three_ == "":
            return f"{self.label_} {self.opcode_} {self.op_one_}, {self.op_two_}\n"
        return f"{self.label_} {self.opcode_} {self.op_one_}, {self.op_two_}, {self.op_three_}\n"
    
    # the five pipeline cycles for now
    def IF(self):
        self.if_ = self.cycle_
        self.cycle_ += 1
    
    def ID(self):
        self.id_ = self.cycle_
        self.cycle_ += 1
    
    def EX(self):
        self.ex_.append(self.cycle_)
        self.cycle_ += 1
    
    def MEM(self):
        self.mem_.append(self.cycle_)
        self.cycle_ += 1
    
    def WB(self):
        self.wb_ = self.cycle_
        self.cycle_ += 1

    # since a branch instruction will only look at itself for prediction, each instruction class will keep track of its own predictor
    def predictor(self):
        pass
    
    def print_instruction(self):
        print(f"Label: {self.label_}\tOpcode: {self.opcode_}\tOp One: {self.op_one_}\tOp Two: {self.op_two_}\tOp Three: {self.op_three_}\n")
        
class Cache:
    """
    Simple Cache Object where there are 4 sets to be written into
    Each set will hold a memory address and their corresponding data
    Miss creates two additional mem stages, hits are based on mem address mod 4 and finding matching addresses
    Write back is only called when a mem is being over written by hit/miss
    """
    def __init__(self):
        # each of the sets should hold a copy of a memory object
        # that way, it will not update the memory object when its changed, only when its kicked out of the cache
        self.being_used = False
        self.set1 = []
        self.set2 = [] 
        self.set3 = [] 
        self.set4 = []

    # insert hit or miss meme here
    def hit_or_miss(self, _address):
        pass

    def write_back(self, _data, _address):
        pass

class Pipeline:
    """
    Pipeline parses the text file into a list of instruction lists, 
    a two dimensional array where each index of the list is a list of label, opcode, all the operands for every line of the text file
    """
    def __init__(self, _fileName="test.txt"):
        self.instructions = [] # holds a list of instruction objects, basically the PC
        self.insExecuted = [] # a list of instruction objects to be written into an excel sheet
        self.registers = Registers()
        self.memory = Memory()
        
        with open(_fileName) as file:
            lines = file.readlines()

        for line in lines:
            # creating regEx object and pattern number
            x = Pipeline.findPattern(line)
            if x != 0: # find_patterns returns 0 if no patterns matched/invalid instruction passed
                label = opcode = op_one = op_two = op_three = "" # place holders
                if x.group(2):
                    label = x.group(2)
                opcode = x.group(3)
                op_one = x.group(4)

                # these try except blocks will catpture additional operands if they exist
                try: 
                    x.group(5)
                    op_two = x.group(5)
                except IndexError:
                    op_two = ""
                try:
                    x.group(6)
                    op_three = x.group(6)
                except IndexError:
                    op_three = ""
                instruction = Instruction(_workbook=0,_label=label,_opcode=opcode,_op_one=op_one,_op_two=op_two,_op_three=op_three)
            else:
                return Exception # if x detected an invalid pattern, raise error
            self.instructions.append(instruction)

    # function accepts a string and returns a regEx object and pattern number it matches
    def findPattern(line):
        # pattern for ADD.D/SUB.D/DIV.D/MUL.D, the ALU instructions
        pattern_1 = "^(([a-zA-Z]+):)?\s*([A-Z]+\.[A-Z]+)\s+(F[1-3]?[0-9])\s*,\s*(F[1-3]?[0-9])\s*,\s*(F[1-3]?[0-9])\s*.*\n?$"
        # pattern for S.D/L.D or
        pattern_2 = "^(([a-zA-Z]+):)?\s*([A-Z]\.[A-Z])\s+(F[1-3]?[0-9])\s*,\s*([1-9]?[0-9]?[0-9])\((\$[1-3]?[0-9])\)\s*.*\n?$"
        # patter for LW/SW
        pattern_3= "^(([a-zA-Z]+):)?\s*([A-Z]+)\s+(\$[1-3]?[0-9])\s*,\s*([1-9]?[0-9]?[0-9])\((\$[1-3]?[0-9])\)\s*.*\n?$"
        # pattern for ADDI
        pattern_4 = "^(([a-zA-Z]+):)?\s*([A-Z]+)\s+(\$[1-3]?[0-9])\s*,\s*(\$[1-3]?[0-9])\s*,\s*([1-9]?[0-9]?[0-9])\s*.*\n?$"
        # pattern for BEQ/BNE
        pattern_5 = "^(([a-zA-Z]+):)?\s*([A-Z]+)\s+(\$[1-3]?[0-9])\s*,\s*(\$[1-3]?[0-9])\s*,\s*([a-zA-Z]+)\s*.*\n?$"
        # pattern for LI
        pattern_6 = "^(([a-zA-Z]+):)?\s*(LI)\s+(\$[1-3]?[0-9])\s*,\s*([1-9]?[0-9]?[0-9])\s*.*\n?$"
        # pattern for J
        pattern_7 = "^(([a-zA-Z]+):)?\s*([A-Z]+)\s+\s*([a-zA-Z]+)\s*.*\n?$"
        patterns = [pattern_1, pattern_2, pattern_3,pattern_4,pattern_5,pattern_6,pattern_7]

        for pattern in patterns:
            x = re.match(pattern, line)
            if x:
                return x
        return 0 

    def print_all_instruction_objects(self):
        for instruction in self.instructions:
            print(instruction)

    def execute_lines(self):
        cycles = 0
        for instruction_line in self.instructions:
            instruction_line.IF()
            instruction_line.ID()
            instruction_line.EX()
            instruction_line.MEM()
            instruction_line.WB()
            self.insExecuted.append(instruction_line)

    def write_to_excel(self, _filename="test.xls"):
        try: os.remove(_filename) # clean up, makes testing easier
        except Exception: pass
        #write to excel file
        wb = Workbook()
        sheet1 = wb.add_sheet(_filename)

        # prints out cycle #s on top
        end_cycle = self.insExecuted[-1].cycle_
        for i in range(1, end_cycle):
            sheet1.write(0, i, i)
        
        for i in range(1,len(self.insExecuted)+1):
            # write(row, column, item)
            sheet1.write(i,0, self.insExecuted[i-1].__str__()) # the col in this will always be 0
            sheet1.write(i,self.insExecuted[i-1].if_, "IF")
            sheet1.write(i,self.insExecuted[i-1].id_, "ID")
            sheet1.write(i,self.insExecuted[i-1].ex_[0], "EX")
            sheet1.write(i,self.insExecuted[i-1].mem_[0], "MEM")
            sheet1.write(i,self.insExecuted[i-1].wb_, "WB")

        wb.save(_filename)



if __name__ == '__main__':
    registers = Registers() # all registers
    memory = Memory() # all memory
    # registers.print_all_registers()
    # memory.print_all_memory()
    pipeline = Pipeline()
    pipeline.print_all_instruction_objects()

    pipeline.execute_lines()
    pipeline.write_to_excel()
