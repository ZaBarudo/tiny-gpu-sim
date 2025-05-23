.PHONY: test compile

export LIBPYTHON_LOC=$(shell cocotb-config --libpython)


test_%:
	make compile
	iverilog -o build/sim.vvp -s gpu -g2012 build/gpu.v
	MODULE=test.test_$* vvp -M $$(cocotb-config --prefix)/cocotb/libs -m libcocotbvpi_icarus build/sim.vvp

compile:
	g++ ./testing-example/cuda_source_code\ /arr_arr_arr_opencl.c -o arr_arr_arr_opencl -lOpenCL
	g++ ./testing-example/cuda_source_code\ /arr_opencl.c -o arr_opencl -lOpenCL
	g++ ./testing-example/cuda_source_code\ /imm_opencl.c -o imm_opencl -lOpenCL
	make compile_alu
	./sv2v -I src/* -w build/gpu.v
	echo "" >> build/gpu.v
	cat build/alu.v >> build/gpu.v
	echo '`timescale 1ns/1ns' > build/temp.v
	cat build/gpu.v >> build/temp.v
	mv build/temp.v build/gpu.v

compile_%:
	./sv2v -w build/$*.v src/$*.sv

clean:
	rm arr_arr_arr_opencl arr_opencl imm_opencl nvidia_output.txt tinygpu_output.txt test.asm results.xml *.ll *.s *.asm ./test/logs/*.txt

# TODO: Get gtkwave visualizaiton

show_%: %.vcd %.gtkw
	gtkwave $^

func_%:
	clang -S --target=tinygpu -emit-llvm -O0 -o ./testing-example/function_call/$*.ll ./testing-example/function_call/$*.c
	python3 clean_files.py -f -i ./testing-example/function_call/ -o ./testing-example/function_call/
	opt -S -passes=mem2reg ./testing-example/function_call/$*.ll -o ./testing-example/function_call/$*2.ll 
	llc -O0 -march=tinygpu ./testing-example/function_call/$*2.ll -o ./testing-example/function_call/$*.s