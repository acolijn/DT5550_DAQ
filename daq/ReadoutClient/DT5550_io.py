from DT5550_Functions import *

import time
import json
import numpy as np

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
        #self.readout_mode = kwargs.pop('mode','data') # 1. data 2. waveform 3. combined

        # handle to the USB....
        self.handle = c_void_p(-1)
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


        return

    def IO_initialize_daq(self):
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

        ntry = 5
        itry = 0

        while (1):
            [err, self.handle] = ConnectDevice(board)
            if (err == 0):
                print("initialize_daq:: Successful connection to board ", board)
                break
            elif (err != 0) and (itry < ntry):
                print("initialize_daq:: Connection Error.... retry connect")
                itry = itry+1
            elif (err != 0) and (itry >= ntry):
                print("initialize_daq:: Connection Error.... terminate")
                break

        return

    def IO_set_registers(self):
        """
        Set the control registers in the DT5550 and DT5550AFE
        :return:
        """

        print('set_registers:: Set up the registers in the DT5550. handle=', self.handle)

        # read configuration from the config_file file
        if self.config_file == "":
            # not defined then read default....
            self.config_file = 'config.json'

        print('set_registers:: Configuration from: ', self.config_file)

        f = open(self.config_file, 'r')
        data = json.load(f)
        f.close()
        # get the registers from teh config file

        reg = data['registers']
        print(reg)
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
        time.sleep(0.3)

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
        time.sleep(0.3)
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

        # trigger mode: 0->single channel 1->two channels or more (OBSOLETE)
        print('set_registers:: Tigger mode =', reg['TMODE'])
        REG_TMODE_SET(reg['TMODE'], self.handle)
        time.sleep(0.1)

        # trigger: minimum energy
        print('set_registers:: Energy threshold for the Energy trigger =', reg['EMIN'])
        REG_EMIN_SET(reg['EMIN'], self.handle)
        time.sleep(0.1)

        # trigger: minimum number of channels
        print('set_registers:: Minimal number of detector hit =', reg['NMIN'])
        REG_NMIN_SET(reg['NMIN'], self.handle)
        time.sleep(0.1)

        for idet in range(N_DETECTOR):
            det_id = data['detector_settings'][idet]['det_id']
            base = data['detector_settings'][idet]['BASE']
            thrs = data['detector_settings'][idet]['THRS']
            invert = data['detector_settings'][idet]['INVERT']
            gain = data['detector_settings'][idet]['GAIN']

            # do we invert the AI or not
            print('set_registers::        id', det_id, ' THRS =', thrs, ' GAIN =', gain, ' INVERT=', invert)

            REG_INVERT_SET(det_id, invert, self.handle)
            time.sleep(0.1)
            # set the detection threshold: the THRS value is how high above the baseline you want the trigger to be.
            # the baseline calculated from the baseline_calculator notebook in the analysis directory of this repo.
            #
            threshold = base + thrs
            REG_THRS_SET(det_id, threshold, self.handle)
            time.sleep(0.1)

            # set the GAIN
            REG_GAIN_SET(det_id, gain, self.handle)
            time.sleep(0.1)

        return

    def IO_setup_oscilloscope(self):
        """
        Setup Oscilloscope readout mode
        :return: 
        """

        print("IO_setup_oscilloscope:: Setup the oscilloscope")

        settings = self.config_data['waveform_settings']

        Decimator = settings['decimator']
        Pre_Trigger = settings['pre_trigger']
        Trigger_Level = settings['threshold']
        Trigger_Channel = settings['channel']
        Trigger_Mode = settings['mode']  # "Analog"  # ""Analog" #"Free", "Analog", "Digital0", "Digital1", "Digital2", "Digital3"
        Trigger_Edge = settings['edge']  # "Rising", "Falling"

        # print(Decimator, Pre_Trigger, Trigger_Level, Trigger_Channel, Trigger_Mode, Trigger_Edge)
        # print(self.handle)
        # print(OSCILLOSCOPE_Oscilloscope_0_SET_DECIMATOR(Decimator, self.handle))

        if (OSCILLOSCOPE_Oscilloscope_0_SET_DECIMATOR(Decimator, self.handle) != 0):
            print("Set Decimator Error")
            exit
        time.sleep(0.1)

        if (OSCILLOSCOPE_Oscilloscope_0_SET_PRETRIGGER(Pre_Trigger, self.handle) != 0):
            print("Set PreTrigger Error")
            exit

        time.sleep(0.1)

        if (OSCILLOSCOPE_Oscilloscope_0_SET_TRIGGER_LEVEL(Trigger_Level, self.handle) != 0):
            print("Set Trigger Level Error")
            exit

        time.sleep(0.1)

        if (OSCILLOSCOPE_Oscilloscope_0_SET_TRIGGER_MODE(Trigger_Mode, Trigger_Channel, Trigger_Edge, self.handle) != 0):
            print("Set Trigger Mode Error")
            exit

        print("IO_setup_oscilloscope:: Setup the oscilloscope = Finished")

        return

    def IO_read_data(self):
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
                while (N_Read_Events < self.n_event - 1):
                    #
                    # read the frame data
                    #
                    [err, Frame_Data, Frame_Read_Data, Frame_Valid_Data] = CPACK_CP_0_GET_DATA(N_Packet, Timeout_ms, self.handle)
                    #
                    # decode the FrameData:
                    #  1. find an event header
                    #  2. patch the event together........
                    #  3. increase the event count
                    #
                    frame_length = len(Frame_Data)
                    #print('LEN = ', len(Frame_Data))

                    index = 0
                    #print('startit......')
                    while True:
                        #print(index,  ' d000=', hex(Frame_Data[index]))

                        if (Frame_Data[index] == 0xffffffff):
                            # found event
                            ##print('found event at index =',index)
                            for j in range(EVENT_LENGTH):
                                if j + index >= frame_length:
                                    break
                                # write data to output file
                                #print(index,j,' d=',hex(Frame_Data[j + index]))

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

    def IO_read_waveforms(self):
        """
        Readout Oscilloscope waveform
        :return:
        """
        Oscilloscope_Status = 0
        Timeout_ms = 1000

        ievent = 0
        fout = open(self.output_file, 'wb')

        # Pre_Trigger samples in oscilloscope....
        Pre_Trigger = int(self.config_data['waveform_settings']['pre_trigger'])

        while (ievent < self.n_event):
            # start reading the scope
            if not OSCILLOSCOPE_Oscilloscope_0_START(self.handle):
                print("Start Error")
            # start reading the scope
            else:
                # give the scope a small break......
                time.sleep(0.1)

                # wait for a trigger to arrive......
                while (Oscilloscope_Status != 1):
                    [_, Oscilloscope_Status] = OSCILLOSCOPE_Oscilloscope_0_GET_STATUS(self.handle)
                    print('Status waiting for trigger ...', Oscilloscope_Status)
                # scope finds a trigegr at a certain location in the circular buffer
                [_, Event_Position] = OSCILLOSCOPE_Oscilloscope_0_GET_POSITION(self.handle)
                # get the data.....
                [_, Oscilloscope_Data, _, _] = OSCILLOSCOPE_Oscilloscope_0_GET_DATA(Timeout_ms, self.handle)
                # reconstruct the data from the scope
                Processed_Data = OSCILLOSCOPE_Oscilloscope_0_RECONSTRUCT_DATA(Oscilloscope_Data, Event_Position, Pre_Trigger)
                np.array(Processed_Data).tofile(fout)
                if ievent % 10 == 0:
                    print('DT5550_Waveform_Readout:: Read ', ievent, ' waveforms')
                ievent = ievent + 1

        fout.close()
        # close the connection to the board
        if CloseConnect(self.handle) == 0:
            print("Disconnect from device: SUCCES")
        else:
            print("Disconnect from device: FAIL")

        return
