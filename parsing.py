import re
import sys
import os
from pathlib import Path
from subprocess import run, CalledProcessError
from textwrap import dedent

IMM_FLAG = False
IMM_VALUE = 0

def get_user_input():
    global IMM_VALUE
    """Get configuration from user in the main script."""
    try:
        # threads = int(input("Enter number of threads (default=8): ") or "8")
        threads = 8

        # print("Enter up to 24 data values (press Enter after each, blank for 0):")
        data = []
        with open('input.txt', 'r') as f:
            data = list(map(int, f.read().strip().split()))
        IMM_VALUE = data[8]
        print("the data",data)
        return threads, data
    except ValueError as e:
        print(f"Invalid input: {e}")
        sys.exit(1)


def get_register_values():
    global IMM_VALUE
    global IMM_FLAG
    """
    Get register constant values from user input for registers R8, R9, and R10.
    These values will be added to the assembly source code.
    """
    try:
        # reg8 = int(input("Enter value for register R8: "))
        # reg9 = int(input("Enter value for register R9: "))
        # reg10 = int(input("Enter value for register R10: "))
        reg8 = 0
        reg9 = 8
        reg10 = 16
        if IMM_FLAG:
            reg9 = IMM_VALUE
        return {'R8': reg8, 'R9': reg9, 'R10': reg10}
    except ValueError as e:
        print(f"Invalid register input: {e}")
        sys.exit(1)


def add_register_constants(asm_code, register_values):
    """
    Adds register constant definitions to the source assembly code.
    Each constant is added as a new line in the format:
       CONST <Register>, #[value]
    The constants are prepended to the existing asm code.
    """
    constants_lines = []
    for reg, val in register_values.items():
        constants_lines.append(f"CONST {reg}, #{val}")
    # Prepend the constant definitions and a blank line to separate from original code.
    modified_code = '\n'.join(constants_lines) + '\n\n' + asm_code
    return modified_code


def update_const_values(asm_code):
    """
    Update constant definitions in the assembly code.
    Replace any occurrence of "CONST RX, #4" with "CONST RX, #1"
    where RX is any register (e.g., R8, R9, etc.).
    """
    # This regex captures the register portion and ensures that '#4'
    # is replaced with '#1', keeping the rest of the line unchanged.
    regex = re.compile(r'(CONST\s+R\d+,\s*#)4\b', flags=re.IGNORECASE)
    updated_code = regex.sub(r'\g<1>1', asm_code)
    return updated_code


def remove_prefix_from_asm_output(asm_output):
    """
    Removes unwanted prefix patterns (e.g., [110]) from each line of assembler output.
    """
    cleaned_lines = []
    for line in asm_output.strip().splitlines():
        # Remove a prefix like "[110]" with an optional following space
        cleaned_line = re.sub(r'^\[\d+\]\s*', '', line)
        cleaned_lines.append(cleaned_line)
    return cleaned_lines


def generate_testbench(assembler_output, output_file, threads, data_values):
    """Generate a Cocotb testbench from assembler output with provided configuration."""
    # Remove unwanted prefixes from the assembler output lines
    cleaned_lines = remove_prefix_from_asm_output(assembler_output)
    
    # Convert the cleaned binary strings to integers by removing spaces and
    # prefixing with '0b' for binary literal representation.
    program = [f"0b{line.replace(' ', '')}" for line in cleaned_lines]
    
    # Format data values for the template
    formatted_data = ', '.join(str(v) for v in data_values)
    
    # Generate the testbench template
    testbench_template = f'''#!/usr/bin/env python3
import cocotb
from cocotb.triggers import RisingEdge
from .helpers.setup import setup
from .helpers.memory import Memory
from .helpers.format import format_cycle
from .helpers.logger import logger


@cocotb.test()
async def test_generated(dut):
    """Test generated from assembler output"""
    # Configuration from main script
    threads = {threads}
    data = [{formatted_data}]
    
    # Initialize memories
    program_memory = Memory(dut=dut, addr_bits=8, data_bits=16, channels=1, name="program")
    data_memory = Memory(dut=dut, addr_bits=8, data_bits=8, channels=4, name="data")
    
    # Program instructions
    program = [
        {', '.join(program)}
    ]
    
    # Run setup
    await setup(
        dut=dut,
        program_memory=program_memory,
        program=program,
        data_memory=data_memory,
        data=data,
        threads=threads
    )
    
    # Display initial state
    data_memory.display(24)
    
    # Run simulation
    cycles = 0
    while dut.done.value != 1:
        data_memory.run()
        program_memory.run()
        
        await cocotb.triggers.ReadOnly()
        format_cycle(dut, cycles)
        
        await RisingEdge(dut.clk)
        cycles += 1
    
    print(f"\\nCompleted in {{cycles}} cycles")
    data_memory.display(24)
    with open("tinygpu_output.txt", "w") as file:
        for item in data_memory.memory[0:24]:
            file.write(str(item)+" ")
    
   
'''

    # Write the generated testbench to file
    with open(output_file, 'w') as f:
        f.write(dedent(testbench_template))
    
    print(f"Generated testbench saved to {output_file}")


class LLVMProcessor:
    @staticmethod
    def clean_llvm_asm(code):
        """Clean LLVM assembly by removing metadata and comments."""
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('.', ';')) and not stripped.startswith('.LBB') or not stripped:
                continue
            cleaned_lines.append(line)
        
        return cleaned_lines

    @staticmethod
    def organize_functions(lines):
        """Organize assembly code into functions with main first."""
        functions = {'main': [], 'others': []}
        current_block = []
        in_main = False
        
        for line in lines:
            stripped = line.strip()
            
            if 'main' in stripped or stripped.startswith('main@function'):
                if current_block and not in_main:
                    functions['others'].append(current_block)
                in_main = True
                current_block = [line]
            elif stripped.startswith('_Z') or stripped.startswith('; -- Begin function'):
                if current_block:
                    functions['main' if in_main else 'others'].append(current_block)
                in_main = False
                current_block = [line]
            else:
                current_block.append(line)
        
        if current_block:
            functions['main' if in_main else 'others'].append(current_block)
        
        return functions

    @staticmethod
    def reconstruct_assembly(functions):
        """Reconstruct assembly code with main first."""
        output_lines = []
        
        # Add main blocks
        for block in functions['main']:
            output_lines.extend(block)
        
        # Add other functions
        for block in functions['others']:
            output_lines.append('')  # Separator
            output_lines.extend(block)
        
        return '\n'.join(output_lines)


class Assembler:
    @staticmethod
    def run_assembler(asm_path, chisel_dir):
        """Run the assembler script from the specified directory."""
        original_dir = os.getcwd()
        assembler_path = os.path.join(chisel_dir, 'assembler.sh')
        
        try:
            # Verify assembler exists
            if not os.path.exists(assembler_path):
                raise FileNotFoundError(f"Assembler not found at {assembler_path}")
            
            # Change to chisel directory
            os.chdir(chisel_dir)
            
            # Run assembler with absolute path to asm file
            result = run(
                ['./assembler.sh', os.path.join(original_dir, asm_path)],
                capture_output=True,
                text=True
            )
            
            # If assembler failed, raise CalledProcessError with full output
            if result.returncode != 0:
                raise CalledProcessError(
                    result.returncode,
                    result.args,
                    result.stdout,
                    result.stderr
                )
            
            return result
        finally:
            # Always return to original directory
            os.chdir(original_dir)



def main():
    global IMM_FLAG
    # Get user configuration first.
    threads, data_values = get_user_input()
    input_file = sys.argv[1]
    IMM_FLAG = True if len(sys.argv) > 2 else False
    asm_path = 'test.asm'
    chisel_dir = os.path.join(os.path.dirname(__file__), '..', 'tiny-gpu-chisel-sim')
    
    try:
        # Process LLVM file.
        with open(input_file, 'r') as f:
            llvm_code = f.read()
        
        # Clean and organize assembly.
        cleaned_lines = LLVMProcessor.clean_llvm_asm(llvm_code)
        functions = LLVMProcessor.organize_functions(cleaned_lines)
        cleaned_code = LLVMProcessor.reconstruct_assembly(functions)
        
        # Get register constant values from user and add to the assembly code.
        register_values = get_register_values()
        cleaned_code = add_register_constants(cleaned_code, register_values)
        
        # Update any constant definitions of the form "CONST RX, #4" to "CONST RX, #1"
        cleaned_code = update_const_values(cleaned_code)
        
        # Save modified assembly
        with open(asm_path, 'w') as f:
            f.write(cleaned_code)
        
        # Run assembler.
        try:
            result = Assembler.run_assembler(asm_path, chisel_dir)
            
            # Print results.
            print("Modified assembly saved to:", os.path.abspath(asm_path))
            print("\nAssembler output:")
            print(result.stdout)

            # Generate output filename.
            base_name = os.path.splitext(os.path.basename(asm_path))[0]
            output_file = f"{base_name}_test.py"
            save_path = os.path.join(os.getcwd(), 'test', output_file)

            # Generate testbench with user configuration.
            generate_testbench(result.stdout, save_path, threads, data_values)
        except CalledProcessError as e:
            print("\nAssembler failed with the following output:")
            print("="*50)
            print("Command:", ' '.join(e.args[1]))  # Show the exact command that failed
            print("Return code:", e.returncode)
            print("\nOutput:")
            print(e.stdout)
            print("\nErrors:")
            print(e.stderr)
            print("="*50)
            sys.exit(1)
        
    except FileNotFoundError as e:
        print(f"File error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
