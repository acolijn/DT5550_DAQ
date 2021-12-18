from DT5550_Functions import *
# import DT5550_io

import sys, getopt, time

def read_data(output_file, n_event, handle):
    """
    read data from the DT5550 through USB3

    :return:
    """
    N_Packet = 1000
    Timeout_ms = 1000
    N_Read_Events = 0

    # open output file
    print("read_data:: Output written to: ", output_file)
    BinaryDataFile = open(output_file, 'wb')

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
        if (Frame_Status > 0):
            while (N_Read_Events < n_event):
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
                            if j + index >= frame_length:
                                break
                            # write data to output file
                            BinaryDataFile.write(Frame_Data[j + index].to_bytes(4, byteorder='little'))

                        index = index + EVENT_LENGTH
                        N_Read_Events = N_Read_Events + 1
                    else:
                        index = index + 1

                    if index >= frame_length:
                        break

                    if N_Read_Events >= n_event:
                        break

                print("Total Acquired Events: ", N_Read_Events)
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

    return 0
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
        opts, args = getopt.getopt(argv, "hn:o:c:i", ["nevent=", "ofile=", "cfile=", "init="])
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

    #iopt = 1
    #
    # if iopt == 0:
    #     io = DT5550_io(n_event=n_event, output_file=output_file, config_file=config_file)
    #
    #     io.IO_initialize_daq()
    #     if do_set_register:
    #         io.IO_set_registers()
    #
    #     io.IO_read_data()
    # elif iopt == 1:

    handle = -1

    ntry = 0
    # try to init the DAQ 3x. If the handle still equals -1..... bad luck.
    while ntry < 3:
        handle = initialize_daq()
        if handle == -1:
            time.sleep(1.0)
            ntry = ntry + 1
        else:
            break

    if handle != -1:
        # set the registers on the DAQ
        if do_set_register:
            set_registers(handle, config_file)
        # read data
        read_data(output_file, n_event, handle)

    print("Exit DAQ")
#-----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main(sys.argv[1:])