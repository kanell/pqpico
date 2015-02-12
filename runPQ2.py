import Picoscope4000
import PQTools as pq
import numpy as np
import time
import matplotlib.pyplot as plt

pico = Picoscope4000.Picoscope4000()
pico.run_streaming()

parameters = pico.get_parameters()

min_snippet_length = parameters['streaming_sample_interval']/2

data = np.array([])
is_first_iteration = 1

try:
    while True:
        while data.size < min_snippet_length:
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
                data = np.append(data,snippet)
                print('Length of recorded snippet: '+str(len(snippet)))
            else:
                print(str(snippet))
            time.sleep(0.1)

        data_chunk = data[:min_snippet_length]
        zero_indices = pq.detect_zero_crossings(data_chunk ,parameters['streaming_sample_interval'])
        print('data_chunk: '+str(data_chunk))
        print('zero_inices: '+str(zero_indices))
        print(np.diff(zero_indices))   
        plt.plot(np.diff(zero_indices), 'b') 
        plt.grid(True)
        plt.show()
        #data_10periods = data(zero_indices[10])
        #np.save('/home/kipfer/pqpico/Data/data_chunk',data_chunk) 
        print(len(data_chunk))

finally:
    pico.close_unit()
