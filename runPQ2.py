import Picoscope4000
import PQTools as pq
import numpy as np
import time
import sys
import matplotlib.pyplot as plt

pico = Picoscope4000.Picoscope4000()
pico.run_streaming()

parameters = pico.get_parameters()
streaming_sample_interval = parameters['streaming_sample_interval']

min_snippet_length = streaming_sample_interval/2

data = np.array(np.zeros(10000000))
data_10periods = np.array([np.zeros(10000000)])
data_10seconds = np.array([])

is_first_iteration = 1
#tstart = time.time()
try:
    while True:
        while data.size < min_snippet_length or True:

            if is_first_iteration:
                # detect the very first zero crossing:
                snippet = pico.get_queue_data()
                if snippet is not None:
                   data = np.append(data,snippet)
                   first_zero_crossing = np.nonzero(np.sign(data) == -1 * np.sign(data[0]))[0][0]-1
                   print('Value before start: '+str(data[first_zero_crossing-1])+', First value: '+str(data[first_zero_crossing]))
                   data = data[first_zero_crossing:]
                   is_first_iteration = 0

            # Get data snippet from Queue
            snippet = pico.get_queue_data()
            if snippet is not None:
                #data = np.append(data,snippet)
                print('Length of recorded snippet: '+str(len(snippet)))
            else:
                pass
                #print(str(snippet))
            time.sleep(0.1)



        
        #data_chunk = data[:min_snippet_length]

        # remove DC component mathmatically, works better than switchung Picoscope to AC coupling

        #data_chunk -= np.mean(data_chunk)
        
        #zero_indices = pq.detect_zero_crossings(data,parameters['streaming_sample_interval'])

        #print('data_chunk: '+str(data_chunk))
        #print('zero_indices: '+str(zero_indices))
        #print(np.diff(zero_indices))   
        #if False:
            #plt.plot(np.diff(zero_indices), 'b') 
            #plt.grid(True)
            #plt.show()
        #np.save('/home/kipfer/pqpico/Data/data_chunk',data_chunk) 
        #print(len(data_chunk))

        #data_10periods = data[:zero_indices[20]-1]
        #data_10seconds = np.append(data_10seconds, data_10periods) #Preallocation?

        #print('Length of data_10seconds : '+str(data_10seconds.size))

        #data = np.array([1,2,3,4,5])
        #data = data[zero_indices[20]:zero_indices[20]+10]
        #shift_zeros = zero_indices - zero_indices[0]

        #for i in xrange(20):    
            #rms_half_period = pq.calculate_rms_half_period(data_10periods[shift_zeros[i]:shift_zeros[i+1]])

        #rms_10_periods = pq.calculate_rms(data_10periods)

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
            

finally:
    pico.close_unit()


#def print memoryusage(variable:
    #prin
