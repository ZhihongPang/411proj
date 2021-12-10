### CMSC 411 Project ###
import os
from os import error, pipe
import sys
from typing import Optional
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
            self.id_ = _id # name of the register, $0-$31/F0-F31
            self.read_cycle = 0 # the cycle which the register is ok to be read
            self.write_cycle = 0 # the cycle the register is ok to be written to
        
        def __str__(self) -> str:
            """ A string representation of the register object """
            return f"Register: {self.id_}\tData: {self.data_}\t\tRead/Write Cycles:{self.read_cycle}, {self.write_cycle}"
            
        # setters and getters for the register
        def set_data(self, _data=0):
            self.data_ = _data
        def get_data(self):
            return self.data_
        def get_id(self):
            return self.id_
        def get_read_cycle(self):
            return self.read_cycle
        def get_write_cycle(self):
            return self.write_cycle

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
    
    # address will be in format of $0 to $18
    def retrieve_at_address(self,  _address, _offset=0):
        """ 
        When using this function, the offset is assumed to be 0 unless another offset is passed to it
        Returns memory at address at given offset
        """
        _address = _address.replace('$', '') 
        _address = int(_address) + int(_offset) # adds both together to get the actual address
        _address %= self.length_ # loops around
        return self.memory_[_address]
    
    def write_to_address(self, _data, _address, _offset=0):
        """ Identical to the retrieve at function """
        _address = _address.replace('$', '') 
        _address = int(_address) + int(_offset)
        _address %= self.length_
        self.memory_[_address] = _data

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
    
    Note: need to do predictor stuff
    """
    def __init__(self, _label, _opcode="", _op_one="", _op_two="", _op_three="", _if=1, _id=2, _ex=[3], _mem=[4], _wb=5) -> None:
        self.opcode_ = _opcode
        self.label_ = _label
        self.op_one_ = _op_one # op one is used as dest most of the time
        self.op_two_ = _op_two
        self.op_three_ = _op_three
        
        # might not need
        # the functional units will be kept track of using variables
        self.if_ = _if
        self.id_ = _id
        self.ex_ = _ex
        self.mem_ = _mem
        self.wb_ = _wb

        self.is_beginning_of_loop_ = False
        self.is_done_ = False

    def __str__(self) -> str:
        if self.op_three_ == "":
            return f"{self.label_} {self.opcode_} {self.op_one_}, {self.op_two_}\n"
        return f"{self.label_} {self.opcode_} {self.op_one_}, {self.op_two_}, {self.op_three_}\n"

    # since a branch instruction will only look at itself for prediction, each instruction class will keep track of its own predictor
    def predictor(self):
        pass
    
    def print_instruction(self):
        print(f"Label: {self.label_}\tOpcode: {self.opcode_}\tOp One: {self.op_one_}\tOp Two: {self.op_two_}\tOp Three: {self.op_three_}\n")

class Pipeline:
    """
    Pipeline parses the text file into a list of instruction lists, 
    a two dimensional array where each index of the list is a list of label, opcode, all the operands for every line of the text file
    """
    def __init__(self, _fileName="test.txt"):
        self.instructions = {} # holds a dictionary of instructions, with keys:instruction address and value:instructions
        self.loops = {} # tracks where loops begin, key:loop name, value:instruction's address

        # current format of executed instructions:
        # list of dictionaries, index:executed instructions, key:cycle, value:stage
        self.insExecuted = []
        self.registers = Registers()
        self.memory = Memory()
        self.cache = {0:[0],1:[0],2:[0],3:[0]} # list of dictionaries, where key:memory address, value:[dirty bit, data], dirty bit == 1 when data has been altered
        self.cache_size = 4 # 4 sets

        # all_instructions = Pipeline.parser()
        # counter = 0 # instruction address counter, first instruction is at address 0000
        # for instruction in all_instructions:
        #     if ':' in instruction[0]: # if a loop is found, then add it to the dictionary, key:loop name value:loop address
        #         loop_name = instruction[0].replace(':', '')
        #         self.loops[loop_name] = counter
        #     self.instructions[counter] = instruction
        #     counter += 1
    
        with open(_fileName) as file:
            lines = file.readlines()
        counter = 0
        for line in lines:
            # creating regEx object and pattern number
            x = Pipeline.findPattern(line)
            if x != 0: # find_patterns returns 0 if no patterns matched/invalid instruction passed
                label = opcode = op_one = op_two = op_three = "" # place holders
                if x.group(2):
                    label = x.group(2)
                    self.loops[counter] = label
                opcode = x.group(3)
                op_one = x.group(4)

                # these try except blocks will catpture additional operands if they exist
                try: 
                    x.group(5)
                    op_two = x.group(5)
                except IndexError: op_two = ""
                try:
                    x.group(6)
                    op_three = x.group(6)
                except IndexError: op_three = ""
                instruction = Instruction(_workbook=0,_label=label,_opcode=opcode,_op_one=op_one,_op_two=op_two,_op_three=op_three)
                self.instructions[counter] = instruction
                counter += 1
            else:
                return Exception # if x detected an invalid pattern, raise error
            

    # just take the filename and do something with it
    # takes a MIPS file, returns a list of instruction lists
    def parser(_filename="test.txt"):
        instructions = []
        with open(_filename, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            # parses the instruction line by comma, newline, some weird space character, and tab
            # the char ':' is maintained for label recognition
            for line in lines:
                line = line.replace(',', ' ').replace('\n', ' ').replace('\xa0', ' ').replace('\t', ' ')
                line = line.split(' ')
                line = [i for i in line if i] # cleans all empty space in the parsed instruction line
                instructions.append(line)    
        return instructions

    # function accepts a string and returns a regEx object and pattern number it matches
    def findPattern(line):
        # pattern for ADD.D/SUB.D/DIV.D/MUL.D, the ALU instructions
        pattern_1 = "^(([a-zA-Z0-9_]+):)?\s*([A-Z]+\.[A-Z]+)?\s*(F[1-3]?[0-9])?\s*,?\s*(F[1-3]?[0-9])?\s*,?\s*(F[1-3]?[0-9])?\s*.*\n?$"
        # pattern for S.D/L.D or
        pattern_2 = "^(([a-zA-Z0-9_]+):)?\s*([A-Z]\.[A-Z])?\s*(F[1-3]?[0-9])?\s*,?\s*([1-9]?[0-9]?[0-9])?\(?(\$[1-3]?[0-9])?\)?\s*.*\n?$"
        # patter for LW/SW
        pattern_3= "^(([a-zA-Z0-9_]+):)?\s*([A-Z]+)?\s*(\$[1-3]?[0-9])?\s*,?\s*([1-9]?[0-9]?[0-9])?\(?(\$[1-3]?[0-9])?\)?\s*.*\n?$"
        # pattern for ADDI
        pattern_4 = "^(([a-zA-Z0-9_]+):)?\s*([A-Z]+)?\s*(\$[1-3]?[0-9])?\s*,?\s*(\$[1-3]?[0-9])?\s*,?\s*([1-9]?[0-9]?[0-9])?\s*.*\n?$"
        # pattern for BEQ/BNE
        pattern_5 = "^(([a-zA-Z0-9_]+):)?\s*([A-Z]+)?\s*(\$[1-3]?[0-9])?\s*,?\s*(\$[1-3]?[0-9])?\s*,?\s*([a-zA-Z]+)?\s*.*\n?$"
        # pattern for LI
        pattern_6 = "^(([a-zA-Z0-9_]+):)?\s*(LI)?\s*(\$[1-3]?[0-9])?\s*,?\s*([1-9]?[0-9]?[0-9])?\s*.*\n?$"
        # pattern for J
        pattern_7 = "^(([a-zA-Z0-9_]+):)?\s*([A-Z]+)?\s*\s*([a-zA-Z]+)?\s*.*\n?$"
        
        for pattern in [pattern_1, pattern_2, pattern_3,pattern_4,pattern_5,pattern_6,pattern_7]:
            x = re.match(pattern, line)
            if x:
                return x
        return 0 

    # for testing
    def print_all_instruction_objects(self):
        for instruction_address in self.instructions:
            print(instruction_address, self.instructions[instruction_address])
    def print_all_loops_and_addresses(self):
        for loops in self.loops:
            print("Address:", self.loops[loops], "Name:", loops)

    def execute_lines(self):
        instruction_counter = 0 # program counter
        stalled_cycles = [0, 1] # list of stalled cycles, cycles 0 and 1 will never be stalls, so they're used as place holders
        last_ID_cycle = 1 # the cycle where the last ID cycle happened
        most_recent_stall = 0 # 0 is a placeholder
        while True:
            # current instruction cycles to stages, key:cycle value:stage, this is then appended to the executed instruction list
            current_instruction = {}

            # fetch instruction and stores the cycle data
            instruction = self.instructions[instruction_counter] # using instruction_counter as key, fetch corresponding instruction
            IF_cycle = last_ID_cycle
            current_instruction[IF_cycle] = "IF" # this adds key:cycle value:stage into the current instruction dictionary
            
            # between each IF stage and ID stage, check for stalled cycles
            # while checking for stalled cycles, also check if stalled cycles is continuous, if there's any break in stalled cycle nums,
            # then the next stage's cycle will be the last continuous stall's cycle + 1, because stalled cycles might have stalls beyond the current stage
            for cycle in range(len(stalled_cycles)-1):
                if stalled_cycles[cycle+1] > IF_cycle: # ignore all stalled cycles before the current IF stage
                    if (stalled_cycles[cycle+1] - stalled_cycles[cycle]) > 1: # there's a break in all of the stalled cycles larger than the IF stage
                        most_recent_stall = stalled_cycles[cycle] # catches the last stall before the ID stage
                        break # once the break is found, there's no more stalls between the IF stage and the ID stage
                    current_instruction[cycle] = "Stall" # adds stalls for all continuous cycles in the stalled cycles list

            # decode the instruction
            # if a loop is present, example: ['Loop:', 'L.D', 'F0', '0($2)'], ':' in index 0 indicates a loop, so start decoding from index 1, else decode from 0
            # opcode_index = 1 if ':' in instruction[0] else 0
            opcode = instruction[opcode_index] # sometimes a line of instructions is just the label
            try: op_one = instruction[opcode_index+1] 
            except Exception: pass # ignore if there's only a label
            try: op_two = instruction[opcode_index+2]
            except Exception: pass 
            try: op_three = instruction[opcode_index+3]
            except Exception: pass 

            op_one = self.instructions[instruction_counter].op_one_
            
            
            # stores the cycle information for the ID stage
            ID_cycle = most_recent_stall+1
            last_ID_cycle = ID_cycle # change the last ID cycle for next iteration
            current_instruction[ID_cycle] = "ID"

            # finds out whether the registers used are ok to be read/written to
            # adds stalls when registers are not ok being read/written to
            source_register_one = source_register_two = destination_register = "" # place holder
            all_opcodes = ["ADD","ADDI","ADD.D","SUB","SUB.D","MUL.D","DIV.D","L.D","LW","S.D","SW","BEQ","BNE"] # J is not included as it does not use registers
            if opcode in all_opcodes:
                if opcode in all_opcodes[:7]: # all ALU instructions write to operand one and read from operand two and three
                    destination_register = op_one
                    source_register_one = op_two
                    source_register_two = op_three
                if opcode in all_opcodes[7:9]: # LD writes to operand one
                    destination_register = op_one
                if opcode in all_opcodes[9:11]: # SD reads from operand one
                    source_register_one = op_one # don't worry about cache here, this is just decoding the instruction
                if opcode in all_opcodes[11:]:
                    source_register_one = op_one
                    source_register_two = op_two

            # these two lines find the largest cycle to stall until, if Any registers aren't ready to be read/writeen to
            largest_cycle = max(self.registers.retrieve(R).get_read_cycle() for R in [destination_register, source_register_one, source_register_two] if R)
            largest_cycle = max(largest_cycle, self.registers.retrieve(R).get_write_cycle() for R in [destination_register, source_register_one, source_register_two] if R)

            for i in range(ID_cycle+1, largest_cycle):
                stalled_cycles.append(i)

            # adds stalls between the ID and EX stages, identicle to the chunk above, can make a function that accepts a min-cycle and the stalled cycles list
            for cycle in range(len(stalled_cycles)-1):
                if stalled_cycles[cycle+1] > ID_cycle: 
                    if (stalled_cycles[cycle+1] - stalled_cycles[cycle]) > 1: 
                        most_recent_stall = stalled_cycles[cycle]
                        break
                    current_instruction[cycle] = "Stall"

            current_cycle = stalled_cycles[-1]+1 if len(stalled_cycles) > 0 else current_cycle+1 # problem is that stalled cycles will be shared by all instructions, so last index doesnt work

            # execute the instruction
            # assumes the right number of operands are present for the given opcode
            if opcode == "L.D": # L.D Fa, Offset(addr), Load a floating point value into Fa
                op_two = op_two.replace(')', '').split('(')
                offset, address = op_two[0], op_two[1]

                # checks cache
                if address in self.cache:
                    self.registers.write_to(_id=op_one, _data=self.memory.retrieve_at_address(_address=address, _offset=offset))
                break

            if opcode == "S.D": # S.D Fa, Offset(addr), Store a floating point value from Fa
                pass
            if opcode == "LI": # LI $d, IMM64 -Integer Immediate, Load Load a 64 bit Integer Immediate into $d
                pass
            if opcode == "LW": # LW $d, Offset(addr), Load an integer value into $d
                pass
            if opcode == "SW": # SW $s, Offset(addr), Store an integer from $s
                pass
            if opcode == "ADD": # ADD $d, $s, $t - Integer add, $d = $s + $t
                pass
            if opcode == "ADDI": # ADDI $d, $s, immediate – Integer Add with Immediate, $d = $s + immediate
                pass
            if opcode == "ADD.D":# ADD.D Fd, Fs, Ft – Floating Point Add, Fd = Fs + Ft
                pass
            if opcode == "SUB": # SUB $d, $s, $t -Integer Subtract, $d = $s - $t
                pass            
            if opcode == "SUB.D": # SUB.D Fd, Fs, Ft – Floating Point Subtract, Fd = Fs - Ft
                pass
            if opcode == "MUL.D": # MUL.D Fd, Fs, Ft -Floating Point Multiply, Fd = Fs X Ft
                pass
            if opcode == "DIV.D": # DIV.D Fd, Fs, Ft – Floating Point Divide, Fd = Fs ÷ Ft
                pass
            if opcode == "BEQ": # BEQ $S, $T, OFF18 - Branch to offset if equal, IF $S = $T, PC += OFF18±
                pass
            if opcode == "BNE": # BNE $S, $T, OFF18 - Branch to offset if not equal, IF $S ≠ $T, PC += OFF18±
                pass
            if opcode == 'J': # J ADDR28 - Unconditional jump to addr, PC = PC31:28 :: ADDR28∅
                pass
            



            opcode_index = opcode = op_one = op_two = op_three = None # flushes key variables between iterations

    # prototype function
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
    pipeline.print_all_loops_and_addresses()

    pipeline.execute_lines()
    # pipeline.write_to_excel()
