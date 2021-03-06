# DT5550-DAQ

Software to control, readout and analyze a lab setup with a CAEN DT5550 FPGA unit. Firmware code 
is developed in the SciCompiler development suite

### Contents

- daq/FinestructureFirmware: SciCompiler DT5550 firmware. Compiles with SciCompiler in combination with Xilinx Vivado v2017
- daq/ReadOutClient: python based client for the DT5550 DAQ board. Sets the registers in the unit and retrieves data over USB3
- daq/DAQgui: GUI for data-acquisition control (under construction)
- analysis: data decoder DT5550.py and analysis code
- analysis/waveplot: waveform plotting GUI

### Info
Author: A.P. Colijn / Jan. 2022
