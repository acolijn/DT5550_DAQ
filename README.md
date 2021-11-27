# FineStructure
Finestructure Constant lab setup

Software to control, readout and analyze a lab setup to measure the fine-structure constant. The DAQ unit is a DT5550+DT5550AFE unit from CAEN and firmware code 
has been developed in the SciCompiler development suite

# Contents

- daq/FinestructureFirmware: SciCompiler DT5550 firmware. Compiles with SciCompiler in combination with Xilinx Vivado v2017
- daq/ReadOutClient: python based client for the DT5550 DAQ board. Sets the registers in the unit and retrieves data over USB3
- analysis: data decoder DT5550.py and analysis code

## Author: A.P. Colijn / Nov. 2021
