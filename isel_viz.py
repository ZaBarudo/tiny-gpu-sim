import os
import subprocess

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
                ["llc", "-O1", "--march=tinygpu", mem2reg_ir,"-view-isel-dags", "-o", clang_output],
                check=True
            )
        else:
            subprocess.run(
                ["llc", "--march=tinygpu", mem2reg_ir, "-view-isel-dags", "-o", clang_output],
                check=True
            )
    except subprocess.CalledProcessError:
        print("Error: llc failed to generate assembly.")
        return 1

    
    return 0



def main():
    # Step 1: Get user input for which file to run
    input_file = input("Enter the file path to run (e.g., ./testing-example/arithmetic/add.cl): ").strip()
    run_tinygpu(input_file)


    
if __name__ == "__main__":
    exit(main())