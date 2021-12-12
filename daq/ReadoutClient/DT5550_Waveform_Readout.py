from DT5550_Functions import *
# from DT5550_io import DT5550_io

import sys, getopt, time
import json
import numpy as np

def setup_oscilloscope(handle, config_file):
    print('setup_oscilloscope:: Set up the registers in the DT5550')

    # read configuration from the config_file file
    if config_file == "":
        # not defined then read default....
        config_file = 'config.json'

    print('setup_oscilloscope:: Configuration from: ',config_file)
    f = open(config_file,'r')
    data = json.load(f)
    f.close()

    settings = data['waveform_settings']

    Decimator = settings['decimator']
    Pre_Trigger = settings['pre_trigger']
    Trigger_Level = settings['threshold']
    Trigger_Channel = settings['channel']
    Trigger_Mode = settings['mode']#"Analog"  # ""Analog" #"Free", "Analog", "Digital0", "Digital1", "Digital2", "Digital3"
    Trigger_Edge = settings['edge']  # "Rising", "Falling"

    if (OSCILLOSCOPE_Oscilloscope_0_SET_DECIMATOR(Decimator, handle) != 0):
        print("Set Decimator Error")
        exit
    # time.sleep(0.1)

    if (OSCILLOSCOPE_Oscilloscope_0_SET_PRETRIGGER(Pre_Trigger, handle) != 0):
        print("Set PreTrigger Error")
        exit
    # time.sleep(0.1)

    if (OSCILLOSCOPE_Oscilloscope_0_SET_TRIGGER_LEVEL(Trigger_Level, handle) != 0):
        print("Set Trigger Level Error")
        exit
    # time.sleep(0.1)

    if (OSCILLOSCOPE_Oscilloscope_0_SET_TRIGGER_MODE(Trigger_Mode, Trigger_Channel, Trigger_Edge, handle) != 0):
        print("Set Trigger Mode Error")
        exit

    return Pre_Trigger
#---------------------------------------------------------------------------------------------------
def main(argv):
    """
    MAIN CODE
    """
    # process command line arguments
    output_file = ''
    #
    config_file = ''
    n_event = 0
    do_set_register = True

    try:
        opts, args = getopt.getopt(argv,"hn:o:c:i",["nevent=","ofile=","cfile=","init="])
    except getopt.GetoptError:
        print('DT5550_Waveform_Readout.py -n <number of events> -o <outputfile> -c <configfile> -i')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('DT5550_Waveform_Readout.py -n <number of events> -o <outputfile> -c <configfile> -i')
            sys.exit(2)
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-c", "--cfile"):
            config_file = arg
        elif opt in ("-n", "--nevent"):
            n_event = int(arg)
        elif opt in ("-i", "--init"):
            do_set_register = False

    iopt = 1
    if iopt == 0:
        #
        # instantiate object from DT5550_io class for DT5550 readout
        #
        io = DT5550_io(n_event=n_event, output_file=output_file, config_file=config_file)

        #
        # connect to the board and initialize the DAQ
        #
        handle = io.IO_initialize_daq()
        #
        # if we want to set the registers in the board do it here (only required once in principle)
        #
        if do_set_register:
            io.IO_set_registers(handle=handle)

        #
        # setup the oscilloscope
        #
        io.IO_setup_oscilloscope(handle=handle)
        #
        # go and fetch the data
        #
        io.IO_read_waveforms(handle=handle)

    else: # BELOW WORKS

        # initialize daq
        handle = initialize_daq()
        # set the registers on the DAQ
        if do_set_register:
            set_registers(handle, config_file)


        Oscilloscope_Status = 0
        Timeout_ms = 1000

        ievent = 0
        fout = open(output_file,'wb')

        # setup oscilloscope... (the onluy variable needed here is the Pre_Trigger..... (ugly coding)
        Pre_Trigger = setup_oscilloscope(handle,config_file)

        while(ievent < n_event):
            # start reading the scope
            if (OSCILLOSCOPE_Oscilloscope_0_START(handle) == True):
                # give the scope a small break......
                time.sleep(0.1)

                # wait for a trigger to arrive......
                while (Oscilloscope_Status != 1):
                    [err, Oscilloscope_Status] = OSCILLOSCOPE_Oscilloscope_0_GET_STATUS(handle)
                    print('Status waiting for trigger ...',Oscilloscope_Status)
                # scope finds a trigegr at a certain location in the circular buffer
                [err, Event_Position] = OSCILLOSCOPE_Oscilloscope_0_GET_POSITION(handle)
                # get the data.....
                [err, Oscilloscope_Data, Oscilloscope_Read_Data, Oscilloscope_Valid_Data] = OSCILLOSCOPE_Oscilloscope_0_GET_DATA(Timeout_ms, handle)
                # reconstruct the data from the scope
                Processed_Data = OSCILLOSCOPE_Oscilloscope_0_RECONSTRUCT_DATA(Oscilloscope_Data, Event_Position, Pre_Trigger)
                np.array(Processed_Data).tofile(fout)
                if ievent%10 == 0:
                    print('DT5550_Waveform_Readout:: Read ',ievent,' waveforms')
                ievent = ievent +1

            else:
                print("Start Error")

        fout.close()
        # close the connection to the board
        if CloseConnect(handle) == 0:
            print("Disconnect from device: SUCCES")
        else:
            print("Disconnect from device: FAIL")

    return
#-----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main(sys.argv[1:])