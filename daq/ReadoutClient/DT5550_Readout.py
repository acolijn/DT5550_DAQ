from DT5550_Functions import *
import sys, getopt, time
import json
import numpy as np

# number of bytes per event
EVENT_LENGTH = 18
# number of detectors
N_DETECTOR = 8
# termination
TERMINATION_50OHM = 1
TERMINATION_1MOHM = 0

def set_registers(handle, config_file):

    # read configuration from the config_file file
    if config_file == "":
        # not defined then read default....
        config_file = 'config.json'

    f = open(config_file,'r')
    data = json.load(f)
    f.close()
    # get the registers from teh config file
    reg = data['registers']

    # DC offset for the single-ended to differential converter
    # bottom row of DT5550AFE
    V_offset = reg['V_offset']
    V_max = 2.0

    #
    # from some repo of nuclear instruments..... funky conversion
    #
    DAC_offset = int((V_offset+V_max)/V_max/2*(4095-1650)+1650)
    print('DC offset =',V_offset,' DAC = ',DAC_offset)

    # set the base addresses for the i2c controller....
    SetAFEBaseAddress(handle)
    time.sleep(0.1)

    # set teh correct termination of the analog inputs
    SetAFEImpedance(TERMINATION_50OHM, handle)

    err = SetAFEOffset(0, DAC_offset, handle)
    time.sleep(0.1)

    # top row of DT5550AFE
    err = SetAFEOffset(1, DAC_offset, handle)
    time.sleep(0.1)


    # set the Integration time
    err = REG_INTTIME_SET(reg['INTTIME'], handle)
    time.sleep(0.1)

    # set the pre-integration time
    err = REG_PREINT_SET(reg['PREINIT'], handle)
    time.sleep(0.1)

    # set the baseline length: 2^n, where n is the value entered
    err = REG_BLLEN_SET(reg['BLLEN'], handle)
    time.sleep(0.1)

    # set the baseline hold time
    err = REG_BLHOLD_SET(reg['BLHOLD'], handle)
    time.sleep(0.1)

    # set the event window lenggth
    err = REG_WINDOW_SET(reg['WINDOW'], handle)
    time.sleep(0.1)

    # trigger mode: 0->single channel 1->two channels or more
    err = REG_TMODE_SET(reg['TMODE'], handle)
    time.sleep(0.1)

    for idet in range(N_DETECTOR):
        det_id = data['detector_settings'][idet]['det_id']
        # do we invert the AI or not
        err = REG_INVERT_SET(det_id,data['detector_settings'][idet]['INVERT'], handle)
        time.sleep(0.1)

        # set the detection threshold
        err = REG_THRS_SET(det_id,data['detector_settings'][idet]['THRS'], handle)
        time.sleep(0.1)

        # set the GAIN
        err = REG_GAIN_SET(det_id,data['detector_settings'][idet]['GAIN'], handle)
        time.sleep(0.1)

    return
#-----------------------------------------------------------------------------------------------------------------------
def initialize_daq():
    """

    :return: handle : handle to the DAQ system
    """

    #   List the DT5550 devices on the USB bus
    [ListOfDevices, count] = ListDevices()
    if count == 0:
        print("ERROR: No DAQ Devices")
        return -1

    # Derive the board id
    board = ListOfDevices[0].encode('utf-8')

    # Initialize the board and get a handle
    Init()
    [err, handle] = ConnectDevice(board)
    if (err == 0):
        print("Successful connection to board ", board)
    else:
        print("Connection Error")
        return -1



    return handle
#-----------------------------------------------------------------------------------------------------------------------
def read_data(filename, N_Total_Events, handle):
    """

    :param filename: name of the output binary data file
    :param N_Total_Events: total number of requested events
    :param handle: handle to DAQ system
    :return:
    """
    nloop = 0
    N_Packet = 1000
    Timeout_ms = 1000
    N_Read_Events = 0

    # open output file
    BinaryDataFile = open(filename,'wb')

    if (CPACK_CP_0_RESET(handle) != 0):
        print("Reset Error!")
    else:
        print("Reset Succes....")
    if (CPACK_CP_0_START(handle) == True):
        [err, Frame_Status] = CPACK_CP_0_GET_STATUS(handle)
        #
        # give USB bus a bit of time to process this......
        #
        time.sleep(0.1)

        #
        # start the data readout
        #
        print('Frame status =',Frame_Status)
        if (Frame_Status >0):
            while (N_Read_Events < N_Total_Events):
                #
                # read the frame data
                #
                [err, Frame_Data, Frame_Read_Data, Frame_Valid_Data] = CPACK_CP_0_GET_DATA(N_Packet, Timeout_ms, handle)
                #
                # decode the FrameData:
                #  1. find an event header
                #  2. patch the event together........
                #  3. increase the event count
                #
                frame_length = len(Frame_Data)
                index = 0

                while True:
                    if (Frame_Data[index] == 0xffffffff):
                        # found event
                        ##print('found event at index =',index)
                        for j in range(EVENT_LENGTH):
                            if j+index >= frame_length:
                                break
                            # write data to output file
                            BinaryDataFile.write(Frame_Data[j+index].to_bytes(4,byteorder='little'))

                        index = index + EVENT_LENGTH
                        N_Read_Events = N_Read_Events+1
                    else:
                        index = index + 1

                    if index >= frame_length:
                        break

                    if N_Read_Events >= N_Total_Events:
                        break


                print("Total Acquired Events: ", N_Read_Events)



                #DAC_offset = nloop*100
                #print('OFFSET=',DAC_offset)
                #err = SetAFEOffset(0, DAC_offset, handle)
                #time.sleep(0.1)

                # top row of DT5550AFE
                #err = SetAFEOffset(1, DAC_offset, handle)
                #time.sleep(0.1)


                #nloop = nloop +1
        else:
            print("Status Error")
    else:
        print("Start Error")

    # close output file
    BinaryDataFile.close()

    # close the connection to the board
    if CloseConnect(handle) == 0:
        print("Disconnect from device: SUCCES")
    else:
        print("Disconnect from device: FAIL")

    return
#-----------------------------------------------------------------------------------------------------------------------
def main(argv):
    """
    MAIN CODE
    """
    # process command line arguments
    output_file = ''
    config_file = ''
    n_event = 0

    try:
        opts, args = getopt.getopt(argv,"hn:o:c:",["nevent=","ofile=","cfile="])
    except getopt.GetoptError:
        print('DT5550_Readout.py -n <number of events> -o <outputfile> -c <configfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('DT5550_Readout.py -n <number of events> -o <outputfile> -c <configfile>')
            sys.exit(2)
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-c", "--cfile"):
            config_file = arg
        elif opt in ("-n", "--nevent"):
            n_event = int(arg)

    print('config = ',config_file)

    # initialize daq
    handle = initialize_daq()
    # set the registers on the DAQ
    set_registers(handle, config_file)
    # start readout
    if handle != -1:
        # read data
        read_data(output_file, n_event, handle)

    print("Exit DAQ")
#-----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main(sys.argv[1:])