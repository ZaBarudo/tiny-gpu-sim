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
    # Check if the file exists
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' not found.")
        return 1

    # Extract base filename
    base = os.path.basename(input_file)
    name = os.path.splitext(base)[0]
    clang_output = f"{name}.S"

    # Step 2: Generate assembly with clang
    try:
        subprocess.run(
            ["clang", "-S", "--target=tinygpu", input_file, "-o", clang_output],
            check=True
        )
    except subprocess.CalledProcessError:
        print("Error: clang command failed.")
        return 1

    # Step 3: Convert to test.asm and parse
    try:
        os.rename(clang_output, "test.asm")
    except OSError as e:
        print(f"Error: Failed to rename {clang_output} to test.asm: {e}")
        return 1

    if not os.path.isfile("test.asm"):
        print("Error: test.asm not found after renaming.")
        return 1

    try:
        if "imm" in input_file:
            subprocess.run(["python3", "parsing.py", "test.asm", ""], check=True)
        else:
            subprocess.run(["python3", "parsing.py", "test.asm"], check=True)
    except subprocess.CalledProcessError:
        print("Error: Python parsing.py failed.")
        return 1

    # Step 4: Run make command
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
    # TODO: parse the output log and parse the memory address if they match in input_file:
    compare_number_files('tinygpu_output.txt', 'nvidia_output.txt')


    
if __name__ == "__main__":
    exit(main())