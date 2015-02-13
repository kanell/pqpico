# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 18:02:43 2015

@author: Malte Gerber
"""
###########------------Module----------------##############

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

########----------------Konstanten---------------############

V_max = 32768/50
R1 = 993000 # Ohm
R2 = 82400*1000000/(82400+1000000) # Ohm
Resolution = (R1+R2)/R2
f_line = 50 # Hz
Class  = 1

########------Initialisierung von globalen Listen-------##########

rms_list = []

#########---------------Funktionen-------------------########

def moving_average(a,n=15):
    ret = np.cumsum(a,dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return np.append(np.zeros(n/2),ret[n-1:]/n)

def Lowpass_Filter(data, SAMPLING_RATE):
    show_filtered_measurement = 1    
    roundoff_freq = 2000.0
    b_hp, a_hp = signal.butter(1, round(roundoff_freq / SAMPLING_RATE / 2,5))
    print('WP: '+str(round(roundoff_freq/SAMPLING_RATE/2)))
    #b_hp, a_hp = signal.butter(1, 0.001)
    print(str(b_hp))
    data_filtered = signal.lfilter(b_hp, a_hp, data)
    
    if (show_filtered_measurement):
        plt.plot(data, 'b') 
        plt.plot(data_filtered, 'r')
        plt.xlim(0, 100000)
        plt.grid(True)
        plt.show()
    return data_filtered
            
def calculate_Frequency(SAMPLING_RATE, data):        
    t = detect_zero_crossings(data, SAMPLING_RATE)
    freq_sample = (t[len(t)-1]-t[0])/(len(t)-1)*2
    measured_frequency = SAMPLING_RATE/freq_sample
            
    return measured_frequency, freq_sample
        
def detect_zero_crossings(data):
    #data_filtered = Lowpass_Filter(data, SAMPLING_RATE)    
    data_filtered = moving_average(data)
    pos = data_filtered > 0
    npos = ~pos
    zero_crossings = ((pos[:-1] & npos[1:]) | (npos[:-1] & pos[1:])).nonzero()[0]
    if False:
        plt.plot(data, 'b') 
        plt.plot(data_filtered, 'r')
        plt.xlim(0, 100000)
        plt.grid(True)
        plt.plot(zero_crossings,data[zero_crossings],'o')
        plt.show()
    return zero_crossings

def fast_fourier_transformation(data, SAMPLING_RATE):
    plot_FFT = 0    #Show FFT Signal Plot        
    #berechnen der Fouriertransformation        
    FFTdata = np.fft.fftshift(np.fft.fft(data))/len(data)     
    #Frequenzen der Oberschwingungen    
    FFTfrequencys = np.fft.fftfreq(len(FFTdata), 1.0/SAMPLING_RATE)
    #wegkürzen der neczgativen frequenzen und dafür verdoppeln der Amplituden
    FFTdata = np.abs(FFTdata[(len(FFTdata)/2):])*2
    
    if (plot_FFT):
        plt.plot(FFTfrequencys[:len(FFTdata)], FFTdata)
        plt.xlabel("f in Hz") # y-Achse beschriefen
        plt.ylabel("FFT") # x-Achse beschriften
        plt.xlim([0,1500]) # länge der angezeigten x-Achse
    
    return FFTdata, FFTfrequencys
        
def calculate_rms(data):
    #Der Effektivwert wird ueber alle Messpunkte gebildet             
    rms_points = np.sqrt(np.mean(np.power(data, 2)))
    rms = rms_points/V_max*Resolution
    rms_list.append(rms)
    return rms_list
    
def calculate_rms_half_period(data):
    #Der Effektivwert wird ueber alle Messpunkte gebildet             
    rms_points = np.sqrt(np.mean(np.power(data, 2)))
    rms_half_period = rms_points/V_max*Resolution
    if (rms_half_period <= (0.9*230) and rms_half_period >= (0.1*230)):
        print ("Es ist eine Unterspannung aufgetreten!")
        ###----hier wird statt der ausgabe ein flag gesetzt-----######
    elif rms_half_period < 0.1*230:
        print("Es liegt eine Spannungunterbrechung vor!")
        ###----hier wird statt der ausgabe ein flag gesetzt-----######
    elif rms_half_period > 1.1*230:
        print ("Es ist eine Überspannung aufgetreten!")
        ###----hier wird statt der ausgabe ein flag gesetzt-----######
    else:
        print("Alles OK!")
        ###----hier wird statt der ausgabe ein flag gesetzt-----######
    return rms_half_period
        
def calculate_harmonics_ClassA(data, SAMPLING_RATE):
    FFTdata, FFTfrequencys = fast_fourier_transformation(data, SAMPLING_RATE)        
    harmonics_amplitudes = np.array([])
    area_amplitudes = 10#round(len(data)/float(SAMPLING_RATE)*measured_frequency) #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden           
    for i in xrange(1,41): 
        #Berechnung der Harmonischen über eine for-Schleife        
        harmonics_amplitudes = np.append(harmonics_amplitudes, (np.sum(FFTdata[int(area_amplitudes*i-1):int(area_amplitudes*i+2)]**2))) #direkter Amplitudenwert aus FFT
    return harmonics_amplitudes
    
def calculate_harmonics_ClassS(data, SAMPLING_RATE):
    FFTdata, FFTfrequencys = fast_fourier_transformation(data, SAMPLING_RATE)        
    harmonics_amplitudes = np.array([])
    area_amplitudes = 10#len(data)/float(SAMPLING_RATE)*measured_frequency #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden 
    for i in xrange(1,41): 
        grouping_part1 = 0.5*FFTdata[int(round(area_amplitudes*i-area_amplitudes/2))]**2
        grouping_part2 = 0.5*FFTdata[int(round(area_amplitudes*i+area_amplitudes/2))]**2
        grouping_part3 = np.sum(FFTdata[int(round(area_amplitudes*i-area_amplitudes/2)+1):int(round(area_amplitudes*i+area_amplitudes/2))]**2)       
        harmonics_amplitudes = np.append(harmonics_amplitudes, (grouping_part1+grouping_part2+grouping_part3))
    return harmonics_amplitudes

def calculate_Pst(data):    
    show_time_signals = 0           #Aktivierung des Plots der Zeitsignale im Flickermeter
    show_filter_responses = 0       #Aktivierung des Plots der Amplitudengänge der Filter.
                                    #(zu Prüfzecken der internen Filter)
    
    fs = 4000    
       
    ## Block 1: Modulierung des Spannungssignals
    
    u = data - np.mean(data)                      # entfernt DC-Anteil
    u_rms = np.sqrt(np.mean(np.power(u,2))) # Normierung des Eingangssignals
    u = u / (u_rms * np.sqrt(2))
    
    ## Block 2: Quadratischer Demulator
    
    u_0 = u**2
    
    ## Block 3: Hochpass-, Tiefpass- und Gewichtungsfilter
    
    # Konfiguration der Filter
    HIGHPASS_ORDER  = 1 #Ordnungszahl der Hochpassfilters
    HIGHPASS_CUTOFF = 0.05 #Hz Grenzfrequenz
    
    LOWPASS_ORDER = 6 #Ordnungszahl des Tiefpassfilters
    if (f_line == 50):
      LOWPASS_CUTOFF = 35.0 #Hz Grenzfrequenz
    
    if (f_line == 60):
      LOWPASS_CUTOFF = 42.0 #Hz Grenzfrequenz
    
    # subtract DC component to limit filter transients at start of simulation
    u_0_ac = u_0 - np.mean(u_0)
    
    b_hp, a_hp = signal.butter(HIGHPASS_ORDER, (HIGHPASS_CUTOFF/(fs/2)), 'highpass')
    u_hp = signal.lfilter(b_hp, a_hp, u_0_ac)
    
    # smooth start of signal to avoid filter transient at start of simulation
    smooth_limit = min(round(fs / 10), len(u_hp))
    u_hp[ : smooth_limit] = u_hp[ : smooth_limit] * np.linspace(0, 1, smooth_limit)
    
    b_bw, a_bw = signal.butter(LOWPASS_ORDER, (LOWPASS_CUTOFF/(fs/2)), 'lowpass')
    u_bw = signal.lfilter(b_bw, a_bw, u_hp)
    
    # Gewichtungsfilter (Werte sind aus der Norm)
    
    if (f_line == 50):
      K = 1.74802
      LAMBDA = 2 * np.pi * 4.05981
      OMEGA1 = 2 * np.pi * 9.15494
      OMEGA2 = 2 * np.pi * 2.27979
      OMEGA3 = 2 * np.pi * 1.22535
      OMEGA4 = 2 * np.pi * 21.9
    
    if (f_line == 60):
      K = 1.6357
      LAMBDA = 2 * np.pi * 4.167375
      OMEGA1 = 2 * np.pi * 9.077169
      OMEGA2 = 2 * np.pi * 2.939902
      OMEGA3 = 2 * np.pi * 1.394468
      OMEGA4 = 2 * np.pi * 17.31512
    
    num1 = [K * OMEGA1, 0]
    denum1 = [1, 2 * LAMBDA, OMEGA1**2]
    num2 = [1 / OMEGA2, 1]
    denum2 = [1 / (OMEGA3 * OMEGA4), 1 / OMEGA3 + 1 / OMEGA4, 1]
    
    b_w, a_w = signal.bilinear(np.convolve(num1, num2), np.convolve(denum1, denum2), fs)
    u_w = signal.lfilter(b_w, a_w, u_bw)
    
    ## Block 4: Quadrierung und Varianzschätzer
    
    LOWPASS_2_ORDER  = 1
    LOWPASS_2_CUTOFF = 1 / (2 * np.pi * 300e-3)  # Zeitkonstante 300 msek.
    SCALING_FACTOR   = 1238400  # Skalierung des Signals auf eine Wahrnehmbarkeitsskala
    
    u_q = u_w**2
    
    b_lp, a_lp = signal.butter(LOWPASS_2_ORDER, (LOWPASS_2_CUTOFF/(fs/2)), 'low')
    s = SCALING_FACTOR * signal.lfilter(b_lp, a_lp, u_q)
    
    ## Block 5: Statistische Berechnung
    
    p_50s = np.mean([np.percentile(s, 100-30, interpolation="linear"),
                     np.percentile(s, 100-50, interpolation="linear"),
                     np.percentile(s, 100-80, interpolation="linear")])
    p_10s = np.mean([np.percentile(s, 100-6, interpolation="linear"),
                     np.percentile(s, 100-8, interpolation="linear"), 
                     np.percentile(s, 100-10, interpolation="linear"),
                     np.percentile(s, 100-13, interpolation="linear"),
                     np.percentile(s, 100-17, interpolation="linear")])
    p_3s = np.mean([np.percentile(s, 100-2.2, interpolation="linear"),
                    np.percentile(s, 100-3, interpolation="linear"),
                    np.percentile(s, 100-4, interpolation="linear")])
    p_1s = np.mean([np.percentile(s, 100-0.7, interpolation="linear"),
                    np.percentile(s, 100-1, interpolation="linear"),
                    np.percentile(s, 100-1.5, interpolation="linear")])
    p_0_1s = np.percentile(s, 100-0.1, interpolation="linear")
    
    P_st = np.sqrt(0.0314*p_0_1s+0.0525*p_1s+0.0657*p_3s+0.28*p_10s+0.08*p_50s)
    
    if (show_time_signals):
        t = np.linspace(0, len(u) / fs, num=len(u))
        plt.figure()
        plt.clf()
        #plt.subplot(2, 2, 1)
        plt.hold(True)
        plt.plot(t, u, 'b', label="u")
        plt.plot(t, u_0, 'm', label="u_0")
        plt.plot(t, u_hp, 'r', label="u_hp")
        plt.xlim(0, len(u)/fs)
        plt.hold(False)
        plt.legend(loc=1)
        plt.grid(True)
        #plt.subplot(2, 2, 2)
        plt.figure()
        plt.clf()    
        plt.hold(True)
        plt.plot(t, u_bw, 'b', label="u_bw")
        plt.plot(t, u_w, 'm', label="u_w")
        plt.xlim(0, len(u)/fs)
        plt.legend(loc=1)
        plt.hold(False)
        plt.grid(True)
        #plt.subplot(2, 2, 3)
        plt.figure()
        plt.clf()    
        plt.plot(t, u_q, 'b', label="u_q")
        plt.xlim(0, len(u)/fs)
        plt.legend(loc=1)
        plt.grid(True)
        #plt.subplot(2, 2, 4)
        plt.figure()
        plt.clf()    
        plt.plot(t, s, 'b', label="s")
        plt.xlim(0, len(u)/fs)
        plt.legend(loc=1)
        plt.grid(True)
    
    if (show_filter_responses):
        f, h_hp = signal.freqz(b_hp, a_hp, 4096)
        f, h_bw = signal.freqz(b_bw, a_bw, 4096)
        f, h_w = signal.freqz(b_w, a_w, 4096)
        f, h_lp = signal.freqz(b_lp, a_lp, 4096)
        f = f/np.pi*fs/2    
        
        plt.figure()
        plt.clf()
        plt.hold(True)
        plt.plot(f, abs(h_hp), 'b', label="Hochpass 1. Ordnung")
        plt.plot(f, abs(h_bw), 'r', label="Butterworth Tiefpass 6.Ordnung")
        plt.plot(f, abs(h_w), 'g', label="Gewichtungsfilter")
        plt.plot(f, abs(h_lp), 'm', label="Varianzschätzer")
        plt.legend(bbox_to_anchor=(1., 1.), loc=2)    
        plt.hold(False)
        plt.grid(True)
        plt.axis([0, 35, 0, 1])
        
    return P_st 
        
def count_up_values(values_list):
    new_value = np.sqrt(np.sum(np.power(values_list,2), axis=0)/len(values_list))
    return new_value
    
def convert_data_to_lower_fs(data, SAMPLING_RATE):
    step = int(SAMPLING_RATE/4000)
    delta = np.arange(0,len(data),step)
    data_flicker =data[delta]
    return data_flicker
    
def calculate_unbalance(rms_10min_u, rms_10min_v, rms_10min_w):
    a = -0.5+0.5j*np.sqrt(3)
    u1 =1.0/3*(rms_10min_u+rms_10min_v+rms_10min_w)
    u2 = 1.0/3 *(rms_10min_u+a*rms_10min_v+a**2*rms_10min_w)
    return np.abs(u2)/np.abs(u1)*100

def calculate_THD(data, SAMPLING_RATE):
    if (Class == 1):
        harmonics_amplitudes = calculate_harmonics_ClassA(data, SAMPLING_RATE)
    elif (Class == 0):
        harmonics_amplitudes = calculate_harmonics_ClassS(data, SAMPLING_RATE)
    else:
        None
    THD = np.sqrt(np.sum(harmonics_amplitudes[1:])/harmonics_amplitudes[0])*100
    return THD
    
def calculate_Plt(Pst_list):
    P_lt = np.power(np.power(Pst_list,3)/12,1/3)
    return P_lt

def test_harmonics(data, SAMPLING_RATE):
    if (Class == 1):
        harmonics_amplitudes = calculate_harmonics_ClassA(data, SAMPLING_RATE)
    elif (Class == 0):
        harmonics_amplitudes = calculate_harmonics_ClassS(data, SAMPLING_RATE)
    else:
        None
    
    return 0