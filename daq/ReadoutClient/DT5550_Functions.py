import RegisterFile

from ctypes import *

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
    triggermode = c_int(0)
    triggermode = (OscilloscopeTriggerChannel << 8)  + (SoftwareTrigger << 7 ) + (Edge << 3) + (SoftwareTrigger << 1) + AnalogTrigger +(Digital0Trigger << 2) + (Digital1Trigger << 2) + Digital1Trigger + (Digital2Trigger << 2) + (Digital2Trigger << 1) + (Digital3Trigger << 2) + (Digital3Trigger << 1) + Digital3Trigger
    triggermode = 0x00
    err = __abstracted_reg_write(triggermode, RegisterFile.SCI_REG_Oscilloscope_0_CONFIG_TRIGGER_MODE, handle)
    return err

def OSCILLOSCOPE_Oscilloscope_0_GET_STATUS(handle):
    [err, status] = __abstracted_reg_read(RegisterFile.SCI_REG_Oscilloscope_0_READ_STATUS, handle)
    return err, status

def OSCILLOSCOPE_Oscilloscope_0_GET_POSITION(handle):
    [err, position] = __abstracted_reg_read(RegisterFile.SCI_REG_Oscilloscope_0_READ_POSITION, handle)
    return err, position

def OSCILLOSCOPE_Oscilloscope_0_GET_DATA(timeout_ms, handle):
    [err, data, read_data, valid_data] = __abstracted_mem_read(8192, RegisterFile.SCI_REG_Oscilloscope_0_FIFOADDRESS, timeout_ms, handle)
    return err, data, read_data, valid_data

def OSCILLOSCOPE_Oscilloscope_0_RECONSTRUCT_DATA(OscilloscopeData, OscilloscopePosition, OscilloscopePreTrigger):
    OscilloscopeChannels = 8
    OscilloscopeSamples = 1024
    Analog = list(range(OscilloscopeSamples*OscilloscopeChannels))
    Digital0 = list(range(OscilloscopeSamples*OscilloscopeChannels))
    Digital1 = list(range(OscilloscopeSamples*OscilloscopeChannels))
    Digital2 = list(range(OscilloscopeSamples*OscilloscopeChannels))
    Digital3 = list(range(OscilloscopeSamples*OscilloscopeChannels))
    for n in range(OscilloscopeChannels):
        current = OscilloscopePosition - OscilloscopePreTrigger
        print('current =',current)
        if ((current) > 0):
            k = 0
            for i in range(current, OscilloscopeSamples-1):
                Analog[k+ OscilloscopeSamples * n] = OscilloscopeData[i+ OscilloscopeSamples * n] & 65535
                print(n,i,k,'data =',Analog[k+ OscilloscopeSamples * n])
                Digital0[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 16 & 1)
                Digital1[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 17 & 1)
                Digital2[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 18 & 1)
                Digital3[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 19 & 1)
                k = k + 1
            for i in range(0, current-1):

                Analog[k+ OscilloscopeSamples * n] = OscilloscopeData[i+ OscilloscopeSamples * n] & 65535
                print(n,i,k,'data =',Analog[k+ OscilloscopeSamples * n])

                Digital0[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 16 & 1)
                Digital1[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 17 & 1)
                Digital2[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 18 & 1)
                Digital3[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 19 & 1)
                k = k + 1
        else:
            k = 0
            for i in range(OscilloscopeSamples+current, OscilloscopeSamples-1):
                Analog[k+ OscilloscopeSamples * n] = OscilloscopeData[i+ OscilloscopeSamples * n] & 65535
                Digital0[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 16 & 1)
                Digital1[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 17 & 1)
                Digital2[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 18 & 1)
                Digital3[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 19 & 1)
                print(n,i,k,'data =',Analog[k+ OscilloscopeSamples * n])

                k = k + 1
            for i in range(0, OscilloscopeSamples+current-1):
                Analog[k+ OscilloscopeSamples * n] = OscilloscopeData[i+ OscilloscopeSamples * n] & 65535
                Digital0[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 16 & 1)
                Digital1[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 17 & 1)
                Digital2[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 18 & 1)
                Digital3[k+ OscilloscopeSamples * n] = (OscilloscopeData[i+ OscilloscopeSamples * n] >> 19 & 1)
                print(n,i,k,'data =',Analog[k+ OscilloscopeSamples * n])

                k = k + 1
    return Analog, Digital0, Digital1,Digital2, Digital3

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


def CPACK_CP_0_RECONSTRUCT_DATA(FrameData):
    in_sync = 0
    tot_data = len(FrameData)
    n_ch =24
    n_packet = tot_data / (n_ch + 3)
    event_energy, Time_Code, Pack_Id, Energy = ([] for i in range(4))
    for i in range(len(FrameData)):
        mpe = FrameData[i]
        if (in_sync == 0):
            if (mpe != 0xffffffff):
                continue
            in_sync = 1
            continue
        if (in_sync == 1):
            event_timecode = mpe 
            Time_Code.append(event_timecode)
            in_sync = 2
            continue
        if (in_sync == 2):
            Pack_Id.append(mpe)
            in_sync = 3
            ch_index = 0
            continue
        if (in_sync == 3):
            if (mpe == 0xffffffff):
                in_sync = 1
            else:
                ev_energy = mpe
                event_energy.append(ev_energy)
                ch_index += 1
                if (ch_index == n_ch):
                    Energy.append(event_energy)
                    event_energy = []
                    in_sync = 0
    return Time_Code, Pack_Id, Energy

