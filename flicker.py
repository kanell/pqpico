# -*- coding: utf-8 -*-
"""
Created on Mon Nov 17 09:36:56 2014

@author: Malte Gerber
"""
import time
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import scipy.io as sio
import scipy.io as io
import analysingMeasurement as ana



"""
##############################################################################
Berechung des Kurzzeitflickerwertes über eine Zeitspanne von 10min.

Pst = flicker(u, f_line, fs)

Inputs:
    u:          Spannungsverlauf
    f_line:     Netzfrequenz (50Hz od. 60Hz)
    fs:         Abtastrate

Output:
    Pst:        Kurzzeitflicker
##############################################################################
"""
time1 = time.time()

show_time_signals = 0           #Aktivierung des Plots der Zeitsignale im Flickermeter
show_filter_responses = 0       #Aktivierung des Plots der Amplitudengänge der Filter.
                                #(zu Prüfzecken der internen Filter)
f_line = 50
fs = 4000

def calculate_Pst():    
    u = np.load('testwerte1.npy')
    #u = ana.example_sin_wave(2400000, 4000)
    
    ## Block 1: Modulierung des Spannungssignals
    
    u = u - np.mean(u)                      # entfernt DC-Anteil
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
      LOWPASS_CUTOFF = 35 #Hz Grenzfrequenz
    
    if (f_line == 60):
      LOWPASS_CUTOFF = 42 #Hz Grenzfrequenz
    
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
    
    
    #time2 = time.time()
    #print("Benötigte Zeit in Sekunden = " + str(time2-time1))
    
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