#from DT5550_Functions import *
import time

import matplotlib.pyplot as plt
from DT5550_io import DT5550_io

import sys
import getopt

#-----------------------------------------------------------------------------------------------------------------------
def main(argv):
    """
    MAIN CODE
    """
    # process command line arguments
    output_file = ''
    config_file = ''
    mode = ''
    n_event = 0
    do_set_register = True

    try:
        opts, args = getopt.getopt(argv, "hn:o:c:im:", ["nevent=", "ofile=", "cfile=", "init=", "mode="])
    except getopt.GetoptError:
        print('DT5550_Readout.py -n <number of events> -o <outputfile> -c <configfile> -i')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('DT5550_Readout.py -n <number of events> -o <outputfile> -c <configfile> -i -m <readout_mode = data / osc>')
            sys.exit(2)
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-c", "--cfile"):
            config_file = arg
        elif opt in ("-n", "--nevent"):
            n_event = int(arg)
        elif opt in ("-m", "--mode"):
            mode = arg
        elif opt in ("-i", "--init"):
            do_set_register = False

    print(n_event, output_file, config_file)
    # instantiate readout class
    io = DT5550_io(n_event=n_event, output_file=output_file, config_file=config_file)
    time.sleep(0.2)
    # initialize the DAQ
    io.IO_initialize_daq()
    time.sleep(0.5)
    # set registers if required
    if do_set_register:
        io.IO_set_registers()

    if mode == "data":  # readout processed data
        # read the required number of events from the DT5550
        io.IO_read_data()
    elif mode == "osc":  # oscilloscope mode
        # setup the oscilloscope
        io.IO_setup_oscilloscope()
        # go and fetch the waveforms
        io.IO_read_waveforms()
    else:
        print("DT5550_Readout:: ERROR wrong readout mode selected")

    print("Exit DAQ")
#-----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main(sys.argv[1:])

