---
title: Build Log: RISC-V Processor with Vector GEMM on an FPGA
summary: A daily log of building an RV32I processor on a DE1-SoC, then adding a vector extension subset and optimizing it for GEMM with the FPGA's DSP blocks.
---

## The project
I want to build a RISC-V CPU from scratch in Verilog on a DE1-SoC (Cyclone V) FPGA board, and then make it good at matrix multiplication. I've already written GEMM in software (AVX and pthreads in my [CNN framework](https://github.com/imathrock/CNNs-in-C)); this is the hardware side of the same problem.

Plan: a sequential RV32I core, then a 5-stage pipeline, then a vector extension subset with a GEMM kernel that uses the DSP blocks.

## Milestones
- [x] Understand how an FPGA is built (LUTs, CLBs, interconnect)
- [x] Read the RV32I base ISA chapters of the manual
- [ ] Set up the toolchain: Quartus, a simulator, the RISC-V GCC toolchain
- [ ] Sequential RV32I core running hand-written programs
- [ ] Sequential core passes riscv-tests
- [ ] Run C programs compiled with the RISC-V toolchain
- [ ] 5-stage pipeline: fetch, decode, execute, memory, writeback
- [ ] Pipelined core passes riscv-tests
- [ ] Vector extension subset with a fixed vector length
- [ ] GEMM kernel on the DSP blocks, benchmarked

## Results
Filled in as I measure things. A dash means not measured yet.

| Design | Fmax | Logic used | DSPs used | GEMM throughput |
|---|---|---|---|---|
| Sequential RV32I | - | - | - | - |
| 5-stage pipeline | - | - | - | - |
| Vector + DSP GEMM | - | - | - | - |

Baseline to beat: my AVX GEMM on a desktop CPU, and the scalar core running the same kernel.
