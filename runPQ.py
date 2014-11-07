import Picoscope 4000
import threading

def prepareMeasurement():
    pico = Picoscope4000()
    pico.setchannel()


def readMeasurements():
    pico.run_streaming()


def calcRMS():
    pass

    # Read numpy data from disk
    
    # split and recombine into correct frames

    # calculate rms and append to rms data (on disk?)

    # maybe plot data (hmtl?)


def calcTHD():
    pass


def calcFrequency():
    pass


prepareMeasurement()

# MAIN LOOP

while True:
    
    # Create and start thread for reading measurements from Picoscope and writing them to disk
    thread_readMeasurements = threading.Thread(target=readMeasurements)
    threads.append(thread_readMeasurements)
    thread_readMeasurements.start()

    # Create and start thread for calculating RMS
    thread_calcRMS = threading.Thread(target=calcRMS)
    threads.append(thread_calcRMS)
    thread_calcRMS.start()

    thread_calcTHD = threading.Thread(target=calcTHD)
    threads.append(thread_calcTHD)
    thread_calcTHD.start()

    thread_calcFrequency = threading.Thread(target=calcFrequency)
    threads.append(thread_calcFrequency)
    thread_calcFrequency.start()



