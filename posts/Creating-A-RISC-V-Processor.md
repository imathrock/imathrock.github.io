---
title: Building a RISC V processor
date: 2026-09-22
tags: RISC V
project: RISC-V Processor
excerpt: Trying to learn FPGAs to work on a ML hardware acceleration project
---

## Motivation
When I was trying to create a CNN framework in C, I realized that it's all matrix multiplication

![alt text](rv32blg1meme.png)

And it is possible to hyper optimize these operations by simply having the weights loaded into a memory matrix and have the vectors flow thru them to get an instant output. (I know the actual industry design is way more complicated and precise). Simultaneously I was taking a Computer Architecture and operating systems class and here we created a pipelined y86 processor on paper and we learned assembly thru simulators. I've always found that to be really cool, so I dug in as much as I could, I looked into SIMD, I accelerated my single threaded CNN framework as fast as I could get it, I learnt about cache optimizations, eviction policies and a whole bunch more. I also created a LC3 emulator and an assembler for that emulator that compiled assmebly into bytecodes that the LC3 virtual machine could run.  

Suffice to say I love low level stuff so the natural next step is to build my own CPU. So I'm going to create the project's scope here. I have a De1 SOC FPGA board and I'm gonna try and create first a sequential RV32I CPU and then a pipelined one. Also somehow figure out how to optimize it for GEMM stuff. 

## Project Scope

Here we go, I want this project to be able to do the following:
- Run the RV32I instruction set sequentially when programmed manually. 
- Pass the RV32I tests
- Run custom programs using the toolchain provided. 
- Parallelize into 5 stages (because y86 is 5 stage), fetch, decode, execute, memory, writeback. 
- Pass the RV32I tests again. 
- Try to optimize it for GEMM by exploring vector registers. 

## 
To do this I need to write verilog. Verilog is a Hardware Description Language. From what I know the code that we write there describes the ciruit inside the FPGA. But what is inside an FPGA? 
