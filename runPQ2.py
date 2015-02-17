import Picoscope4000
import PQTools2 as pq
import numpy as np
import time
import sys
import matplotlib.pyplot as plt
from ring_array import ring_array

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
                time.sleep(0.1)
    
        #data_chunk = data[:min_snippet_length]

        # remove DC component mathmatically, works better than switchung Picoscope to AC coupling

        #data_chunk -= np.mean(data_chunk)

        zero_indices = pq.detect_zero_crossings(data.get_data_view())

        #print('data_chunk: '+str(data_chunk))
        print('zero_indices: '+str(zero_indices))
        print(np.diff(zero_indices))   
        #if False:
            #plt.plot(np.diff(zero_indices), 'b') 
            #plt.grid(True)
            #plt.show()
        #np.save('/home/kipfer/pqpico/Data/data_chunk',data_chunk) 
        #print(len(data_chunk))

        data_10periods = data.cut_off_front(zero_indices[20]-1)
        #data_10seconds = np.append(data_10seconds, data_10periods) #Preallocation?

        print('Length of data_10periods : '+str(data_10periods.size))

        #data = np.array([1,2,3,4,5])
        #data = data[zero_indices[20]:zero_indices[20]+10]
        #shift_zeros = zero_indices - zero_indices[0]

        #for i in xrange(20):    
            #rms_half_period = pq.calculate_rms_half_period(data_10periods[shift_zeros[i]:shift_zeros[i+1]])

        print(np.mean(data_10periods))
        data_10periods -= np.mean(data_10periods)
    
        for i in xrange(20):    
            rms_half_period[i] = pq.calculate_rms_half_period(data_10periods[zero_indices[i]:zero_indices[i+1]])

        print('RMSs: '+str(rms_half_period))

        plt.plot(rms_half_period)
        plt.grid(True)
        plt.show()

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
            

        break

finally:
    pico.close_unit()


#def print memoryusage(variable:
#prin
