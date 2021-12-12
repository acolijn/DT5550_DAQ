from DT5550_Functions import *

import sys, getopt, time
import json
import numpy as np

# number of bytes per event
EVENT_LENGTH = 18

class DT5550_io:
    """
    Basic class for DT5550 datataking
    """
    def __init__(self, **kwargs):
        """

        :param kwargs:
        """
        self.n_event = kwargs.pop('n_event',-1)
        self.output_file = kwargs.pop('output_file','None')
        self.config_file = kwargs.pop('config_file','None')
        self.readout_mode = kwargs.pop('mode','data') # 1. data 2. waveform 3. combined

        # handle to the USB....
        self.handle = -1
        # read the configuration data
        self.read_configuration()

        return

    def read_configuration(self):
        """
        Read the configuration from the json file
        :return:
        """
        # read configuration from the config_file file
        if self.config_file == "":
            # not defined then read default....
            self.config_file = 'config.json'

        print('read_configuration:: Configuration from: ', self.config_file)

        f = open(self.config_file, 'r')
        self.config_data = json.load(f)
        f.close()

        return 0

    def initialize_daq(self):
        """
        Initilaize the DT5550 DAQ board
        """

        #   List the DT5550 devices on the USB bus
        [ListOfDevices, count] = ListDevices()
        if count == 0:
            print("initialize_daq:: ERROR: No DAQ Devices")
            return -1

        # Derive the board id
        board = ListOfDevices[0].encode('utf-8')

        # Initialize the board and get a handle
        Init()
        [err, self.handle] = ConnectDevice(board)
        if (err == 0):
            print("initialize_daq:: Successful connection to board ", board)
        else:
            print("initialize_daq:: Connection Error")
            return -1

        return 0

    def set_registers(self):
        """
        Set the control registers in the DT5550 and DT5550AFE
        :return:
        """

        print('set_registers:: Set up the registers in the DT5550. handle=', self.handle)

        # get the registers from the config file
        reg = self.config_data['registers']

        # DC offset for the single-ended to differential converter
        # bottom row of DT5550AFE
        V_offset = reg['V_offset']

        #
        # I actually think that the maximum dV = +-0.9V (????)
        #
        V_max = 1.8

        #
        # from some repo of nuclear instruments..... funky conversion
        #
        ####DAC_offset = int((V_offset+V_max)/V_max/2*(4095-1650)+1650)

        #
        # but now I think it should be like this.....
        #
        DAC_offset = int(1024 * V_offset / V_max * 2 + 2048)
        # set the base addresses for the i2c controller....
        SetAFEBaseAddress(self.handle)
        time.sleep(0.1)

        # set the correct termination of the analog inputs

        print('set_registers:: DT5550AFE:: Input Impedance =', reg['Termination'])
        termination = reg['Termination']
        if termination == TERMINATION_50OHM:
            SetAFEImpedance(TERMINATION_50OHM, self.handle)
        elif termination == TERMINATION_1KOHM:
            SetAFEImpedance(TERMINATION_1KOHM, self.handle)
        else:
            print('set_registers:: DT5550AFE:: ERROR Wrong termination chosen')
            return -1

        # set the DDC offsets

        # bottom row of DT5550AFE
        print('set_registers:: DT5550AFE:: DC offset =', V_offset, 'V DAC = ', DAC_offset)

        SetAFEOffset(0, DAC_offset, self.handle)
        time.sleep(0.1)
        # top row of DT5550AFE
        SetAFEOffset(1, DAC_offset, self.handle)
        time.sleep(0.1)

        # set the Integration time
        print('set_registers:: Integration time =', reg['INTTIME'] * CLK, ' ns')
        REG_INTTIME_SET(reg['INTTIME'], self.handle)
        time.sleep(0.1)

        # set the pre-integration time
        print('set_registers:: Pre-integration time =', reg['PREINIT'] * CLK, ' ns')
        REG_PREINT_SET(reg['PREINIT'], self.handle)
        time.sleep(0.1)

        # set the baseline length: 2^n, where n is the value entered
        print('set_registers:: Baseline length =', reg['BLLEN'], ' (see manual)')
        REG_BLLEN_SET(reg['BLLEN'], self.handle)
        time.sleep(0.1)

        # set the baseline hold time
        print('set_registers:: Baseline hold time =', reg['BLHOLD'], ' (see manual)')
        REG_BLHOLD_SET(reg['BLHOLD'], self.handle)
        time.sleep(0.1)

        # set the event window lenggth
        print('set_registers:: Event window =', reg['WINDOW'] * CLK, ' (ns)')
        REG_WINDOW_SET(reg['WINDOW'], self.handle)
        time.sleep(0.1)

        # trigger mode: 0->single channel 1->two channels or more
        print('set_registers:: Tigger mode =', reg['TMODE'])
        REG_TMODE_SET(reg['TMODE'], self.handle)
        time.sleep(0.1)

        for idet in range(N_DETECTOR):
            det_id = self.config_data['detector_settings'][idet]['det_id']
            thrs = self.config_data['detector_settings'][idet]['THRS']
            invert = self.config_data['detector_settings'][idet]['INVERT']
            gain = self.config_data['detector_settings'][idet]['GAIN']

            # do we invert the AI or not
            print('set_registers::        id', det_id, ' THRS =', thrs, ' GAIN =', gain, ' INVERT=', invert)

            REG_INVERT_SET(det_id, invert, self.handle)
            time.sleep(0.1)
            # set the detection threshold
            REG_THRS_SET(det_id, thrs, self.handle)
            time.sleep(0.1)

            # set the GAIN
            REG_GAIN_SET(det_id, gain, self.handle)
            time.sleep(0.1)

        return 0

    def read_data(self):
        """
        read data from the DT5550 through USB3

        :return:
        """
        N_Packet = 1000
        Timeout_ms = 1000
        N_Read_Events = 0

        # open output file
        print("read_data:: Output written to: ",self.output_file)
        BinaryDataFile = open(self.output_file, 'wb')

        if (CPACK_CP_0_RESET(self.handle) != 0):
            print("Reset Error!")
        else:
            print("Reset Succes....")
        if (CPACK_CP_0_START(self.handle) == True):
            [err, Frame_Status] = CPACK_CP_0_GET_STATUS(self.handle)
            #
            # give USB bus a bit of time to process this......
            #
            time.sleep(0.1)

            #
            # start the data readout
            #
            if (Frame_Status > 0):
                while (N_Read_Events < self.n_event):
                    #
                    # read the frame data
                    #
                    [err, Frame_Data, Frame_Read_Data, Frame_Valid_Data] = CPACK_CP_0_GET_DATA(N_Packet, Timeout_ms,
                                                                                               self.handle)
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

                        if N_Read_Events >= self.n_event:
                            break

                    print("Total Acquired Events: ", N_Read_Events)
            else:
                print("Status Error")
        else:
            print("Start Error")

        # close output file
        BinaryDataFile.close()

        # close the connection to the board
        if CloseConnect(self.handle) == 0:
            print("Disconnect from device: SUCCES")
        else:
            print("Disconnect from device: FAIL")

        return 0