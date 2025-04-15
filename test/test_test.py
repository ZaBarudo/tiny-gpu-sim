#!/usr/bin/env python3
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
    threads = 8
    data = [4, 2, 3, 14, 15, 6, 7, 8, 2, 2, 3, 4, 5, 6, 7, 8, 0, 0, 0, 0, 0, 0, 0, 0]

    # Initialize memories
    program_memory = Memory(dut=dut, addr_bits=8, data_bits=16, channels=1, name="program")
    data_memory = Memory(dut=dut, addr_bits=8, data_bits=8, channels=4, name="data")

    # Program instructions
    program = [
        0b1001100000000000, 0b1001100100001000, 0b1001101000010000, 0b0101000011011110, 0b0011000100001111, 0b1001000000000000, 0b1001001000000000, 0b1001001100001001, 0b0010000000100011, 0b0001001000010001, 0b0010000000000000, 0b0001010000001100, 0b0011000000000010, 0b1001001100000001, 0b0011001000100011, 0b0010000000000000, 0b0001010000000111, 0b1001001000000001, 0b0101000100010010, 0b0011000110000001, 0b1000000000010000, 0b1111000000000000
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

    print(f"\nCompleted in {cycles} cycles")
    data_memory.display(24)
    with open("tinygpu_output.txt", "w") as file:
        for item in data_memory.memory[0:24]:
            file.write(str(item)+" ")


