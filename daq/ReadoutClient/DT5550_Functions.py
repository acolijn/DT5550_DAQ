import RegisterFile
import json, time
from ctypes import *

# number of bytes per event
EVENT_LENGTH = 18
# number of detectors
N_DETECTOR = 8
# termination
TERMINATION_50OHM = 1
TERMINATION_1MOHM = 0
# clock speed of DT5550
CLK = 12.5

#
# load the USB3 communication library
#
mydll = cdll.LoadLibrary('niusb3_core.dll') 

def Init():
    err = mydll.NI_USB3_Init()
    return err

def ConnectDevice(board):
    handle = c_void_p(256)
    err = mydll.NI_USB3_ConnectDevice(board, byref(handle))
    return err, handle

def CloseConnect(handle):
    err = mydll.NI_USB3_CloseConnection(byref(handle))
    return err    
    
def ListDevices():
    count = c_int(0)
    s = create_string_buffer(2048)
    err = mydll.NI_USB3_ListDevices(byref(s), 0, byref(count))
    str_con = (s.value.decode('ascii')) 
    str_devices = str_con.split(';')
    dev_count = count.value
    return str_devices, dev_count 

def __abstracted_reg_write(data, address, handle):
    err = mydll.NI_USB3_WriteReg(data, address, byref(handle))
    return err

def __abstracted_reg_read(address, handle):
    data = c_uint(0)
    err = mydll.NI_USB3_ReadReg(byref(data), address, byref(handle))
    return err, data.value

def __abstracted_mem_write(data, count, address, timeout_ms, handle):
    written_data = c_uint(0)
    err = mydll.NI_USB3_WriteData(data, count, address, 0, timeout_ms, byref(handle), byref(written_data))
    return err, written_data.value

def __abstracted_mem_read(count, address, timeout_ms, handle):
    data = (c_uint * (1 * count))()
    read_data = (c_int * 1)()
    valid_data = (c_int * 1)()

    err = mydll.NI_USB3_ReadData(data, count, address, 0, timeout_ms, byref(handle), byref(read_data), byref(valid_data))
    return err, data, read_data, valid_data


def __abstracted_fifo_read(count, address, address_status, blocking, timeout_ms, handle):
    data = (c_uint * (2* count))()
    read_data = c_uint(0)
    valid_data = c_uint(0)
    err = mydll.NI_USB3_ReadData(byref(data), count, address, 0, timeout_ms, byref(handle), byref(read_data), byref(valid_data))
    return err, data, read_data.value, valid_data.value

def __abstracted_fifo_write(data, count, address, timeout_ms, handle):
    written_data = c_uint(0)
    err = mydll.NI_USB3_WriteData(data, count, address, 1, timeout_ms, byref(handle), byref(written_data))
    return err, written_data.value

def __abstracted_fifo_read(count, address, timeout_ms, handle):
    # data = (c_uint * (2 * count))()
    data = (c_uint * (1 * count))()
    read_data = (c_int * 1)()
    valid_data = (c_int * 1)()
    err = mydll.NI_USB3_ReadData(byref(data), count, address, 1, timeout_ms, byref(handle), byref(read_data), byref(valid_data))
    return err, data, read_data, valid_data     

#
# communications to the I2C bus to teh DT5550AFE
#
def SetAFEBaseAddress(handle):
    err = mydll.NI_USB3_SetIICControllerBaseAddress(RegisterFile.SCI_REG_i2c_master_0_CTRL, RegisterFile.SCI_REG_i2c_master_0_MON, byref(handle))
    return err

def SetAFEOffset(top, value, handle):
    err = mydll.NI_USB3_SetOffset(top, value, byref(handle))   
    return err

def SetAFEImpedance(value, handle):
    err = mydll.NI_USB3_SetImpedance(value, byref(handle))
    return err

#
# registers on the DT5550
#
def REG_INTTIME_GET(handle):
    [err, data] = __abstracted_reg_read(RegisterFile.SCI_REG_INTTIME, handle)
    return err, data

def REG_INTTIME_SET(data, handle):
    err = __abstracted_reg_write(data, RegisterFile.SCI_REG_INTTIME, handle)
    return err

def REG_PREINT_GET(handle):
    [err, data] = __abstracted_reg_read(RegisterFile.SCI_REG_PREINT, handle)
    return err, data

def REG_PREINT_SET(data, handle):
    err = __abstracted_reg_write(data, RegisterFile.SCI_REG_PREINT, handle)
    return err

#def REG_GAIN_GET(handle):
#    [err, data] = __abstracted_reg_read(RegisterFile.SCI_REG_GAIN, handle)
#    return err, data

def REG_GAIN_SET(idet, data, handle):
    address = RegisterFile.SCI_REG_GAIN_BASE+idet+1
    err = __abstracted_reg_write(data, address, handle)
    return err

#def REG_THRS_GET(handle):
#    [err, data] = __abstracted_reg_read(RegisterFile.SCI_REG_THRS, handle)
#    return err, data

def REG_THRS_SET(idet, data, handle):
    address = RegisterFile.SCI_REG_THRS_BASE+idet+1
    err = __abstracted_reg_write(data, address , handle)
    return err

def REG_BLLEN_GET(handle):
    [err, data] = __abstracted_reg_read(RegisterFile.SCI_REG_BLLEN, handle)
    return err, data

def REG_BLLEN_SET(data, handle):
    err = __abstracted_reg_write(data, RegisterFile.SCI_REG_BLLEN, handle)
    return err

def REG_BLHOLD_GET(handle):
    [err, data] = __abstracted_reg_read(RegisterFile.SCI_REG_BLHOLD, handle)
    return err, data

def REG_BLHOLD_SET(data, handle):
    err = __abstracted_reg_write(data, RegisterFile.SCI_REG_BLHOLD, handle)
    return err

def REG_TSIN_GET(handle):
    [err, data] = __abstracted_reg_read(RegisterFile.SCI_REG_TSIN, handle)
    return err, data

def REG_TSIN_SET(data, handle):
    err = __abstracted_reg_write(data, RegisterFile.SCI_REG_TSIN, handle)
    return err

def REG_WINDOW_GET(handle):
    [err, data] = __abstracted_reg_read(RegisterFile.SCI_REG_WINDOW, handle)
    return err, data

def REG_WINDOW_SET(data, handle):
    err = __abstracted_reg_write(data, RegisterFile.SCI_REG_WINDOW, handle)
    return err

def REG_REARM_GET(handle):
    [err, data] = __abstracted_reg_read(RegisterFile.SCI_REG_REARM, handle)
    return err, data

def REG_REARM_SET(data, handle):
    err = __abstracted_reg_write(data, RegisterFile.SCI_REG_REARM, handle)
    return err

#def REG_INVERT_GET(handle):
#    [err, data] = __abstracted_reg_read(RegisterFile.SCI_REG_INVERT, handle)
#    return err, data

def REG_INVERT_SET(idet, data, handle):
    address = RegisterFile.SCI_REG_INVERT_BASE + idet + 1
    err = __abstracted_reg_write(data, address , handle)
    return err

def REG_TMODE_GET(handle):
    [err, data] = __abstracted_reg_read(RegisterFile.SCI_REG_TMODE, handle)
    return err, data

def REG_TMODE_SET(data, handle):
    err = __abstracted_reg_write(data, RegisterFile.SCI_REG_TMODE, handle)
    return err

def OSCILLOSCOPE_Oscilloscope_0_START(handle):
    err = __abstracted_reg_write(0, RegisterFile.SCI_REG_Oscilloscope_0_CONFIG_ARM, handle)
    if (err != 0):
       return False
    err = __abstracted_reg_write(1, RegisterFile.SCI_REG_Oscilloscope_0_CONFIG_ARM, handle)
    if (err != 0):
       return False
    return True

def OSCILLOSCOPE_Oscilloscope_0_SET_DECIMATOR(OscilloscopeDecimator, handle):
    err = __abstracted_reg_write(OscilloscopeDecimator, RegisterFile.SCI_REG_Oscilloscope_0_CONFIG_DECIMATOR, handle)
    return err

def OSCILLOSCOPE_Oscilloscope_0_SET_PRETRIGGER(OscilloscopePreTrigger, handle):
    err = __abstracted_reg_write(OscilloscopePreTrigger, RegisterFile.SCI_REG_Oscilloscope_0_CONFIG_PRETRIGGER, handle)
    return err

def OSCILLOSCOPE_Oscilloscope_0_SET_TRIGGER_LEVEL(OscilloscopeTriggerLevel, handle):
    err = __abstracted_reg_write(OscilloscopeTriggerLevel, RegisterFile.SCI_REG_Oscilloscope_0_CONFIG_TRIGGER_LEVEL, handle)
    return err

def OSCILLOSCOPE_Oscilloscope_0_SET_TRIGGER_MODE(OscilloscopeTriggerMode, OscilloscopeTriggerChannel, OscilloscopeTriggerEdge, handle):
    """
    Set the trigger configuration for the waveform readout

    :param OscilloscopeTriggerMode: "external", "Analog", "Digital[0:3]"
    :param OscilloscopeTriggerChannel: channel to trigger on - only relevant if OscilloscopeTriggerMode!= "external"
    :param OscilloscopeTriggerEdge: "Rising" / "Falling"  - only relevant if ......
    :param handle:
    :return:
    """
    triggermode = 0

    if OscilloscopeTriggerMode != "external":
        AnalogTrigger = 0
        Digital0Trigger = 0
        Digital1Trigger = 0
        Digital2Trigger = 0
        Digital3Trigger = 0
        SoftwareTrigger = 0
        if (OscilloscopeTriggerMode == "Analog"):
            AnalogTrigger = 1
        if (OscilloscopeTriggerMode == "Digital0"):
            Digital0Trigger = 1
        if (OscilloscopeTriggerMode == "Digital1"):
            Digital1Trigger = 1
        if (OscilloscopeTriggerMode == "Digital2"):
            Digital2Trigger = 1
        if (OscilloscopeTriggerMode == "Digital3"):
            Digital3Trigger = 1
        if (OscilloscopeTriggerMode == "Free"):
            SoftwareTrigger = 1
        if (OscilloscopeTriggerEdge == "Rising"):
            Edge = 0
        else:
            Edge = 1
        triggermode = (OscilloscopeTriggerChannel << 8)  + (SoftwareTrigger << 7 ) + (Edge << 3) + (SoftwareTrigger << 1) + AnalogTrigger +(Digital0Trigger << 2) + (Digital1Trigger << 2) + Digital1Trigger + (Digital2Trigger << 2) + (Digital2Trigger << 1) + (Digital3Trigger << 2) + (Digital3Trigger << 1) + Digital3Trigger
    else: # external trigger mode
        triggermode = 0x00

    print('TMODE = ',triggermode)
    err = __abstracted_reg_write(triggermode, RegisterFile.SCI_REG_Oscilloscope_0_CONFIG_TRIGGER_MODE, handle)
    return err

def OSCILLOSCOPE_Oscilloscope_0_GET_STATUS(handle):
    [err, status] = __abstracted_reg_read(RegisterFile.SCI_REG_Oscilloscope_0_READ_STATUS, handle)
    return err, status

def OSCILLOSCOPE_Oscilloscope_0_GET_POSITION(handle):
    [err, position] = __abstracted_reg_read(RegisterFile.SCI_REG_Oscilloscope_0_READ_POSITION, handle)
    return err, position

def OSCILLOSCOPE_Oscilloscope_0_GET_DATA(timeout_ms, handle):
    [err, data, read_data, valid_data] = __abstracted_mem_read(8*1024, RegisterFile.SCI_REG_Oscilloscope_0_FIFOADDRESS, timeout_ms, handle)
    return err, data, read_data, valid_data

def OSCILLOSCOPE_Oscilloscope_0_RECONSTRUCT_DATA(OscilloscopeData, OscilloscopePosition, OscilloscopePreTrigger):
    OscilloscopeChannels = 8
    OscilloscopeSamples = 1024
    Analog = list(range(OscilloscopeSamples*OscilloscopeChannels))

    for n in range(OscilloscopeChannels):
        current = OscilloscopePosition - OscilloscopePreTrigger
        if ((current) > 0):
            k = 0
            for i in range(current, OscilloscopeSamples-1):
                Analog[k+ OscilloscopeSamples * n] = OscilloscopeData[i+ OscilloscopeSamples * n] & 0x000fffff
                k = k + 1
            for i in range(0, current-1):
                Analog[k+ OscilloscopeSamples * n] = OscilloscopeData[i+ OscilloscopeSamples * n] & 0x000fffff
                k = k + 1

        else:
            k = 0
            for i in range(OscilloscopeSamples+current, OscilloscopeSamples-1):
                Analog[k+ OscilloscopeSamples * n] = OscilloscopeData[i+ OscilloscopeSamples * n] & 0x000fffff
                k = k + 1
            for i in range(0, OscilloscopeSamples+current-1):
                Analog[k+ OscilloscopeSamples * n] = OscilloscopeData[i+ OscilloscopeSamples * n] & 0x000fffff
                k = k + 1
    #for k in range(len(Analog)):
    #   if (Analog[k]&0x0000ffff<10000) and (k>0):
    #      Analog[k] = Analog[k-1]

    return Analog

def CPACK_CP_0_RESET(handle):
    err = __abstracted_reg_write(2, RegisterFile.SCI_REG_CP_0_CONFIG, handle)
    err = __abstracted_reg_write(0, RegisterFile.SCI_REG_CP_0_CONFIG, handle)
    return err

def CPACK_CP_0_FLUSH(handle):
    err = __abstracted_reg_write(4, RegisterFile.SCI_REG_CP_0_CONFIG, handle)
    err = __abstracted_reg_write(0, RegisterFile.SCI_REG_CP_0_CONFIG, handle)
    return err

def CPACK_CP_0_START(handle):
    err = __abstracted_reg_write(2, RegisterFile.SCI_REG_CP_0_CONFIG, handle)
    if (err != 0):
       return False
    err = __abstracted_reg_write(0, RegisterFile.SCI_REG_CP_0_CONFIG, handle)
    if (err != 0):
       return False
    err = __abstracted_reg_write(1, RegisterFile.SCI_REG_CP_0_CONFIG, handle)
    if (err != 0):
       return False
    return True

def CPACK_CP_0_GET_STATUS(handle):
    [err, status] = __abstracted_reg_read(RegisterFile.SCI_REG_CP_0_READ_STATUS, handle)
    status = status & 0xf
    return err, status

def CPACK_CP_0_GET_AVAILABLE_DATA(handle):
    [err, status] = __abstracted_reg_read(RegisterFile.SCI_REG_CP_0_READ_VALID_WORDS, handle)
    return err, status

def CPACK_CP_0_GET_DATA(n_packet, timeout_ms, handle):
    n_line = 16
    data_length = n_packet *( 2 + n_line)
    [err, data, read_data, valid_data] = __abstracted_fifo_read(data_length, RegisterFile.SCI_REG_CP_0_FIFOADDRESS, timeout_ms, handle)
    return err, data, read_data, valid_data

def set_registers(handle, config_file):

    print('set_registers:: Set up the registers in the DT5550')

    # read configuration from the config_file file
    if config_file == "":
        # not defined then read default....
        config_file = 'config.json'

    print('set_registers:: Configuration from: ',config_file)

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

    # set the base addresses for the i2c controller....
    SetAFEBaseAddress(handle)
    time.sleep(0.1)

    # set the correct termination of the analog inputs

    print('set_registers:: DT5550AFE:: Input Impedance =',reg['Termination'])
    termination = reg['Termination']
    if termination == TERMINATION_50OHM:
        SetAFEImpedance(TERMINATION_50OHM, handle)
    elif termination == TERMINATION_1MOHM:
        SetAFEImpedance(TERMINATION_1MOHM, handle)
    else:
        print('set_registers:: DT5550AFE:: ERROR Wrong termination chosen')
        return -1

    # set the DDC offsets

    # bottom row of DT5550AFE
    print('set_registers:: DT5550AFE:: DC offset =',V_offset,'V DAC = ',DAC_offset)

    SetAFEOffset(0, DAC_offset, handle)
    time.sleep(0.1)
    # top row of DT5550AFE
    SetAFEOffset(1, DAC_offset, handle)
    time.sleep(0.1)


    # set the Integration time
    print('set_registers:: Integration time =',reg['INTTIME']*CLK,' ns')
    REG_INTTIME_SET(reg['INTTIME'], handle)
    time.sleep(0.1)

    # set the pre-integration time
    print('set_registers:: Pre-integration time =',reg['PREINIT']*CLK,' ns')
    REG_PREINT_SET(reg['PREINIT'], handle)
    time.sleep(0.1)

    # set the baseline length: 2^n, where n is the value entered
    print('set_registers:: Baseline length =',reg['BLLEN'],' (see manual)')
    REG_BLLEN_SET(reg['BLLEN'], handle)
    time.sleep(0.1)

    # set the baseline hold time
    print('set_registers:: Baseline hold time =',reg['BLHOLD'],' (see manual)')
    REG_BLHOLD_SET(reg['BLHOLD'], handle)
    time.sleep(0.1)

    # set the event window lenggth
    print('set_registers:: Event window =',reg['WINDOW']*CLK,' (ns)')
    REG_WINDOW_SET(reg['WINDOW'], handle)
    time.sleep(0.1)

    # trigger mode: 0->single channel 1->two channels or more
    print('set_registers:: Tigger mode =',reg['TMODE'])
    REG_TMODE_SET(reg['TMODE'], handle)
    time.sleep(0.1)

    for idet in range(N_DETECTOR):
        det_id = data['detector_settings'][idet]['det_id']
        thrs = data['detector_settings'][idet]['THRS']
        invert = data['detector_settings'][idet]['INVERT']
        gain = data['detector_settings'][idet]['GAIN']

        # do we invert the AI or not
        print('set_registers::        id',det_id,' THRS =',thrs,' GAIN =',gain,' INVERT=',invert )

        REG_INVERT_SET(det_id, invert, handle)
        time.sleep(0.1)
        # set the detection threshold
        REG_THRS_SET(det_id, thrs, handle)
        time.sleep(0.1)

        # set the GAIN
        REG_GAIN_SET(det_id, gain, handle)
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