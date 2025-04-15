import os
import subprocess

def compare_number_files(file1, file2, verbose=True):
    def read_numbers(filename):
        with open(filename, 'r') as f:
            return list(map(int, f.read().strip().split()))

    numbers1 = read_numbers(file1)
    numbers2 = read_numbers(file2)

    if numbers1 == numbers2:
        if verbose:
            print("✅ The numbers in both files match exactly.")
        return True
    else:
        if verbose:
            print("❌ The numbers do not match.")
            min_len = min(len(numbers1), len(numbers2))
            for i in range(min_len):
                if numbers1[i] != numbers2[i]:
                    print(f"Mismatch at position {i}: {file1} = {numbers1[i]}, {file2} = {numbers2[i]}")
            if len(numbers1) != len(numbers2):
                print(f"Different number of elements: {file1} has {len(numbers1)}, {file2} has {len(numbers2)}")
        return False

def run_opencl(input_file):
    try:
        if "_imm" in input_file: # using immediate value as a parameter in the function
            subprocess.run(["./imm_opencl", input_file],check=True)
        elif "loop" in input_file or "open_cl" in input_file: # using one array 
            subprocess.run(["./arr_opencl", input_file],check=True)
        else: #using three arrays
            subprocess.run(["./arr_arr_arr_opencl", input_file],check=True)
    except subprocess.CalledProcessError:
        print("Error: openCl failed.")
        return 1

def run_tinygpu(input_file):
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' not found.")
        return 1

    base = os.path.basename(input_file)
    name = os.path.splitext(base)[0]
    llvm_ir = f"{name}.ll"
    cleaned_ir = f"{name}_clean.ll"
    mem2reg_ir = f"{name}_mem2reg.ll"
    clang_output = f"{name}.S"

    # Step 1: Generate LLVM IR with -O0
    try:
        subprocess.run(
            ["clang", "-O0", "-S", "-emit-llvm", "--target=tinygpu", input_file, "-o", llvm_ir],
            check=True
        )
    except subprocess.CalledProcessError:
        print("Error: clang failed to generate LLVM IR.")
        return 1

    # Step 2: Remove 'optnone' attribute from IR
    try:
        with open(llvm_ir, "r") as infile:
            ir_contents = infile.read()
        ir_contents = ir_contents.replace("optnone", "")
        with open(cleaned_ir, "w") as outfile:
            outfile.write(ir_contents)
    except Exception as e:
        print(f"Error cleaning optnone: {e}")
        return 1

    # Step 3: Apply mem2reg optimization
    try:
        subprocess.run(
            ["opt", "-passes=mem2reg", cleaned_ir, "-S", "-o", mem2reg_ir],
            check=True
        )
        subprocess.run(
            ["opt", "-passes=break-crit-edges", mem2reg_ir, "-S", "-o", mem2reg_ir],
            check=True
        )
    except subprocess.CalledProcessError:
        print("Error: opt mem2reg pass failed.")
        return 1

    # Step 4: Compile optimized IR to assembly
    try:
        if "loop" in input_file or "mat_add" in input_file:
            subprocess.run(
                ["llc", "-O1", "--march=tinygpu", mem2reg_ir, "-o", clang_output],
                check=True
            )
        else:
            subprocess.run(
                ["llc", "--march=tinygpu", mem2reg_ir, "-o", clang_output],
                check=True
            )
    except subprocess.CalledProcessError:
        print("Error: llc failed to generate assembly.")
        return 1

    # Step 5: Rename to test.asm
    try:
        os.rename(clang_output, "test.asm")
    except OSError as e:
        print(f"Error: Failed to rename {clang_output} to test.asm: {e}")
        return 1

    if not os.path.isfile("test.asm"):
        print("Error: test.asm not found after renaming.")
        return 1

    # Step 6: Run parsing
    try:
        if "imm" in input_file:
            subprocess.run(["python3", "parsing.py", "test.asm", ""], check=True)
        else:
            subprocess.run(["python3", "parsing.py", "test.asm"], check=True)
    except subprocess.CalledProcessError:
        print("Error: Python parsing.py failed.")
        return 1

    # Step 7: Run test
    try:
        subprocess.run(["make", "test_test"], check=True)
    except subprocess.CalledProcessError:
        print("Error: Make command failed for target test_test.")
        return 1

    print("Workflow completed successfully.")
    return 0



def main():
    # Step 1: Get user input for which file to run
    input_file = input("Enter the file path to run (e.g., ./testing-example/arithmetic/add.cl): ").strip()
    run_tinygpu(input_file)
    run_opencl(input_file)
    compare_number_files('tinygpu_output.txt', 'nvidia_output.txt')


    
if __name__ == "__main__":
    exit(main())