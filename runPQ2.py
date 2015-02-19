import Picoscope4000
import PQTools2 as pq
import numpy as np
import time
import sys
import matplotlib.pyplot as plt
from ring_array import ring_array

PLOTTING = 0

pico = Picoscope4000.Picoscope4000()
pico.run_streaming()

parameters = pico.get_parameters()
streaming_sample_interval = parameters['streaming_sample_interval']

min_snippet_length = streaming_sample_interval/2

data = ring_array()
data_10periods = np.array([np.zeros(10000000)])
data_10seconds = np.array([])

rms_half_period = np.array(np.zeros(20))

is_first_iteration = 1
#tstart = time.time()
#time.sleep(0.5) # Activate when first data is None and first iterations runs with None data, should be fixed

try:
    while True:
        while data.size < min_snippet_length:

            if is_first_iteration:
                # detect the very first zero crossing:
                snippet = pico.get_queue_data()
                if snippet is not None:
                    print('Snippet is '+str(snippet))
                    data.attach_to_back(snippet)
                    print('data: '+str(data.get_data_view()))
                    print('data[0]: '+str(data.get_index(0)))
                    first_zero_crossing = np.nonzero(np.sign(data.get_data_view()) == -1 * np.sign(data.get_index(0)))[0][0]-1
                    print('first_zero_crossing: '+str(first_zero_crossing))
                    print('Value before start: '+str(data.get_index(first_zero_crossing-1))+', First value: '+str(data.get_index(first_zero_crossing)))
                    data.cut_off_front(first_zero_crossing)
                    print('data: '+str(data.get_data_view()))
                    is_first_iteration = 0

            else:
                # Get data snippet from Queue
                snippet = pico.get_queue_data()
                if snippet is not None:
                    data.attach_to_back(snippet)
                    print('Length of recorded snippet: '+str(len(snippet)))
                else:
                    pass
                    #print(str(snippet))
    
        
        # Find 10 periods
        # ===============
        zero_indices = pq.detect_zero_crossings(data.get_data_view())
        data_10periods = data.cut_off_front(zero_indices[20]-1)

 
        # Calculate and store frequency for ten periods
        # =============================================
        frequency_10periods = pq.calculate_frequency_10periods(zero_indices, streaming_sample_interval)
        print(str(frequency_10periods))
        print('zero_indices: '+str(zero_indices))
        print(np.diff(zero_indices))   
        if PLOTTING:
            plt.plot(np.diff(zero_indices), 'b') 
            plt.grid(True)
            plt.show()
        print('Length of data_10periods : '+str(data_10periods.size))
        print(np.mean(data_10periods))
        #data_10periods -= np.mean(data_10periods)
    
     
        # Calculate and store RMS values of half periods 
        # ==============================================
        for i in xrange(20):    
            rms_half_period[i] = pq.calculate_rms_half_period(data_10periods[zero_indices[i]:zero_indices[i+1]])
        print('RMSs: '+str(rms_half_period))
        if PLOTTING:
            plt.plot(rms_half_period)
            plt.grid(True)
            plt.show()


        # Calculate and store RMS values of 10 seconds
        # ============================================
        rms_10_periods = pq.calculate_rms(data_10periods)
        print('RMS: '+str(rms_10_periods))

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


#def print memoryusage(variable:
#prin
