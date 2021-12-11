### CMSC 411 Project ###
import os
import sys
from typing import Optional
import xlwt

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
            return f"Register: {self.id_}\tData: {self.data_}    \t\tRead/Write Cycles:{self.read_cycle}, {self.write_cycle}"
            
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
        def set_read_cycle(self,cycle=0):
            self.read_cycle = cycle
        def set_write_cycle(self,cycle=0):
            self.write_cycle = cycle

    # the two types of registers
    class FPRegister(Register):
        def __init__(self, _data=0.0, _id=""):
            super().__init__(_data=_data, _id=_id)
        def set_data(self, _data=0.0):
            self.data_ = float(_data) # type checking by type casting lol
    class IntRegister(Register):
        def __init__(self, _data=0, _id=""):
            super().__init__(_data=_data, _id=_id)
        def set_data(self, _data=0):
            self.data_ = int(_data)

class Memory:
    """
    Memory Simulation, just a class with a list in it,
    default parameter for the data_set, if no data_set is used then it will use the default
    """
    def __init__(self, data_set=[45,12,0,92,10,135,254,127,18,4,55,8,2,98,13,5,233,158,167]):
        self.memory_ = data_set
        self.length_ = len(self.memory_)
    
    # address will either be a single int immediate or an int register, with an optional offset
    # when a register is found, retrieve the value at that regsister and pass its value as the address, pass offset as well if found
    def retrieve_at_address(self,  _address:int, _offset=0):
        """ 
        When using this function, the offset is assumed to be 0 unless another offset is passed to it
        Returns memory at address at given offset
        """
        _address = int(_address) + int(_offset) # adds both together to get the actual address
        _address %= self.length_ # loops around
        return self.memory_[_address]
    
    def write_to_address(self, _data, _address, _offset=0):
        """ Identical to the retrieve at function """
        _address = _address.replace('$', '') 
        _address = int(_address) + int(_offset)
        _address %= self.length_
        self.memory_[_address] = _data

    # getter function
    def get_length(self):
        return self.length_

    def print_all_memory(self):
        print("\nAll memory location and data")
        for i in range(self.length_):
            print(f"Address: {i}\tData: {self.memory_[i]}")


class Instruction:
    """ Each instruction object tracks their own labels, opcode and operands """
    def __init__(self, _label="", _opcode="", _op_one="", _op_two="", _op_three="") -> None:
        self.opcode_ = _opcode
        self.label_ = _label
        self.op_one_ = _op_one
        self.op_two_ = _op_two
        self.op_three_ = _op_three

    def __str__(self) -> str:
        if self.opcode_ == "":
            return f"{self.label_}\n"
        if self.op_one_ == "":
            return f"{self.label_} {self.opcode_}\n"
        if self.op_two_ == "":
            return f"{self.label_} {self.opcode_} {self.op_one_}\n"
        if self.op_three_ == "":
            return f"{self.label_} {self.opcode_} {self.op_one_}, {self.op_two_}\n"
        return f"{self.label_} {self.opcode_} {self.op_one_}, {self.op_two_}, {self.op_three_}\n"
    
    def print_instruction(self):
        print(f"Label: {self.label_}\tOpcode: {self.opcode_}\tOp One: {self.op_one_}\tOp Two: {self.op_two_}\tOp Three: {self.op_three_}\n")

class Pipeline:
    """
    Pipeline parses the text file into a list of instruction lists, 
    a two dimensional array where each index of the list is a list of label, opcode, all the operands for every line of the text file
    """
    def __init__(self, _fileName="test.txt"):
        self.instructions = {} # holds a dictionary of instructions, with keys:instruction address and value:instructions
        self.loops = {} # tracks where loops begin, key:loop name, value:[instruction's address, 1/0 where 1 = last taken and 0 = last not taken]

        # current format of executed instructions:
        # list of dictionaries, index:executed instructions, key:cycle, value:dictionary of stages
        self.insExecuted = []
        self.registers = Registers()
        self.memory = Memory()
        # to modify cache do self.cache[set#][1] = address and self.cache[set#] = data
        self.cache = {0:[0, None, None],1:[0, None, None],2:[0, None, None],3:[0, None, None]} # key:set # (mem address % len(cache)), value:[dirty bit, memory address, data], dirty bit == 1 when data has been altered
        self.cache_size = 4 # 4 sets

        all_instructions = Pipeline.parser()
        counter = 0 # instruction address counter, first instruction is at address 0000
        for instruction in all_instructions:
            if ':' in instruction[0]: # if a loop is found, then add it to the dictionary, key:loop name value:loop address
                loop_name = instruction[0].replace(':', '')
                self.loops[loop_name] = [counter, 1] # 1 indicate the branch will initially be taken
            self.instructions[counter] = instruction
            counter += 1
    
    def __str__(self,instruction): # string representation of an instruction list
        if len(instruction) <= 1:
            return f"{instruction[0]}"
        if len(instruction) == 2:
            return f"{instruction[0]} {instruction[1]}"
        if len(instruction) == 3:
            return f"{instruction[0]} {instruction[1]}, {instruction[2]}"
        if len(instruction) == 4:
            return f"{instruction[0]} {instruction[1]} {instruction[2]}, {instruction[3]}"
        return f"{instruction[0]} {instruction[1]} {instruction[2]}, {instruction[3]}, {instruction[4]}"

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

    # for testing
    def print_all_instruction_objects(self):
        for instruction_address in self.instructions:
            print(instruction_address, self.instructions[instruction_address])
    def print_all_loops_and_addresses(self):
        for loops in self.loops:
            print("Address:", self.loops[loops], "Name:", loops)

    def execute(self):
        def registers_check(status='R'): # status is Read by defualt, anything else checks for write, which checks for the largest read-ready and the largest write-ready cycles respectively
            """ add stalls up to the largest cycle required in order to avoid a data hazard """
            source_register_one = source_register_two = destination_register = "" # place holder
            all_opcodes = ["ADD","ADDI","ADD.D","SUB","SUB.D","MUL.D","DIV.D","L.D","LW","S.D","SW","BEQ","BNE"] # J is not included as it does not use registers
            if opcode in all_opcodes:
                if opcode in all_opcodes[:7]: # all ALU instructions write to operand one and read from operand two and three
                    destination_register = op_one
                    source_register_one = op_two
                    source_register_two = op_three
                if opcode in all_opcodes[7:9]: # LD writes to operand one
                    destination_register = op_one
                if opcode in all_opcodes[9:11]: # SD reads from operand one, don't worry about the destination/memory here
                    source_register_one = op_one # don't worry about cache here, this is just decoding the instruction
                if opcode in all_opcodes[11:]:
                    source_register_one = op_one
                    source_register_two = op_two
            # finds the largest read/write cycles, largest cycle is whichever one requested
            largest_read_cycle = max((self.registers.retrieve(R).get_read_cycle() for R in [destination_register, source_register_one, source_register_two] if R), default=0)
            largest_write_cycle = max((self.registers.retrieve(R).get_write_cycle() for R in [destination_register, source_register_one, source_register_two] if R),default=0)
            largest_cycle = largest_read_cycle if status == 'R' else largest_write_cycle
            if largest_cycle > ID_cycle:
                for i in range(ID_cycle+1, largest_cycle):
                    if i not in stalled_cycles: # no need to add repeated stall cycles
                        stalled_cycles.append(i) 
                        print(f"Stalled cycle added: {i}") # debug

        def write_stalled_cycles(smallest_cycle:int):
            """
            helper function that iterates through the stalled cycles to find the smallest stalled cycle larger than a given cycle
            the given cycle is usually the most recent stage's cycle
            example: IF cycle happens to be 5, this function will check if cycle 6 is in the stalled cycles list
            If cycle 6 is found, then keep adding stalls into the current instruction until there's a skip in the cycles, which indicates the end of the stalls
            """
            most_recent_stall = smallest_cycle
            if smallest_cycle+1 in stalled_cycles:
                for cycle in stalled_cycles:
                    if cycle == most_recent_stall+1: 
                        current_instruction[cycle] = "Stall" 
                        most_recent_stall = cycle
            return most_recent_stall # if no immediate stalls are found | if there's a break between stalls


        instruction_counter = 0 
        stalled_cycles = [] # list of stalled cycles
        last_ID_cycle = 1 # tracks the last ID cycle  
        for i in range(len(self.instructions)): 
            # key:cycle value:{0:raw instruction line, IF cycle:IF, IF-ID stalls, ID cycle:ID, ID-EX stalls, all EX cycles:EX(#),...
            #                               ... EX-MEM stalls, all MEM cycles:MEM, WB cycle:WB}
            current_instruction = {}

            # fetch instruction and stores the cycle data
            instruction = self.instructions[instruction_counter] # using instruction_counter as key, fetch corresponding instruction
            IF_cycle = last_ID_cycle
            current_instruction[0] = self.__str__(self.instructions[instruction_counter])
            current_instruction[IF_cycle] = "IF" # this adds key:cycle value:stage into the current instruction dictionary
            instruction_counter += 1 # after fetching, increment instruction counter
            
            # between each IF-ID stage, write any stalled cycles to the current instruction
            most_recent_stall = write_stalled_cycles(IF_cycle)

            # decode the instruction
            # if a loop is present, example: ['Loop:', 'L.D', 'F0', '0($2)'], ':' in index 0 indicates a loop, so start decoding from index 1, else decode from 0
            opcode_index = 1 if ':' in instruction[0] else 0
            try: opcode = instruction[opcode_index] # sometimes a line of instructions is just the label
            except Exception: opcode = "" 
            try: op_one = instruction[opcode_index+1] 
            except Exception: op_one = ""
            try: op_two = instruction[opcode_index+2]
            except Exception: op_two = "" 
            try: op_three = instruction[opcode_index+3]
            except Exception: op_three = ""
            
            # stores the cycle information for the ID stage
            ID_cycle = most_recent_stall+1
            last_ID_cycle = ID_cycle # change the last ID cycle for next iteration
            current_instruction[ID_cycle] = "ID"

            # checks the stalled cycles list
            registers_check() # checks for the largest read cycle to wait for
            most_recent_stall = write_stalled_cycles(ID_cycle)

            # execute the instruction
            # assumes the instruction given will have the correct operands with the supplied opcode
            if opcode == "L.D" or opcode == "LW": # L.D Fa, Offset(addr), LW $d, Offset(addr) -> Load a floating point/int value into Fa/$d
                # if LD is detected, pretty much just skip the Ex stage and enter the MEM stage(s)
                EX_cycle = most_recent_stall+1
                current_instruction[EX_cycle] = "EX"
                most_recent_stall = write_stalled_cycles(EX_cycle)

                address = offset = 0 # in case offset not present, initialize it to 0 as a place holder
                if '$' in op_two: # indicate register is being used
                    if '(' in op_two: # indicates offset presence
                        op_two = op_two.replace(')', '').split('(')
                        offset, address = op_two[0], op_two[1]
                    # regardless of whether the offset is present, the address here will always be the return value of the register
                    address = self.registers.retrieve(address).get_data() # sets address to value of the register
    
                elif '$' not in op_two: # basic input validation
                    raise Exception("Bruh, you need a register for load instructions")

                address += int(offset) # combine the address and the offset into one int immediate address
                address %= self.memory.get_length() # this will yield the actual mem address, as any addresses > 18 will not be accepted

                registers_check('w') # register's write-readiness check

                # self.cache = {key:set# : Value:[dirty bit, memory address, data]}
                cache_set = address % self.cache_size
                MEM_cycle = most_recent_stall+1
                most_recent_stall = write_stalled_cycles(MEM_cycle)
                if self.cache[cache_set][1] != address: # this means the address at the required cache set is not the same, ie. a miss
                    stalled_cycles.append(MEM_cycle+1)
                    stalled_cycles.append(MEM_cycle+2)

                    # if cahe miss, there will be three MEM stages after EX
                    current_instruction[MEM_cycle] = current_instruction[MEM_cycle+1] = current_instruction[MEM_cycle+2] = "MEM"
                    most_recent_stall = MEM_cycle+2 # given the possibility of multiple MEM stages, most recent stall will always be the last MEM stage

                    # write to cache
                    self.cache[cache_set] = [0, address, self.memory.retrieve_at_address(address)]

                elif self.cache[cache_set][1] == address: # mem address already in cache
                    self.registers.write_to(_id=op_one, _data=self.memory.retrieve_at_address(_address=address, _offset=offset))
                    current_instruction[MEM_cycle] = "MEM"
                    most_recent_stall = MEM_cycle

                # end of EX and MEM stages
                self.registers.write_to(_id=op_one, _data=self.cache[cache_set][2]) # write to register using cache
                
                WB_cycle = most_recent_stall+1
                current_instruction[WB_cycle] = "WB"

                self.registers.retrieve(op_one).set_read_cycle(cycle=most_recent_stall) # the register used will not be ready until the end of MEM stage
                self.registers.retrieve(op_one).set_write_cycle(cycle=WB_cycle) # register will not be ready to be written to until WB
                self.insExecuted.append(current_instruction)
                
                opcode_index = opcode = op_one = op_two = op_three = None # flushes key variables between iterations
                
            if opcode == "S.D": # S.D Fa, Offset(addr), Store a floating point value from Fa
                EX_cycle = most_recent_stall+1
                current_instruction[EX_cycle] = "EX"
                most_recent_stall = write_stalled_cycles(EX_cycle)

                address = offset = 0

            if opcode == "LI": # LI $d, IMM64 -Integer Immediate, Load Load a 64 bit Integer Immediate into $d
                # identical to L.D but without register-read-check and cache check
                EX_cycle = most_recent_stall+1
                current_instruction[EX_cycle] = "EX"
                most_recent_stall = write_stalled_cycles(EX_cycle)

                registers_check('w') # register's write-readiness check
                MEM_cycle = most_recent_stall+1
                current_instruction[MEM_cycle] = "MEM"
                most_recent_stall = write_stalled_cycles(MEM_cycle)
                self.registers.write_to(_id=op_one, _data=op_two) # unsure if immediates can have offsets, something like 7(18) will not be accepted for now

                WB_cycle = most_recent_stall+1
                current_instruction[WB_cycle] = "WB"
                self.insExecuted.append(current_instruction)
                opcode_index = opcode = op_one = op_two = op_three = None

            if opcode == "SW": # SW $s, Offset(addr), Store an integer from $s
                pass
            if opcode == "ADD" or opcode == "ADD.D": # ADD $d, $s, $t | ADD.D Fd, Fs, Ft -> Integer add, $d = $s + $t | Floating Point Add, Fd = Fs + Ft
                pass
            if opcode == "ADDI": # ADDI $d, $s, immediate – Integer Add with Immediate, $d = $s + immediate
                pass
            if opcode == "SUB" or opcode == "SUB.D": # SUB $d, $s, $t | SUB.D Fd, Fs, Ft -> Integer Subtract, $d = $s - $t | Floating Point Subtract, Fd = Fs - Ft
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
        wb = xlwt.Workbook(encoding='utf-8')
        
        sheet1 = wb.add_sheet(_filename)
        sheet1.col(0).width = 256 * 18 # some arbitrary width big enough to theoretically fit most instructions
        sheet1.set_panes_frozen(True)
        sheet1.set_vert_split_pos(1) 
        # prints out cycle#s on top
        end_cycle = max(self.insExecuted[-1].keys()) # end cycle is the largest key of the last instruction executed
        sheet1.write(0,0, "Cycle", xlwt.easyxf("font: bold on; align: horiz right"))
        for i in range(1, end_cycle+1):
            sheet1.write(0, i, i, xlwt.easyxf("align: horiz left"))
        
        for i in range(1, len(self.insExecuted)+1):
            # write(row, column, item)
            for cycle in self.insExecuted[i-1]:
                sheet1.write(i,cycle, self.insExecuted[i-1][cycle])
        wb.save(_filename)
        os.startfile(_filename)

if __name__ == '__main__':
    registers = Registers() # all registers
    memory = Memory() # all memory
    # registers.print_all_registers()
    # memory.print_all_memory()
    pipeline = Pipeline()
    # pipeline.print_all_instruction_objects()
    # pipeline.print_all_loops_and_addresses()

    pipeline.execute()
    pipeline.registers.print_all_registers()
    pipeline.write_to_excel()
