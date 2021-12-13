### CMSC 411 Project ###
import os
import xlwt

class Registers:
    """
    This class oversees all registers, when called it will initialize a class that holds two lists, one for each type of registers
    """
    def __init__(self):
        self.FPRegs_ = [] # list of Floating point Register objects
        self.IntRegs_ = [] # list of Integer Register objects

        # register's names corresponds to their index # in the list
        for i in range(32):
            temp = Registers.FPRegister(_id=f"F{i}")
            self.FPRegs_.append(temp)
            temp = Registers.IntRegister(_id=f"${i}")
            self.IntRegs_.append(temp)
    
    def retrieve(self, _id):
        """ return register object with the supplied _id, _id must be $0-$31 or F0-F31 """
        index = int(_id.replace("$", "").replace("F", ""))
        
        # index being accessed must be between 0 and 31, and _id must start with $ or F
        if not (0 <= index <= 31) or _id[0] not in ['F', '$']:
            raise Exception(f"{_id} is not a valid register!") # Register.retrieve() received an invalid register name.

        if _id[0] == 'F': return self.FPRegs_[index]
        if _id[0] == '$': return self.IntRegs_[index]
    
    def write_to(self, _id, _data):
        """ takes in a register ($0-$31 or F0-F31) and writes given data to the register """
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
        """ Each register object represents an individual register """
        def __init__(self, _id, _data=0):
            self.id_ = _id # immutable name of the register, $0-$31/F0-F31
            self.data_ = _data # either int or float
            self.read_cycle = 0 # the cycle which the register is ok to be read
            self.write_cycle = 0 # the cycle the register is ok to be written to
        
        def __str__(self) -> str:
            """ A string representation of the register object """
            return f"Register: {self.id_}\tData: {self.data_}    \t\tRead/Write Cycles:{self.read_cycle}, {self.write_cycle}"
            
        # setters and getters for the register
        def set_data(self, _data):
            self.data_ = _data
        def set_read_cycle(self, cycle):
            self.read_cycle = cycle
        def set_write_cycle(self, cycle):
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
        def __init__(self, _id, _data=0.0):
            super().__init__(_id=_id, _data=_data)
        def set_data(self, _data=0.0):
            self.data_ = float(_data) # type checking by type casting lol
    class IntRegister(Register):
        def __init__(self, _id, _data=0):
            super().__init__(_id=_id, _data=_data)
        def set_data(self, _data=0):
            self.data_ = int(_data)

class Memory:
    """
    Main memory, a list where data at index represent data at memory address
    default parameter for the data_set, if no data_set is provided then it will use the default
    """
    def __init__(self, data_set=[45,12,0,92,10,135,254,127,18,4,55,8,2,98,13,5,233,158,167]):
        self.memory_ = data_set
        self.length_ = len(self.memory_)
    
    # address will be an int immediate or int data retrieved from a register, with an optional offset
    def retrieve_at_address(self,  _address, _offset=0):
        """ returns memory at given address plus offset """
        _address = int(_address) + int(_offset) # adds both together to get the actual address
        _address %= self.length_ # makes memory circular
        return self.memory_[_address]
    
    def write_to_address(self, _data, _address, _offset=0):
        """ sets data at given memory location """
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
        self.label_ = _label # not every instruction will have a label
        self.opcode_ = _opcode
        self.op_one_ = _op_one
        self.op_two_ = _op_two
        self.op_three_ = _op_three

    # all these code just to print commas in right places lol
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
    """ manages registers and memory, does the actual pipeline """
    def __init__(self, _fileName="test.txt"):
        self.instructions = {} # key:instruction address, value:list containing the instruction, label, opcode, and operands
        self.loops = {} # key:loop name, value:loop instruction's address, tracks address that the branches might jump to 
        self.branches = {} # branch predictor, key:address of branch, value: 1|0 where 1 == taken and 0 == not taken
        self.insExecuted = [] # list of dictionaries, index:executed instructions, executed instruction = {key:cycle, value:dictionary of stages}
        self.registers = Registers()
        self.memory = Memory()
        # key:set # (mem address % len(cache)), value:[dirty bit, memory address, data, forward cycle], forward cycle = read-safe cycle for cache
        self.cache = {0:[0, None, None, 0],1:[0, None, None, 0],2:[0, None, None, 0],3:[0, None, None, 0]} 
        self.cache_size = 4

        all_instructions = Pipeline.parser(_fileName)
        counter = 0 # instruction address counter, first instruction is at address 0000
        for instruction in all_instructions:
            if ':' in instruction[0]: # if a loop is found, then add it to the dictionary, 
                loop_name = instruction[0].replace(':', '')
                self.loops[loop_name] = counter # key:loop name, value:loop address
            try:
                opcode_shift = 1 if ':' in instruction[0] else 0
                if instruction[opcode_shift] in ["BNE", "BEQ"]: # when a branch instruction is found, add it to the branches dictionary
                    self.branches[counter] = 1 # key:branch address, value:1/0 taken/not taken
            except Exception: pass
            self.instructions[counter] = instruction
            counter += 1
    
    def __str__(self,instruction): # string representation of the instruction line, all this just to make sure commas are correctly placed ;)
        if len(instruction) <= 1:
            return f"{instruction[0]}"
        if len(instruction) == 2:
            return f"{instruction[0]} {instruction[1]}"
        if len(instruction) == 3:
            if ':' in instruction[0]:
                return f"{instruction[0]} {instruction[1]}, {instruction[2]}"
            return f"{instruction[0]} {instruction[1]} {instruction[2]}"
        if len(instruction) == 4:
            if ':' in instruction[0]:
                return f"{instruction[0]} {instruction[1]} {instruction[2]}, {instruction[3]}"
            return f"{instruction[0]} {instruction[1]}, {instruction[2]}, {instruction[3]}"
        return f"{instruction[0]} {instruction[1]} {instruction[2]}, {instruction[3]}, {instruction[4]}"

    def parser(_filename="test.txt"):
        """ takes a filename, parse the file into a list of instruction lists, instruction list will contain opcode and operands """
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

    # prints
    def print_all_instruction_objects(self):
        for instruction_address in self.instructions:
            print(instruction_address, self.instructions[instruction_address])
    def print_all_loops_and_addresses(self):
        for loops in self.loops:
            print("Address:", self.loops[loops], "Name:", loops)
    def print_all_branch_addresses(self):
        for branch in self.branches:
            print(f"Branch address: {branch} Taken: {bool(self.branches[branch])}")

    def execute(self):
        """ The man, the myth, the legend, it's the actual pipeline simulator """
        def registers_check(current_cycle=0,status='R'):
            """
            status is Read by defualt, anything else checks for write, which checks for the largest read-ready and the largest write-ready cycles respectively
            add stalls up to the largest cycle required in order to avoid a data hazard
            """
            all_opcodes = ["ADD","ADD.D","SUB","SUB.D","MUL.D","DIV.D","ADDI","L.D","LW","S.D","SW","BEQ","BNE", "J"]
            source_register_one = source_register_two = destination_register = "" # place holder
            if opcode in all_opcodes: # assigns the operands into destination or source registers
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
                if opcode in all_opcodes[9:11]: # SD/SW
                    source_register_one = op_one
                    try: parsed = op_two.replace(")","").split("(")
                    except Exception: parsed = op_two
                    destination_register = parsed[1]
                if opcode in all_opcodes[11:13]: # Branches except J
                    source_register_one = op_one
                    source_register_two = op_two

            # finds the largest read/write cycles, largest cycle is determined by status passed
            largest_read_cycle = max((self.registers.retrieve(R).get_read_cycle() for R in [destination_register, source_register_one, source_register_two] if R), default=0)
            largest_write_cycle = max((self.registers.retrieve(R).get_write_cycle() for R in [destination_register, source_register_one, source_register_two] if R),default=0)
            largest_cycle = largest_read_cycle if status == 'R' else largest_write_cycle
            if largest_cycle > current_cycle:
                for i in range(current_cycle+1, largest_cycle):
                    if i not in stalled_cycles: # no need to add repeated stall cycles
                        stalled_cycles.append(i) 

        def write_stalled_cycles(smallest_cycle:int):
            """
            if the cycle immediately following the given cycle is a stall, then add stalls until a break is found,\n
            when given a stage cycle, it will fill in stalls found between the given stage and the next, then return the cycle right before the next stage starts\n

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
            return most_recent_stall # most recent stall is unchanged if no stall is found
        
        def mem_check(cycle):
            """ 
            takes in the cycle which the first mem stage is supposed to go, if that stage is already a mem stage in the last executed instruction,
            then add stalls until the stage is no longer in the list, at that point, write in the mem stages to the current instruction
            return the last mem cycle
            """
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
                            cycle += 1
                            return cycle
                        return cycle
                    return cycle
            except Exception: pass
            return cycle 

        instruction_counter = 0 # program counter
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
            current_instruction[IF_cycle] = "IF"
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

            most_recent_stall = write_stalled_cycles(ID_cycle) # write in stalls between ID-EX
            registers_check(current_cycle=ID_cycle) # checks for the largest read cycle to stall until
            
            # execute the instruction
            if opcode == "L.D" or opcode == "LW": # L.D Fa, Offset(addr), LW $d, Offset(addr) -> Load a floating point/int value into Fa/$d
                # input validation for the respective opcodes
                if opcode == "L.D" and 'F' not in op_one:
                    raise Exception(f"Register {op_one} is invalid, opcode L.D requires a floating point register as the first operand!")
                if opcode == "LW" and '$' not in op_one:
                    raise Exception(f"Register {op_one} is invalid, opcode LW requires an integer register as the first operand!")

                # if LD is detected, Ex stage will take 1 cycle, then immediately enter the MEM stage
                EX_cycle = most_recent_stall+1
                current_instruction[EX_cycle] = "EX"
                registers_check(current_cycle=EX_cycle,status='w') # register's write-readiness check
                most_recent_stall = write_stalled_cycles(EX_cycle) # stalls between EX-MEM

                address = offset = 0 # placeholder
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
            ### Monstrocity of an input validation
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
                MEM_cycle = mem_check(MEM_cycle)
                current_instruction[MEM_cycle] = "MEM"
                
                # these 4 instructions are all basically the same
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
                if self.branches[instruction_counter-1]: # check if the branch is a taken
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
                        # incorrectly predicted taken/not taken
                        self.branches[instruction_counter-1] = 0 # invert prediction

                        #updating EX cycle and Most recent stall
                        EX_cycle = most_recent_stall+1
                        most_recent_stall = write_stalled_cycles(EX_cycle)

                        registers_check(current_cycle=EX_cycle) # registers' read-readiness check
                        current_instruction[most_recent_stall] = "EX"
                        
                        self.insExecuted.append(current_instruction)
                        def make_two_dummy():
                            current_instruction = {}
                            instruction_counter = address
                            #setting current instruction to first instruction in the loop
                            current_instruction[0] = self.__str__(self.instructions[instruction_counter])
                            
                            #updating IF cycle and Most recent stall
                            IF_cycle = last_ID_cycle
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
        for i in range(1, end_cycle+2):
            sheet.write(0, i, i, xlwt.easyxf("align: horiz left"))
        
        for i in range(1, len(current_pipeline.insExecuted)+1):
            # write(row, column, item)
            for cycle in current_pipeline.insExecuted[i-1]:
                sheet.write(i,cycle, current_pipeline.insExecuted[i-1][cycle])
        
        print(f"ALL REGISTERS FOR {file}.txt:",end='')
        current_pipeline.registers.print_all_registers()
        print(f"ALL MEMORY FOR {file}.txt:",end='')
        current_pipeline.memory.print_all_memory()

    wb.save(_filename)
    os.startfile(_filename) # this might only work on windows

if __name__ == '__main__':
    run()
