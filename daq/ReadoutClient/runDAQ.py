import sys
import getopt
import os
from datetime import datetime

PYTHON = "C:\ProgramData\Anaconda3\python"
#-----------------------------------------------------------------------------------------------------------------------
def main(argv):
    """
    MAIN CODE
    """

    os.chdir('../ReadOutClient/')

    n_event_per_file = 100000
    config_file = ""
    outdir = "C:/data/"
    save_waveform = False

    try:
        opts, args = getopt.getopt(argv, "hn:o:c:iw", ["nevent=", "outdir=", "cfile=", "init=", "wform="])
    except getopt.GetoptError:
        print('runDAQ.py -n <number of events> -o <outdir> -c <configfile> -w')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('runDAQ.py -n <number of events> -o <outdir> -c <configfile> -w')
            sys.exit(2)
        elif opt in ("-o", "--outdir"):
            outdir = arg
        elif opt in ("-c", "--cfile"):
            config_file = arg
        elif opt in ("-n", "--nevent"):
            n_event = int(arg)
        elif opt in ("-w", "--wform"):
            save_waveform = True

    if config_file == "":
        return -1

    #
    # make smaller runs. will save the events in multiple files
    #
    nrun = int((n_event-1) / n_event_per_file) + 1

    # initialize daq
    date_tag = datetime.today().strftime('%Y%m%d_%H%M%S')
    #
    # create output directory
    #
    if outdir == "":
        outdir = r"C:\data/"
    outdir = outdir + date_tag
    cmd = 'mkdir "'+outdir+'"'
    print('Create output directory:', cmd)
    os.system(cmd)
    outdir = outdir + '/'

    #
    # copy configuration file to the output directory
    #
    tmp = config_file.split('.')
    print(tmp)
    cmd = 'copy '+config_file+r' "'+outdir+'config_'+date_tag+'.json'+r' "'
    print('Copy config file to output directory::', cmd)
    os.system(cmd)

    #
    # run the DAQ.....
    #
    for irun in range(nrun):
        # make the DAQ run command
        n_proc = n_event_per_file
        if int(n_event/((irun+1)*n_event_per_file)) == 0:
            n_proc = n_event % n_event_per_file

        output_file = outdir + "/data_" +date_tag + "_" + str(irun) + ".raw"
        cmd = PYTHON+" DT5550_Readout.py -n "+str(n_proc)+" -c "+config_file+" -o " + output_file + " -m data"
        if irun > 0:
            cmd = cmd + " -i"
        # run the DAQ
        print(cmd)
        os.system(cmd)

        if save_waveform:
            output_file = outdir + "/waveform_" +date_tag + "_" + str(irun) + ".raw"
            cmd = PYTHON+" DT5550_Readout.py -n 25  -c " + config_file + " -o " + output_file + " -i -m osc"
            print(cmd)
            os.system(cmd)

    print("Exit runDAQ")
#-----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main(sys.argv[1:])