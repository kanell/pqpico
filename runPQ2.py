import Picoscope4000
import PQTools3 as pq
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

streaming_sample_interval = parameters['streaming_sample_interval']

min_snippet_length = streaming_sample_interval/2

data = ring_array(size=10000000)
data_10seconds = ring_array(size=20000000) 
data_10min = ring_array(size=20000000)
rms_half_period = np.array(np.zeros(20))

first_value = 0
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
                # ====================================
                if snippet is not None:
                    data.attach_to_back(snippet)
                    data_10seconds.attach_to_back(snippet)

                    queueLogger.debug('Length of snippet:      +'+str(snippet.size))
                    queueLogger.debug('Length of current data: '+str(data.size))

                    # Cut off everything before the first zero crossing:
                    # ==================================================
                    first_zero_crossing = np.nonzero(np.sign(data.get_data_view()) == -1 * np.sign(data.get_index(0)))[0][0]-1
                    queueLogger.debug('Cut off '+str(first_zero_crossing)+' values before first zero crossing') 
                    data.cut_off_front(first_zero_crossing)
                    data_10seconds.cut_off_front(first_zero_crossing)
                    is_first_iteration = 0

            else:
                # Get data snippet from Queue:
                # ============================
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
        if zero_indices.size < 15 or zero_indices.size > 200:
            dataLogger.error('Number of zero crossings in '+str(data.get_data_view().size)+': '+str(zero_indices.size))
        dataLogger.debug('Cutting off :'+str(zero_indices[20]-1))
        queueLogger.debug('Cutting off:            -'+str(zero_indices[20]-1))
        data_10periods = data.cut_off_front(zero_indices[20]-1)
        
        # Calculate and store frequency for 10 periods
        # =============================================
        frequency_10periods = pq.calculate_frequency_10periods(zero_indices, streaming_sample_interval)
        dataLogger.debug('Frequency of 10 periods: '+str(frequency_10periods))
        if PLOTTING:
            plt.plot(np.diff(zero_indices), 'b') 
            plt.title('Difference between zero crossings')
            plt.grid(True)
            plt.show()
        dataLogger.debug('Mean value of 10 periods: '+str(np.mean(data_10periods)))
    
     
        # Calculate and store RMS values of half periods 
        # ==============================================
        for i in xrange(20):    
            rms_half_period[i] = pq.calculate_rms_half_period(data_10periods[zero_indices[i]:zero_indices[i+1]])
        if PLOTTING:
            plt.plot(rms_half_period)
            plt.title(' Voltage RMS of Half Periods')
            plt.grid(True)
            plt.show()

        # Calculate and store RMS values of 10 periods
        # ============================================
        rms_10periods = pq.calculate_rms(data_10periods)
        dataLogger.debug('RMS voltage of 10 periods: '+str(rms_10periods))

        # Calculate and store harmonics and THD values of 10 periods
        # ==========================================================
        harmonics_10periods = pq.calculate_harmonics_voltage(data_10periods,streaming_sample_interval)
        thd_10periods = pq.calculate_THD(harmonics_10periods, streaming_sample_interval)
        dataLogger.debug('THD of 10 periods: '+str(thd_10periods))
        
        # Calculate frequency of 10 seconds
        # =================================
        if (data_10seconds.size > 10*streaming_sample_interval):
            frequency_data = data_10seconds.cut_off_front(10*streaming_sample_interval)
            #pq.compare_filter_for_zero_crossings(frequency_data, streaming_sample_interval)
            if PLOTTING:
                plt.plot(frequency_data)
                plt.grid()
                plt.show()
            frequency = pq.calculate_Frequency(streaming_sample_interval,frequency_data)
            dataLogger.info('Frequency of 10s: '+str(frequency))
            pico.put_queue_data()
        
        # Prepare data for Flicker calculation
        # ====================================
            data_for_10min = pq.convert_data_to_lower_fs(frequency_data, streaming_sample_interval, first_value)       
            data_10min.attach_to_back(data_for_10min)
        
        # Calculate flicker of 10 min
        # ===========================
        if (data_10min.size > 600*streaming_sample_interval/250):
            flicker_data = data_10min.cut_off_front(600*streaming_sample_interval/250)
            Pst = pq.calculate_Pst(flicker_data)
            dataLogger.info('Pst: '+str(Pst))
            break

finally:
    pico.close_unit()

    # Error Handling: Save and log all variables
    # ==========================================
