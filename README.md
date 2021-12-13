# CMSC 421 Fall 2021 Project: MIPS Pipeline Simulator
# Authors: Avalon Ferman, Zhihong Pang

## Overview
Congratulations, you've stumbled upon our MIPS assembly pipeline simulator!
When run on a Windows 10 system, this will automatically open an excel file named "Hot stuff.xls" with the three example outputs. If not, you can find the output file within the program directory. The final Register and Memory information can be found in the terminal you executed the program with.
* to test different files, pass a list containing the file name into run(). For example, if you want to test only example1.txt, do run(["example1"]), but by default it will test all three example cases given.

## Installation
Use the package manager pip to install xlwt
```bash
pip install xlwt
```

## Usage
This program have been tested with Windows 10 and the UMBC Linux Terminal
within the folder where proj.py resides, enter "py proj.py" in the terminal to run the program
```bash
py proj.py
```
or
```bash
python proj.py
```

## Table of contents
1. Classes
    * Registers
    * Memory
    * Instruction
    * Pipeline
2. Run()
3. Notes

## Classes
* Registers
    * When called it will initialize a two lists, each containing either FP or Int register objects
    * This class can retrieve single register objects by name, and edit their data by name
* Memory
    * The Main memory is just a list of data, with their indexes representing the memory addresses
    * This class can retrieve and edit data at a given int immediate address, if a register is used, will retrieve the data at the register before passing the data to this function as an int immediate
* Instruction
    * During parsing, each instruction line will be turned into an Instruction object, which serves to track the instruction line's label, opcode and operands
* Pipeline
    * Variables:
        * The instructions variable is a dictionary that uses the instruction address as keys and a list containing the label, opcode, and operands to that instruction as values. 
            * Example: if LI $7, 0 is the first instruction, then key 0 in self.instructions will give ["LI", "$7", "0"]
        * The loops dictionary holds any labels that are found, keys in this dictionary are the label names and their values are the address where the label points to
        * The branches dictionary holds the address where the branch is found, this is used as the predictor, where during execution, if the address is in this dictionary, then check the value, if 1 then predict taken, 0 then not taken
        * insExecuted is a list that holds all of the instructions that are executed, executed instructions are in the form of a dictionary. Keys: cycles and Values: string representation of the stage executed.
        * Cache is a dictionary with 4 keys, each representing a set that memory fetched can go into, the value at each set contains information on whether the memory stored in the cache has been altered, the memory address where the memory came from, the data at the cache, and a forward cycle where the cache is read-safe
        * stalled cycles is a list that contains all stalled stages within the pipeline.

        * The Pipeline also initializes Registers and Memory, and manages within individual pipeline classes
    
    * parser()
        * The parser takes in a filename and goes line by line to parse every line into a list containing their labels, opcode, and operands
    * Execute()
        * The idea behind the implementation of the pipeline is a line-by-line execution of instructions, kind of like a scoreboard, and registers will track their own read-ready and write-ready cycles to avoid a data hazard.
        * registers_check()
            * Checks the registers used, and depending on the status, it will either check for the registers used's read-ready or write-ready cycles, once the largest cycle to stall for is found, then add stalls between the current cycle and the largest into the stalled cycles list.
        * write_stalled_cycles()
            * Will check to see if the cycle directly after the current cycle is in the stalled cycles list, if it is, then we know to stall until a break in the stalls is found, which indicates the end of the stalls
        * mem_check()
            * checks to see if the current mem cycle is also a mem cycle in the last executed instructions, if yes, then will stall until its no longer in conflict.
        
        * Execute starts with the program counter being 0, and will keep track of the last ID cycle outside of the main loop.
        * the main loop will not end unless the instruction counter has reached the las instruction's index.
        * the current instruction tracks the cycle and stages for the current instruction.
        
        * Logic:
            * IF cycle is always the last ID cycle, the IF stage will fetch the instruction from the self.instructions using the instruction counter as key, then run the write_stalled_cycles function to write in all stalled functions between IF and ID, set the most recent stall to either the IF cycle or the last stall cycle before the ID stage
            * The ID stage is always the most recent stall + 1, and will decode the fetched instruction into label, opcode, and operands, if there's no label then it will just be an empty string. Part of the decoding is to add in stalls up to the largest cycle required for the source registers to be read-safe, that will be the most recent stall, then write in stalls between the ID and the EX stages
            * Ex stage is different depending on opcode
                * LD/LW/LI instructions will write the EX stage at the most recent stall+1, then check to find the largest write-ready cycle for the source register, stall until that cycle, then check cache. If cache miss then add three mem cycles. Regardless of cache hit or cache miss, it will run the mem_check function to make sure the mem cycles don't overlap.
                * SD/SW is identicle to the LD/LW/LI instructions, with the difference being that instead of checking for write-ready cycles, it will check for the largest read-ready cycle, also, by implementation, SD/SW only takes 1 cycle to reach main memory, therefore, mem stages will always be 1 cycle unless there's overlap.
                * The ADD/ADD.D/SUB/SUB.D/MUL.D/DIV.D instructions are all very similar. After checking for the largest read-cycle for the registers used and writing the stalled cycles. The ADD/SUB instructions only takes 1 ex cycle, the ADD.D/SUB.D takes 2 ex cycles, and the MUL.D and DIV.D each takes 10 and 40 respectively. Then check for the write-ready cycle, and check for mem stage overlaps, after that wrtie in the mem stage.
                * All but the branch instruction does WB right after the mem stage.

                * The Branch instructions have 4 cases, correctly predicted taken/not taken, and incorrectly predicted taken/not taken. When predicted correcly, it will either take or not take the branch, but regardless, it will only change the program counter, which effects the instruction fetched by the IF stage of the next iteration. The incorrectly predicted branches will fetch instructions until they execute to the ex cycle of the branch. This will then invert the branch predictor in self.branches[branch address].
                * Jump instruction will unconditionally change the program counter to the int immediate provided.
    * run()
        * The run function will create an excel file named "Hot stuff.xls" which contains very hot pipeline example outputs.
        * It will add sheets based on the number of file names given to the function in the parameter files, so if you want to test other test files, just pass a list of filenames into the run function.
        * When the program is executed on non-windows 10 systems, it might not open the excel file automatically. Just look in the program's directory to find the hot stuff.xls for the program's output.

## Note
If you choose to run this program with the UMBC Linux Terminal, you might receive an os.startfile error. In that case, open the program's directory and find the "Hot stuff.xls" for the output of three example files