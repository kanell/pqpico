import Picoscope4000
import PQTools2 as pq
import numpy as np
import time
import sys
import matplotlib.pyplot as plt
from ring_array import ring_array
import logging

PLOTTING = 0

pico = Picoscope4000.Picoscope4000()
pico.run_streaming()

parameters = pico.get_parameters()
streaming_sample_interval = parameters['streaming_sample_interval']

min_snippet_length = streaming_sample_interval/2

data = ring_array(size=10000000)
#data_10periods = np.array([np.zeros(10000000)])

data_10seconds = ring_array(size=20000000) 

rms_half_period = np.array(np.zeros(20))

is_first_iteration = 1
#tstart = time.time()
#time.sleep(0.5) # Activate when first data is None and first iterations runs with None data, should be fixed

# Initialize Logging
# ==================

queueLogger = logging.getLogger('queueLogger')
queueLogger.setLevel(logging.DEBUG)

fhq = logging.FileHandler('Logs/queueLog.log')
fhq.setLevel(logging.DEBUG)

shq = logging.StreamHandler()
shq.setLevel(logging.INFO)

formatterq = logging.Formatter('%(asctime)s \t %(levelname)s \t %(message)s')
fhq.setFormatter(formatterq)
shq.setFormatter(formatterq)

queueLogger.addHandler(fhq)
queueLogger.addHandler(shq)

dataLogger = logging.getLogger('dataLogger')
dataLogger.setLevel(logging.DEBUG)

fhd = logging.FileHandler('Logs/dataLog.log')
fhd.setLevel(logging.DEBUG)

shd = logging.StreamHandler()
shd.setLevel(logging.INFO)

formatterd = logging.Formatter('%(asctime)s \t %(levelname)s \t %(message)s')
fhd.setFormatter(formatterd)
shd.setFormatter(formatterd)

dataLogger.addHandler(fhd)
dataLogger.addHandler(shd)

try:
    while True:
        while data.size < min_snippet_length:

            snippet = pico.get_queue_data()

            if is_first_iteration:
                # Detect the very first zero crossing:
                if snippet is not None:
                    data.attach_to_back(snippet)
                    data_10seconds.attach_to_back(snippet)

                    queueLogger.debug('Length of snippet:      +'+str(snippet.size))
                    queueLogger.debug('Length of current data: '+str(data.size))

                    # Cut off everything before the first zero crossing:
                    first_zero_crossing = np.nonzero(np.sign(data.get_data_view()) == -1 * np.sign(data.get_index(0)))[0][0]-1
                    queueLogger.debug('Cut off '+str(first_zero_crossing)+' values before first zero crossing') 
                    data.cut_off_front(first_zero_crossing)
                    data_10seconds.cut_off_front(first_zero_crossing)
                    is_first_iteration = 0

            else:
                # Get data snippet from Queue
                if snippet is not None:
                    data.attach_to_back(snippet)
                    data_10seconds.attach_to_back(snippet)

                    queueLogger.debug('Length of snippet:      +'+str(snippet.size))
                    queueLogger.debug('Length of current data: '+str(data.size))
                else:
                    pass
    
        
        # Find 10 periods
        # ===============
        zero_indices = pq.detect_zero_crossings(data.get_data_view())
        dataLogger.debug('Cutting off :'+str(zero_indices[20]-1))
        queueLogger.debug('Cutting off:            -'+str(zero_indices[20]-1))
        data_10periods = data.cut_off_front(zero_indices[20]-1)

 
        # Calculate and store frequency for ten periods
        # =============================================
        frequency_10periods = pq.calculate_frequency_10periods(zero_indices, streaming_sample_interval)
        dataLogger.debug('Frequency of 10 periods: '+str(frequency_10periods))
        if PLOTTING:
            plt.plot(np.diff(zero_indices), 'b') 
            plt.grid(True)
            plt.show()
        dataLogger.debug('Mean value of 10 periods: '+str(np.mean(data_10periods)))
    
     
        # Calculate and store RMS values of half periods 
        # ==============================================
        for i in xrange(20):    
            rms_half_period[i] = pq.calculate_rms_half_period(data_10periods[zero_indices[i]:zero_indices[i+1]])
        if PLOTTING:
            plt.plot(rms_half_period)
            plt.grid(True)
            plt.show()


        # Calculate and store RMS values of 10 periods
        # ============================================
        rms_10periods = pq.calculate_rms(data_10periods)
        dataLogger.debug('RMS voltage of 10 periods: '+str(rms_10periods))


        # Calculate frequency of 10 seconds
        # =================================
        if (data_10seconds.size > 10*streaming_sample_interval):
            frequency_data = data_10seconds.cut_off_front(10*streaming_sample_interval)
            plt.plot(frequency_data)
            plt.grid()
            plt.show()
            frequency = pq.calculate_Frequency(streaming_sample_interval,frequency_data)
            dataLogger.info('Frequency10s: '+str(frequency))
            break



        #harmonics = pq.calculate_harmonics_ClassA(data_10periods, parameters['streaming_sample_interval'])

        #if data_10seconds.size >= streaming_sample_interval*1:
            #freq_data = data_10seconds[:streaming_sample_interval*1]
            #data_10seconds = data_10seconds[streaming_sample_interval*+1:]
        #if time.time() - tstart > 10 or False:
            #print('data_10seconds: '+str(data_10seconds.size)+' using '+str(data_10seconds.nbytes/1000000.0)+' MB')
            #print('data_10periods: '+str(data_10periods.size)+' using '+str(data_10periods.nbytes/1000000.0)+' MB')
            #print('freq_data: '+str(freq_data.size)+' using '+str(freq_data.nbytes/1000000.0)+' MB')
            #print('shift_zeros: '+str(shift_zeros.size)+' using '+str(shift_zeros.nbytes/1000000.0)+' MB')
            #print('rms_10_periods: '+str(rms_10_periods.size)+' using '+str(rms_10_periods.nbytes/1000000.0)+' MB')
            #break
            

        #break

finally:
    pico.close_unit()

    # Error Handling: Save and log all variables
    # ==========================================




#def print memoryusage(variable:
#prin
