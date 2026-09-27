---
title: What's Inside an FPGA chip?
date: 2026-09-24
tags: RISC V
project: RISC-V Processor
excerpt: What the heck are they made of?
---

Before we move on, I've found a BPS space style channel called Breaking Taps. This guy manufactured his own chip and it's really cool!

## What is an FPGA?
An FPGA is a field programmable gate array. As the name suggests it's a gate array that we can program to do our specific task. It's not a general purpose computer so the word 'program' is describing a hardware circuit that gets configured inside the chip. To program an FPGA we use a HDL (Hardware Description Language), the name is self explanatory. But how is it that hardware can be configured?

## Inside an FPGA
Inside an FPGA is a mesh of Configurable Logic Blocks (CLB) and Programmable Interconnects. It's in part quite similar to the grid system most north american cities have. The roads represent wires that connect to CLBs and the interconnects are the intersections of these roads. So for data to go from one point to another, data can traverse this grid of wires thru different CLBs to then get modified according to our requirements and provide us with an output. This is a quite restricted analogy as it can only describe combinational logic and not sequential one. This FPGA chip is surrounded by IO blocks, used to communicate with external devices. 

### Configurable Logic Blocks
Since this blog post series is about me entering rabbit holes, I'm going to try and figure out how a CLB works by making it from scratch in logisim. In [this repository](https://github.com/imathrock/FPGA-emulator) I tried creating a small FPGA gate array fabric in logisim and C++ last year (2025). I'm deciding to revive this repository. At the time of writing this repository has some logisim circuits that simulate multiplexers, latches and Flip Flops.

We know about the gates. All of them are listed as: AND, OR, NOT, XOR. Using these 4 we can create anything. A Configurable logic block looks as follows:
![alt text](CLB-24-09-26.png)
This seems too basic to run an operating system but this is the primitive used in FPGA that when scaled form the programmable fabric. What we see here is we have a D flip flop, A Multiplexer and a LUT (Lookup table). Let's start by creating these basic components inside logisim-evolution. 

#### Multiplexer
This is kinda basic so I'm just gonna show circuits and not explain how they work.
A 2 to 1 multiplexer acts as a selection tool. Depending on what the select pin is, the output either comes from one pin or the other. 
Here's an image of one I created
![mux animation](muxgif1.gif "How the mux selects its input")
It's possible to chain many of these together to then get $2^n$ size mux, It would have $n$ select pins. 

#### LUT
A LUT is a Lookup table. Think of it as a configurable truth table but it's a physical circuit. So how do you make a LUT? A LUT needs to have persistent memory because that is the programmable bit of our Configurable Logic Block. So it needs to have flip flops.

Let's make a flip flop!
##### Flip Flops
We're really getting in the weeds here. To make a flip flop we need something that can retain data. To begin we will make an SR latch. A latch is a circuit that holds data. The following is an example of an SR latch. 
![SR latch](20260924-1242-26.8401116.mp4 "SR latch")
This latch consists of 2 NOR gates with outputs connected to one another's inputs. We control the 2 reamining inputs. As you can see there can be an illegal combination of inputs where a race condition can be created between the inputs. To get around this we use what's called a gated latch. Simply chuck in some AND gates in there and introduce a clock signal. Like the following:
![Clocked Gated SR latch](20260924-1311-32.9307776.mp4 "Clocked Gated SR latch")
Next in progression comes the Flip Flop. The following is a D flip flop:
![D flip flop](20260924-1329-19.0745021.mp4 "D flip flop")
Here because of the not gate we can not have an illegal condition of both inputs being high at the same time. There are T flip flops, JK flip flops and SR flip flops. Edge triggered flip-flop behavior gets finicky in Logisim due to gate propagation race conditions, so I'm sticking with standard library primitives here. Since we have D flip flop we can abstract it away into a single logisim component and it already exists in logisim. 

##### Creating the LUT
To create a Lookup table we needed a memory element that can store our custom truth table. An array of these flip flops that can be programmed are stored in one single register with the size $2^n$ where $n$ is the size of the array. Here is a 4 bit register for 2 inputs.

![4 bit register](20260926-1107-07.2627114.mp4 "4 bit register")

The D flip flop has set and reset pins that look connected here but are not actually connected, they're placed in close proximity such that they seem connected. Connecting them does nothing here but these set and reset pins have "authority" over the D pin, when set is high or reset is high, the D pin will not work. Now that we can store information, we need to be able to select what comes out based on out 2 inputs and would you look at that we get to use the multiplexer. Here's how I hooked it up to create a 2 input LUT. 
![2 input LUT](20260926-1121-21.9714965.mp4 "2 input LUT")
The dip switch box is out input of the LUT, the value written on the left side can be set by programming it and clocking once. 
Converting this to a 4 input LUT we get the following circuit:
![4 Input LUT](20260926-1136-34.2190547.mp4 "4 Input LUT")
I did not bother going thru the whole range in the video to keep the video short. 
#### Creating the full CLB
Now to create a CLB we need to have the LUT, a D flip flop and a mux to select which output to take. The LUT selects an output and a select pin selects whether to choose the output from the flip flop or the LUT. Here's the full CLB. I've chosen to use a ROM instead of a register to create the LUT because they are effictively the same. 
![Configurable Logic Block](20260926-1909-19.5097825.mp4 "Configurable Logic Block")

This is perhaps the most basic CLB one can make. There are some things needed to be cleared. Based on the previous material it might seem that LUTs are only made of an array of flip flops but that is not true, If that is how a register/LUT were then to store a single bit the number of transistors required would be much larger which then becomes a bottleneck. Instead SRAMs are used to store data. A LUT can be thought of as memory where a single bit is read instead of a byte or more and the input is an address. 

The CLBs used in modern FPGAs are more complex than this, they can have multiple LUTs, some adder and multiplier logic and lot more. I found it difficult to get my hands on a diagram that depicts what a modern CLB looks like but the following is a screenshot I took form this video about FPGAs by the youtube channel excessive overkill. ![alt text](modernCLB.png) As it says it's half a CLB. [Here's the link to the video](https://www.youtube.com/watch?v=d3nuepnbmC4)

These CLB's are arranged in a fabric, or a grid like pattern and then connected to each other using programmable interconnects. These programmable interconnects have switchboxes that decide which wire to connect to which CLB and they can be programmed too. Like the following:![alt text](fpgafabric.png)
Building this switchbox and simulating an FPGA fabric in logisim goes into FPGA CAD design stuff that I would like to refrain from going into because this series is about creating a pipelined RISC V CPU and not simulating an FPGA and writing compilers etc and it would not be a constructive detour from the original goal. These chips also contain DSPs that can be used to enhance multiplication and addition operations but I'm cutting the rabbit hole short here for this blog post. 

Moving forward I'm going to begin work on the CPU.

Joe Barnard says "may your skies be blue and your winds be low". I'd like to create my own. 

*May your logic be configurable!*