from DT5550_Functions import *
from ctypes import *
import sys
import numpy as np

INIT_REGISTERS = 0


from array import array
def main(argv):

    # initialize daq
    handle = initialize_daq()
    # set the registers on the DAQ
    if INIT_REGISTERS:
        set_registers(handle, config_file)

    Oscilloscope_Status = 0
    Timeout_ms = 1000
    Decimator = 0
    Pre_Trigger = 500
    Trigger_Level = 56000
    Trigger_Channel = 0
    Trigger_Mode = "Analog" #"Free", "Analog", "Digital0", "Digital1", "Digital2", "Digital3"
    Trigger_Edge = "Rising" #"Rising", "Falling"

    nevent = 5

    ievent = 0
    fout = open('waveform.output','wb')
    while(ievent < nevent):
        if (OSCILLOSCOPE_Oscilloscope_0_SET_DECIMATOR(Decimator, handle) != 0):
            print("Set Decimator Error")
            exit
        if (OSCILLOSCOPE_Oscilloscope_0_SET_PRETRIGGER(Pre_Trigger, handle) != 0):
            print("Set PreTrigger Error")
            exit
        if (OSCILLOSCOPE_Oscilloscope_0_SET_TRIGGER_LEVEL(Trigger_Level, handle) != 0):
            print("Set Trigger Level Error")
            exit
        if (OSCILLOSCOPE_Oscilloscope_0_SET_TRIGGER_MODE(Trigger_Mode, Trigger_Channel, Trigger_Edge, handle) != 0):
            print("Set Trigger Mode Error")
            exit
        if (OSCILLOSCOPE_Oscilloscope_0_START(handle) == True):
            while (Oscilloscope_Status != 1):
                [err, Oscilloscope_Status] = OSCILLOSCOPE_Oscilloscope_0_GET_STATUS(handle)
            [err, Event_Position] = OSCILLOSCOPE_Oscilloscope_0_GET_POSITION(handle)
            [err, Oscilloscope_Data, Oscilloscope_Read_Data, Oscilloscope_Valid_Data] = OSCILLOSCOPE_Oscilloscope_0_GET_DATA(Timeout_ms, handle)
            print(Oscilloscope_Data, Oscilloscope_Read_Data, Oscilloscope_Valid_Data)
            print('position event = ',Event_Position)

            #for i in range(len(Oscilloscope_Data)):
            #    print(i,Oscilloscope_Data[i])
            Analog = OSCILLOSCOPE_Oscilloscope_0_RECONSTRUCT_DATA(Oscilloscope_Data, Event_Position, Pre_Trigger)
            np.array(Analog).tofile(fout)


            #plt.cla()
            #plt.plot(Analog)
            #plt.show()

            #plt.pause(0.01)

            print(ievent)
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