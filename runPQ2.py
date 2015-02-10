import Picoscope4000
import PQTools as pq
import numpy as np

pico = Picoscope4000()
pico.run_streaming()

parameters = pico.get_parameters()


min_snippet_length = parameters['streaming_sample_interval']/2

data = np.array([])

while True:
    while data.size < min_snippet_length:
        # Get data snippet from Queue

        snippet = pico.get_queue_data()
        if snippet is not None:
            data = np.append(data,snippet)

    data_chunk = data[:min_snippet_length]
    zero_indeces = pq.detect_zero_crossings(data_chunk,parameters['streaming_sample_interval'])
    data_10periods = data[zero_indeces[0]:zero_indeces[20]]
    data = data[zero_indeces[20]+1:]
    shift_zeros = zero_indeces - zero_indeces[0]
    for i in xrange(20):    
        rms_half_period = pq.calculate_rms_half_period(data_10periods[shift_zeros[i]:shift_zeros[i+1]])
    rms_10_periods = pq.calculate_rms(data_10periods)
    harmonics = pq.calculate_harmonics_ClassA(data_10periods, parameters['streaming_sample_interval'])
    
    

