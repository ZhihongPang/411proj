### CMSC 411 Project ###
import os
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
        index = -1 # place holder
        if len(_id) == 2:
            index = int(_id[1])
        if len(_id) == 3 :
            index = int(f"{_id[1]}{_id[2]}") # weird looking code, casts an f-string with the two _id positions into an int
        
        # registers with index not in range of 0, 31 or ids that doesn't start with F or $ or id length is too long
        if not (0 <= index <= 31) or _id[0] not in ['F', '$'] or (len(_id) not in [2,3]):
            raise Exception(f"{_id} is not a valid register!") # Register.retrieve() received an invalid register name.

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
        except Exception: print(f"\"{_id}\" is not a valid register!")
        else: temp.set_data(_data)

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
        def set_read_cycle(self,cycle=0):
            self.read_cycle = cycle
        def set_write_cycle(self,cycle=0):
            self.write_cycle = cycle    
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
        self.loops = {} # tracks where loops begin, key:loop name, value:instruction's address
        self.branches = {} # branch predictor, key:address of branch, value: 1|0 where 1 == taken and 0 == not taken

        # current format of executed instructions:
        # list of dictionaries, index:executed instructions, key:cycle, value:dictionary of stages
        self.insExecuted = []
        self.registers = Registers()
        self.memory = Memory()
        # to modify cache do self.cache[set#][1] = address and self.cache[set#] = data
        # key:set # (mem address % len(cache)), value:[dirty bit, memory address, data, forward cycle], dirty bit == 1 when data has been altered
        self.cache = {0:[0, None, None, 0],1:[0, None, None, 0],2:[0, None, None, 0],3:[0, None, None, 0]} 
        self.cache_size = 4 # 4 sets

        all_instructions = Pipeline.parser(_fileName)
        counter = 0 # instruction address counter, first instruction is at address 0000
        for instruction in all_instructions:
            opcode_shift = 1 if ':' in instruction[0] else 0 # opcode in index 1 if label exists, else at index 0
            if ':' in instruction[0]: # if a loop is found, then add it to the dictionary, key:loop name value:loop address
                loop_name = instruction[0].replace(':', '')
                self.loops[loop_name] = counter 
            if instruction[opcode_shift] == "BNE" or instruction[opcode_shift] == "BEQ":
                self.branches[counter] = 1 # all branches are taken initially by default

            self.instructions[counter] = instruction
            counter += 1
    
    def __str__(self,instruction): # overly complicated just so the commas are in the correct places ;)
        opcode_shift = 1 if ':' in instruction[0] else 0
        if len(instruction) <= 1:
            return f"{instruction[0]}"
        if len(instruction) == 2:
            return f"{instruction[0]} {instruction[1]}"
        if len(instruction) == 3:
            if opcode_shift:
                return f"{instruction[0]} {instruction[1]}, {instruction[2]}"
            return f"{instruction[0]} {instruction[1]} {instruction[2]}"
        if len(instruction) == 4:
            if opcode_shift:
                return f"{instruction[0]} {instruction[1]} {instruction[2]}, {instruction[3]}"
            return f"{instruction[0]} {instruction[1]}, {instruction[2]}, {instruction[3]}"
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
        def registers_check(current_cycle=0,status='R'): # status is Read by defualt, anything else checks for write, which checks for the largest read-ready and the largest write-ready cycles respectively
            """ add stalls up to the largest cycle required in order to avoid a data hazard """
            all_opcodes = ["ADD","ADD.D","SUB","SUB.D","MUL.D","DIV.D","ADDI","L.D","LW","S.D","SW","BEQ","BNE", "J"]
            source_register_one = source_register_two = destination_register = "" # place holder
            if opcode in all_opcodes:
                if opcode in all_opcodes[:6]: # most ALU instructions write to operand one and read from operand two and three
                    destination_register = op_one
                    source_register_one = op_two
                    source_register_two = op_three
                if opcode in all_opcodes[6]: # ADDI has to be special
                    destination_register = op_one
                    source_register_one = op_two
                if opcode in all_opcodes[7:9]: # LD/LW
                    destination_register = op_one
                    source_register_one = op_two.replace(')', '').split('(')
                    source_register_one = source_register_one[1]
                    # print("Load register check:",source_register_one)
                if opcode in all_opcodes[9:11]: # SD/SW
                    source_register_one = op_one
                    try: parsed = op_two.replace(")","").split("(")
                    except Exception: parsed = op_two
                    destination_register = parsed[1]
                    # print("Op two: ", op_two)
                    # print("Store register check:",destination_register)
                if opcode in all_opcodes[11:13]: # Branches except J
                    source_register_one = op_one
                    source_register_two = op_two
            # finds the largest read/write cycles, largest cycle is whichever one requested
            largest_read_cycle = max((self.registers.retrieve(R).get_read_cycle() for R in [destination_register, source_register_one, source_register_two] if R), default=0)
            largest_write_cycle = max((self.registers.retrieve(R).get_write_cycle() for R in [destination_register, source_register_one, source_register_two] if R),default=0)
            largest_cycle = largest_read_cycle if status == 'R' else largest_write_cycle
            if largest_cycle > current_cycle:
                for i in range(current_cycle+1, largest_cycle):
                    if i not in stalled_cycles: # no need to add repeated stall cycles
                        stalled_cycles.append(i) 
                        print(f"Stalled cycle added: {i}") # debug

        def write_stalled_cycles(smallest_cycle:int):
            """
            if the cycle immediately following the given cycle is a stall, then add stalls until a break is found,\n
            when given a stage, it will fill in possible stalls between the given stage and the next, then return the cycle right before the next stage starts\n

            example: say IF cycle happens to be 5, this function will check if cycle 6 is in the stalled cycles list
            If cycle 6 is found, then keep adding stalls into the current instruction until there's a skip in the cycles, which indicates the end of the stalls, 
            let cycles 6-10 all be stall cycles, it will return 10 to indicate end of stall
            """
            most_recent_stall = smallest_cycle
            if smallest_cycle+1 in stalled_cycles:
                for cycle in stalled_cycles:
                    if cycle == most_recent_stall+1: 
                        current_instruction[cycle] = "Stall" 
                        most_recent_stall = cycle
            return most_recent_stall # if no immediate stalls are found | if there's a break between stalls
        
        def mem_check(cycle): # possible fix for the overlapping mem stages problem
            """ 
            takes in the cycle which the first mem stage is supposed to go, if that stage is already a mem stage in the last executed instruction,
            then add stalls until the stage is no longer in the list, at that point, write in the mem stages to the current instruction
            return the last mem cycle
            """
            # HOT FIX to the overlapping MEM stages problem, it works for example3
            # have not tested it for any other cases other than example3, I don't now if this work for any other cases
            try:
                if self.insExecuted[-1][cycle] == "MEM":
                    stalled_cycles.append(cycle)
                    current_instruction[cycle] = "Stall"
                    cycle += 1
                    current_instruction[cycle] = "MEM"
                    if self.insExecuted[-1][cycle] == "MEM":
                        stalled_cycles.append(cycle)
                        current_instruction[cycle] = "Stall"
                        cycle += 1
                        current_instruction[cycle] = "MEM"
                        if self.insExecuted[-1][cycle] == "MEM":
                            stalled_cycles.append(cycle)
                            current_instruction[cycle] = "Stall"
                            return cycle
                        return cycle
                    return cycle
            except Exception: pass
            return cycle # holy shit this is such a mess of a fix

        instruction_counter = 0 
        stalled_cycles = [] # list of stalled cycles
        last_ID_cycle = 1 # tracks the last ID cycle  
        while instruction_counter != len(self.instructions):
            # key:cycle value:{0:raw instruction line, IF cycle:IF, IF-ID stalls, ID cycle:ID, ID-EX stalls, all EX cycles:EX(#),...
            #                               ... EX-MEM stalls, all MEM cycles:MEM, WB cycle:WB}
            current_instruction = {}

            # fetch instruction and stores the cycle data
            try: instruction = self.instructions[instruction_counter] # using instruction_counter as key, fetch corresponding instruction
            except Exception: break
            IF_cycle = last_ID_cycle
            current_instruction[0] = self.__str__(self.instructions[instruction_counter])
            current_instruction[IF_cycle] = "IF" # this adds key:cycle value:stage into the current instruction dictionary
            instruction_counter += 1 # after fetching, increment instruction counter
            
            # between each IF-ID stage, write any stalled cycles to the current instruction
            most_recent_stall = write_stalled_cycles(IF_cycle)

            # decode the instruction
            # if a loop is present, example: ['Loop:', 'L.D', 'F0', '0($2)'], ':' in index 0 indicates a loop, so start decoding from index 1, else decode from 0
            opcode_index = 1 if ':' in instruction[0] else 0
            label = instruction[0].replace(':', '') if ':' in instruction[0] else ""
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
            registers_check(current_cycle=ID_cycle) # checks for the largest read cycle to wait for
            most_recent_stall = write_stalled_cycles(ID_cycle)

            # execute the instruction
            # assumes the instruction given will have the correct operands with the supplied opcode
            if opcode == "L.D" or opcode == "LW": # L.D Fa, Offset(addr), LW $d, Offset(addr) -> Load a floating point/int value into Fa/$d
                # input validation for the respective opcodes
                if opcode == "L.D" and 'F' not in op_one:
                    raise Exception(f"Register {op_one} is invalid, opcode L.D requires a floating point register as the first operand!")
                if opcode == "LW" and '$' not in op_one:
                    raise Exception(f"Register {op_one} is invalid, opcode LW requires an integer register as the first operand!")

                # if LD is detected, pretty much just skip the Ex stage and enter the MEM stage(s)
                EX_cycle = most_recent_stall+1
                current_instruction[EX_cycle] = "EX"
                most_recent_stall = write_stalled_cycles(EX_cycle)

                registers_check(current_cycle=EX_cycle,status='w') # register's write-readiness check

                address = offset = 0 # in case offset not present, initialize it to 0 as a place holder
                if '$' in op_two: # indicate register is being used
                    if '(' in op_two: # indicates offset presence
                        op_two = op_two.replace(')', '').split('(')
                        offset, id = op_two[0], op_two[1]
                    # regardless of whether the offset is present, the address here will always be the return value of the register
                    address = self.registers.retrieve(id).get_data() # sets address to value of the register
    
                elif '$' not in op_two: # basic input validation
                    raise Exception("Bruh, you need a register for load instructions")

                address += int(offset) # combine the address and the offset into one int immediate address
                address %= self.memory.get_length() # this will yield the actual mem address, as any addresses > 18 will not be accepted

                # self.cache = {key:set# : Value:[dirty bit, memory address, data, forward cycle]}
                cache_set = address % self.cache_size
                MEM_cycle = most_recent_stall+1
                most_recent_stall = write_stalled_cycles(MEM_cycle)
                if self.cache[cache_set][1] != address: # this means the address at the required cache set is not the same, ie. a miss
                    if self.cache[cache_set][0] != 0: # cached memory has been altered, write previous cached memory address back to memory
                        self.memory.write_to_address(_data=self.cache[cache_set][1], _address=self.cache[cache_set][2])

                    stalled_cycles.append(MEM_cycle+1)
                    stalled_cycles.append(MEM_cycle+2)

                    # if cahe miss, there will be three MEM stages after EX
                    most_recent_stall = mem_check(most_recent_stall)
                    current_instruction[most_recent_stall] = current_instruction[most_recent_stall+1] = current_instruction[most_recent_stall+2] = "MEM"
                    most_recent_stall = MEM_cycle+2 # given the possibility of multiple MEM stages, most recent stall will always be the last MEM stage

                    # write to cache
                    self.cache[cache_set] = [0, address, self.memory.retrieve_at_address(address), most_recent_stall] # cache/memory can be forwarded at end of mem

                elif self.cache[cache_set][1] == address: # mem address already in cache
                    if self.cache[cache_set][3] > MEM_cycle:
                        most_recent_stall = write_stalled_cycles(self.cache[cache_set][3]) # if the memory in cache is not yet ready, stall between ex and mem until ok
                        most_recent_stall = mem_check(most_recent_stall)
                        MEM_cycle = most_recent_stall
                        current_instruction[MEM_cycle] = "MEM"
                    else:
                        # most_recent_stall = MEM_cycle
                        most_recent_stall = mem_check(most_recent_stall)
                        MEM_cycle = most_recent_stall
                        current_instruction[MEM_cycle] = "MEM"

                # end of EX and MEM stages
                self.registers.write_to(_id=op_one, _data=self.cache[cache_set][2]) # write to register using cache
                
                WB_cycle = most_recent_stall+1
                current_instruction[WB_cycle] = "WB"

                self.registers.retrieve(op_one).set_read_cycle(cycle=most_recent_stall) # load instructions forwards at MEM stage
                self.registers.retrieve(op_one).set_write_cycle(cycle=WB_cycle) # register will not be ready to be written to until WB
                self.insExecuted.append(current_instruction)
                
                opcode_index = opcode = op_one = op_two = op_three = None # flushes key variables between iterations

                # print(f"Cache in cycle: {instruction_counter} after load")
                # for stuff in self.cache:
                #     print(f"Set: {stuff} Cache: [Dirty bit: {self.cache[stuff][0]}, Address: {self.cache[stuff][1]}, Data: {self.cache[stuff][2]}, Forward Cycle: {self.cache[stuff][3]}]")
                
            if opcode == "S.D" or opcode == "SW": # S.D Fa, Offset(addr) | SW $s, Offset(addr) -> Store a floating point value from Fa | Store an integer from $s
                if opcode == "S.D" and 'F' not in op_one:
                    raise Exception(f"Register {op_one} is invalid, opcode S.D requires a floating point register as the first operand!")
                if opcode == "SW" and '$' not in op_one:
                    raise Exception(f"Register {op_one} is invalid, opcode SW requires an integer register as the first operand!")

                # execute cycle
                EX_cycle = most_recent_stall+1
                current_instruction[EX_cycle] = "EX"
                most_recent_stall = write_stalled_cycles(EX_cycle)

                # beginning of mem, similar to LD/LW
                # obtains the raw address immediate
                address = offset = 0
                if '$' in op_two:
                    if '(' in op_two:
                        op_two = op_two.replace(')', '').split('(')
                        offset, id = op_two[0], op_two[1]
                    # regardless of whether the offset is present, the address will always be the return value of the register
                    address = self.registers.retrieve(id).get_data()
                elif '$' not in op_two: # basic input validation
                    raise Exception("Bruh, you need a register for store instructions")
                address += int(offset) # combine the address and the offset into one immediate
                address %= self.memory.get_length() # this will yield the actual mem address, as any addresses > 18 will not be accepted

                registers_check(current_cycle=EX_cycle) # register's read-readiness check

                # store does not interact with cache
                # but then when will memory in cache ever be modified? since store goes directly to memory,
                # the only use for cache is for quicker memory access, but will never actualy write anything from cache back to memory
                MEM_cycle = most_recent_stall+1
                most_recent_stall = write_stalled_cycles(MEM_cycle)
                data = self.registers.retrieve(op_one).get_data()
                # current_instruction[MEM_cycle] = "MEM"
                # most_recent_stall = MEM_cycle
                most_recent_stall = mem_check(most_recent_stall)
                MEM_cycle = most_recent_stall
                current_instruction[MEM_cycle] = "MEM"

                self.memory.write_to_address(_data=data, _address=address) # writes directly to memory
                
                WB_cycle = most_recent_stall+1
                current_instruction[WB_cycle] = "WB"

                self.insExecuted.append(current_instruction)
                opcode_index = opcode = op_one = op_two = op_three = None
                
            if opcode == "LI" or opcode == "ADDI": # LI $d, IMM64 | ADDI $d, $s, immediate -> Integer Immediate, Load a 64 bit Integer Immediate into $d | $d = $s + immediate
                # identical to L.D but without register-read-check and cache check
                EX_cycle = most_recent_stall+1
                current_instruction[EX_cycle] = "EX"
                most_recent_stall = write_stalled_cycles(EX_cycle)

                if opcode == "ADDI":
                    registers_check(current_cycle=EX_cycle) # with ADDI, you'll also need to check for read cycles

                registers_check(current_cycle=EX_cycle, status='w') # register's write-readiness check
                MEM_cycle = most_recent_stall+1
                MEM_cycle = mem_check(MEM_cycle)
                current_instruction[MEM_cycle] = "MEM"

                most_recent_stall = write_stalled_cycles(MEM_cycle)
                data = op_two if opcode == "LI" else op_three # data is the immediate, immediate at op_two if LI, op_three if ADDI
                if opcode == "ADDI":
                    register_data = self.registers.retrieve(op_two).get_data()
                    data = int(data) + int(register_data)
                self.registers.write_to(_id=op_one, _data=data) # unsure if immediates can have offsets, something like 7(18) will not be accepted for now

                WB_cycle = most_recent_stall+1
                current_instruction[WB_cycle] = "WB"
                self.insExecuted.append(current_instruction)
                opcode_index = opcode = op_one = op_two = op_three = None

            # ADD/SUB $d, $s, $t | ADD.D/SUB.D Fd, Fs, Ft -> Integer add/sub, $d = $s +/- $t | Floating Point Add/sub, Fd = Fs +/- Ft
            # MUL.D Fd, Fs, Ft | DIV.D Fd, Fs, Ft -> Floating Point Multiply/Divide, Fd = Fs X/÷ Ft
            if opcode in ["ADD", "ADD.D", "SUB", "SUB.D", "MUL.D", "DIV.D"]: 
                if opcode == "ADD" or opcode == "ADD.D":
                    temp = []
                    temp.append(op_one) if (opcode == "ADD" and '$' not in op_one) or (opcode == "ADD.D" and 'F' not in op_one) else temp.append('')
                    temp.append(op_two) if (opcode == "ADD" and '$' not in op_two) or (opcode == "ADD.D" and 'F' not in op_one) else temp.append('')
                    temp.append(op_three) if (opcode == "ADD" and '$' not in op_three) or (opcode == "ADD.D" and 'F' not in op_one) else temp.append('')
                    if any(temp):
                        raise Exception(f'Instruction: {self.__str__(instruction)} is invalid, opcode {opcode} contains {"Integer" if opcode != "ADD" else "Floating Point"} registers!')
                if opcode == "SUB" or opcode == "SUB.D":
                    temp = []
                    temp.append(op_one) if (opcode == "SUB" and '$' not in op_one) or (opcode == "SUB.D" and 'F' not in op_one) else temp.append('')
                    temp.append(op_two) if (opcode == "SUB" and '$' not in op_two) or (opcode == "SUB.D" and 'F' not in op_one) else temp.append('')
                    temp.append(op_three) if (opcode == "SUB" and '$' not in op_three) or (opcode == "SUB.D" and 'F' not in op_one) else temp.append('')
                    if any(temp):
                        raise Exception(f'Instruction: {self.__str__(instruction)} is invalid, opcode {opcode} contains {"Integer" if opcode != "SUB" else "Floating Point"} registers!')
                if opcode == "MUL.D" or opcode == "DIV.D":
                    temp = []
                    temp.append(op_one) if 'F' not in op_one else temp.append('')
                    temp.append(op_two) if 'F' not in op_two else temp.append('')
                    temp.append(op_three) if 'F' not in op_three else temp.append('')
                    if any(temp):
                        raise Exception(f'Instruction: {self.__str__(instruction)} is invalid, opcode {opcode} requires all Floating Point registers!')
                
                EX_cycle = most_recent_stall+1
                most_recent_stall = write_stalled_cycles(most_recent_stall)
                EX_cycle = most_recent_stall
                registers_check(current_cycle=EX_cycle) # registers' read-readiness check
                if opcode == "ADD" or opcode == "SUB":
                    current_instruction[most_recent_stall] = "EX"
                if opcode == "ADD.D" or opcode == "SUB.D":
                    current_instruction[most_recent_stall+1] = "A1"
                    current_instruction[most_recent_stall+2] = "A2"
                    most_recent_stall += 2
                if opcode == "MUL.D":
                    counter = 1
                    for i in range(most_recent_stall+1, most_recent_stall+11):
                        current_instruction[i] = f"M{counter}"
                        if i != most_recent_stall+1:
                            if i not in stalled_cycles:
                                stalled_cycles.append(i) 
                        counter += 1
                    most_recent_stall += 10
                if opcode == "DIV.D":
                    counter = 1
                    for i in range(most_recent_stall+1, most_recent_stall+41):
                        current_instruction[i] = f"D{counter}"
                        if i != most_recent_stall+1:
                            if i not in stalled_cycles:
                                stalled_cycles.append(i) 
                        counter += 1
                    most_recent_stall += 40

                registers_check(current_cycle=most_recent_stall, status='w') # registers' write-readiness check
                most_recent_stall = write_stalled_cycles(most_recent_stall)
                MEM_cycle = most_recent_stall+1
                current_instruction[MEM_cycle] = "MEM"
                
                if opcode == "ADD" or opcode == "ADD.D":
                    data = self.registers.retrieve(op_two).get_data() + self.registers.retrieve(op_three).get_data()
                if opcode == "SUB" or opcode == "SUB.D":
                    data = self.registers.retrieve(op_two).get_data() - self.registers.retrieve(op_three).get_data()
                if opcode == "MUL.D":
                    data = self.registers.retrieve(op_two).get_data() * self.registers.retrieve(op_three).get_data()
                if opcode == "DIV.D":
                    data = self.registers.retrieve(op_two).get_data() / self.registers.retrieve(op_three).get_data()
                self.registers.write_to(_id=op_one, _data=data)
                self.registers.retrieve(op_one).set_read_cycle(most_recent_stall)

                most_recent_stall = MEM_cycle
                WB_cycle = most_recent_stall+1
                self.registers.retrieve(op_one).set_write_cycle(most_recent_stall+1)
                current_instruction[WB_cycle] = "WB"
                self.insExecuted.append(current_instruction)
                opcode_index = opcode = op_one = op_two = op_three = None

            if opcode == "BEQ" or opcode == "BNE": # BEQ $S, $T, OFF18 - Branch to offset if equal/not equal, IF $S = $T | IF $S ≠ $T, PC += OFF18±
                address = self.loops[op_three] if op_three in self.loops else op_three # instruction address to jump to, either address of the label or an immediate
                data1 = self.registers.retrieve(op_one).get_data()
                data2 = self.registers.retrieve(op_two).get_data()
                
                if (opcode == "BEQ" and data1 == data2) or (opcode == "BNE" and data1 != data2):
                    instruction_counter = address # a jump is essentially just changing the program counter

                    #updating EX cycle and Most recent stall
                    EX_cycle = most_recent_stall+1
                    most_recent_stall = write_stalled_cycles(EX_cycle)

                    registers_check(current_cycle=EX_cycle) # registers' read-readiness check
                    current_instruction[most_recent_stall] = "EX"
                    self.insExecuted.append(current_instruction)
                

                elif (opcode == "BNE" and data1 == data2) or (opcode == "BEQ" and data1 != data2):                   
                    #updating EX cycle and Most recent stall
                    EX_cycle = most_recent_stall+1
                    most_recent_stall = write_stalled_cycles(EX_cycle)

                    registers_check(current_cycle=EX_cycle) # registers' read-readiness check
                    current_instruction[most_recent_stall] = "EX"
                    
                    self.insExecuted.append(current_instruction)
                    print(instruction_counter)
                    def make_two_dummy():
                        current_instruction = {}
                        instruction_counter = address
                        #setting current instruction to first instruction in the loop
                        current_instruction[0] = self.__str__(self.instructions[instruction_counter])
                        
                        #updating IF cycle and Most recent stall
                        IF_cycle = last_ID_cycle
                        print(last_ID_cycle)
                        most_recent_stall = write_stalled_cycles(IF_cycle)
                        current_instruction[most_recent_stall] = "IF"
                        
                        ID_cycle = IF_cycle + 1
                        most_recent_stall = write_stalled_cycles(ID_cycle)
                        current_instruction[most_recent_stall] = "ID"

                        self.insExecuted.append(current_instruction)
                        
                        current_instruction = {}
                        #setting current instruction to first instruction in the loop
                        current_instruction[0] = self.__str__(self.instructions[instruction_counter+1])
                        
                        #updating IF cycle and Most recent stall
                        IF_cycle = ID_cycle
                        most_recent_stall = write_stalled_cycles(IF_cycle)

                        current_instruction[most_recent_stall] = "IF"
                        self.insExecuted.append(current_instruction)

                        return IF_cycle+1

                    #checking to see if there instructions after the loop if there continue out the loop if not go back to loop
                    try: 
                        if self.instructions[instruction_counter]:
                            last_ID_cycle = make_two_dummy()
                    except Exception: 
                        make_two_dummy()
                
            if opcode == 'J': # J ADDR28 - Unconditional jump to addr, PC = PC31:28 :: ADDR28∅
                address = self.loops[label][0] if label in self.loops else op_three
                instruction_counter = address
            

            opcode_index = opcode = op_one = op_two = op_three = None # flushes key variables between iterations

        print("stalled cycles:")
        for cycle in stalled_cycles:
            print(cycle, end=" ")
        
def run(_files=["example1", "example2", "example3"]): # _files = ["example1", "example2", "example3"]
    _filename = "Hot stuff.xls"
    try: os.remove(_filename) # clean up, makes testing easier
    except Exception: pass

    #write to excel file
    wb = xlwt.Workbook(encoding='utf-8')
    
    for file in _files:
        current_pipeline = Pipeline(f"{file}.txt")
        current_pipeline.execute()

        sheet = wb.add_sheet(file)
        sheet.col(0).width = 256 * 17 # some arbitrary width big enough to theoretically fit most instructions
        sheet.set_panes_frozen('1')
        sheet.set_vert_split_pos(1) # freezes column 1
        # prints out cycle#s on top
        end_cycle = max(current_pipeline.insExecuted[-1].keys()) # end cycle is the largest key of the last instruction executed
        sheet.write(0,0, "Cycle", xlwt.easyxf("font: bold on; align: horiz right"))
        for i in range(1, end_cycle+1):
            sheet.write(0, i, i, xlwt.easyxf("align: horiz left"))
        
        for i in range(1, len(current_pipeline.insExecuted)+1):
            # write(row, column, item)
            print(current_pipeline.insExecuted[i-1][0])
            for cycle in current_pipeline.insExecuted[i-1]:
                sheet.write(i,cycle, current_pipeline.insExecuted[i-1][cycle])
    wb.save(_filename)
    os.startfile(_filename)

if __name__ == '__main__':
    run()
