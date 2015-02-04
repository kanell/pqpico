import Picoscope4000
import PQTools as pq

pico = Picoscope4000()
pico.run_streaming()

parameters = pico.get_parameters()

min_snippet_length = parameters.streaming_sample_interval/2

data = np.array()

while True:
    while data.size < min_snippet_length:
        # Get data snippet from Queue

        snippet = pico.get_queue_data()
        if snippet is not None:
            data = np.append(data,snippet)

    data_chunk = data[:min_snippet_length]
    zero_indeces = pq.detect_zero_crossings(data_chunk,parameters.streaming_sample_interval)
    data_10periods = data(zero_indeces[10]
    

