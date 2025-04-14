#!/bin/bash
# Usage: ./run_workflow.sh
# This script prompts for a file to process, generates assembly using clang,
# parses the generated .asm file with parsing.py, and finally calls make with a custom target.

# Step 1: Get user input for which file to run.
read -p "Enter the file path to run (e.g., ./testing-example/arithmetic/add.cl): " input_file

# Check if the file exists.
if [[ ! -f "$input_file" ]]; then
    echo "Error: File '$input_file' not found."
    exit 1
fi

# Extract the base filename (without extension) for later use.
# e.g., "add.cl" -> "add"
base=$(basename "$input_file")
name="${base%.*}"

# Step 2: Run clang to generate assembly.
# This produces an assembly file with .S extension.
clang -S --target=tinygpu "$input_file" -o "${name}.S"
if [[ $? -ne 0 ]]; then
    echo "Error: clang command failed."
    exit 1
fi

# sed -i 's/CONST \(R[0-9]\+\),[[:space:]]*#4/CONST \1, #1/gI' "${name}.S"
# if [[ $? -ne 0 ]]; then
#     echo "Error: Failed to update constant values in ${name}.asm."
#     exit 1
# fi

# Step 3: Convert the clang output to the expected .asm file.
# Rename the generated .S file to .asm.
mv "${name}.S" "test.asm"
if [[ $? -ne 0 ]]; then
    echo "Error: Failed to rename ${name}.S to test.asm."
    exit 1
fi

# Verify the .asm file exists.
if [[ ! -f "test.asm" ]]; then
    echo "Error: ${name}.asm not found."
    exit 1
fi

# Run the Python parser on the .asm file.
python3 parsing.py "test.asm"
if [[ $? -ne 0 ]]; then
    echo "Error: Python parsing.py failed."
    exit 1
fi

# Step 4: Run make with the target "compile_[out]"
make_target="test_test"
make "$make_target"
if [[ $? -ne 0 ]]; then
    echo "Error: Make command failed for target ${make_target}."
    exit 1
fi

echo "Workflow completed successfully."
