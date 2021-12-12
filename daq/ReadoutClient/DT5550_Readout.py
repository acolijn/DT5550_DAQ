from DT5550_Functions import *
from DT5550_io import *

import sys, getopt, time
import json
import numpy as np

#-----------------------------------------------------------------------------------------------------------------------
def main(argv):
    """
    MAIN CODE
    """
    # process command line arguments
    output_file = ''
    config_file = ''
    n_event = 0
    do_set_register = True

    try:
        opts, args = getopt.getopt(argv,"hn:o:c:i",["nevent=","ofile=","cfile=","init="])
    except getopt.GetoptError:
        print('DT5550_Readout.py -n <number of events> -o <outputfile> -c <configfile> -i')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('DT5550_Readout.py -n <number of events> -o <outputfile> -c <configfile> -i')
            sys.exit(2)
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-c", "--cfile"):
            config_file = arg
        elif opt in ("-n", "--nevent"):
            n_event = int(arg)
        elif opt in ("-i", "--init"):
            do_set_register = False

    #
    # instantiate object from DT5550_io class for DT5550 readout
    #
    io = DT5550_io(n_event=n_event, output_file=output_file, config_file=config_file)

    #
    # connect to the board and initialize the DAQ
    #
    io.initialize_daq()
    #
    # if we want to set the registers in the board do it here (only required once in principle)
    #
    if do_set_register:
        io.set_registers()

    #
    # go and fetch the data
    #
    io.read_data()

    print("Exit DAQ")
#-----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main(sys.argv[1:])