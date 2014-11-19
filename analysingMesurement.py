# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 10:05:32 2014

Analysing the measurement:

@author: Malte Gerber
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import Picoscope2000, Picoscope4000
import time
import scipy.signal as signal
import math


SAMPLEPOINTS = 2**16   #Samplepoints
SAMPLING_RATE = 327680  #Sampling Rate

#SAMPLING_RATE = 500000

#class Measurement:
    
def load_measurepoints(SAMPLEPOINTS):
    #Load files from the directory        
    npyfiles = glob.glob('C:\Users\Malte Gerber\Desktop\PQdata\*.npy')
    measurepoints = np.load(npyfiles[0])
    #add the content from all files to one list
    i = 0
    while len(measurepoints) < SAMPLEPOINTS:
        measurepoints = np.concatenate([measurepoints, (np.load(npyfiles[i]))], axis=0) 
        i = i+1
    measurepoints = measurepoints[:SAMPLEPOINTS]
    return measurepoints
    
def fast_fourier_transformation(measurepoints,SAMPLEPOINTS):
    #berechnen der Fouriertransformation        
    FFTmeasurepoints = np.fft.fftshift(np.fft.fft(measurepoints))/SAMPLEPOINTS 
    #Frequenzen der Oberschwingungen    
    FFTfrequency = np.fft.fftfreq(len(FFTmeasurepoints), 1.0/SAMPLING_RATE)
    #wegkürzen der negativen frequenzen und dafür verdoppeln der Amplituden
    FFTmeasurepoints = np.abs(FFTmeasurepoints[(len(FFTmeasurepoints)/2):])*2
    return FFTmeasurepoints, FFTfrequency  
    
def calculate_rms(measurepoints):
    rms = np.sqrt(np.mean(np.power(np.int32(measurepoints), 2)))
    return rms

def example_sin_wave(SAMPLEPOINTS, SAMPLING_RATE):
    Tn = 0.02 #ms Frequenz der sinusspannung
    t = np.linspace(0.0,1.0*SAMPLEPOINTS/SAMPLING_RATE,num=SAMPLEPOINTS)
    measurepoints = 230*np.sqrt(2)*np.sin(2*np.pi/Tn*t)+23*np.sqrt(2)*np.sin(2*np.pi/Tn*3*t)+2.3*np.sqrt(2)*np.sin(2*np.pi/Tn*5*t) 
    return measurepoints
    
def plt_definition_FFT(FFTmeasurepoints, SAMPLEPOINTS, SAMPLING_RATE):
    deltaT = 1.0/(SAMPLING_RATE)   #s ->Zeit von einem Messpunkt zum nächsten
    fMax = 1.0/deltaT   #Hz -> Maximale Frequenz der Fourieranalyse
    fAxis = np.linspace(0,fMax/2,SAMPLEPOINTS/2) #x-Achse von 0 bis nyquist-frequenz=fmax/2 mit SAMPLEPOINTS/2 Datenpunkten
    plt.plot(fAxis,FFTmeasurepoints) 
    plt.xlabel("f in Hz") # y-Achse beschriefen
    plt.ylabel("FFT") # x-Achse beschriften
    plt.xlim([0,1500]) # länge der x-Achse
    

def THD(SAMPLEPOINTS, SAMPLING_RATE, FFTmeasurepoints):
    THD = 0 #Startwert der THD
    for i in range(2,41): 
        Bereich_Amplituden = SAMPLEPOINTS/float(SAMPLING_RATE)/0.02*i #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden           
        THD_Amplituden = FFTmeasurepoints[Bereich_Amplituden]    
        THD_Amplituden = np.power((THD_Amplituden),2)  
        THD = THD + THD_Amplituden
    THD = np.sqrt(THD/(FFTmeasurepoints[SAMPLEPOINTS/float(SAMPLING_RATE)/0.02]**2)) #darf nicht größer als 8% betragen
    return THD

def Oberschwingungen_Gruppierung(SAMPLEPOINTS, SAMPLING_RATE, FFTmeasurepoints):
    Gruppierung = 0
    for i in range(1,41): 
        Bereich_Amplituden = SAMPLEPOINTS/float(SAMPLING_RATE)/0.02*i #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden           
        Gruppierung_teil1 = 0.5*FFTmeasurepoints[Bereich_Amplituden-(SAMPLEPOINTS/float(SAMPLING_RATE)/0.02)/2]**2
        Gruppierung_teil2 = 0.5*FFTmeasurepoints[Bereich_Amplituden+(SAMPLEPOINTS/float(SAMPLING_RATE)/0.02)/2]**2
        FFTmeasurepoints_Bereich = FFTmeasurepoints[(Bereich_Amplituden-(SAMPLEPOINTS/float(SAMPLING_RATE)/0.02)/2+1):(Bereich_Amplituden+(SAMPLEPOINTS/float(SAMPLING_RATE)/0.02)/2)]**2       
        Gruppierung_teil3 = np.sum(FFTmeasurepoints_Bereich)
        Gruppierung = Gruppierung_teil1+Gruppierung_teil2+Gruppierung_teil3+Gruppierung
        if (i==1):
            erste_Oberschwingung = Gruppierung
            Gruppierung = 0
    THD_Gruppierung = np.sqrt(Gruppierung/erste_Oberschwingung)
    return THD_Gruppierung

def Frequency(measurepoints_filtered, SAMPLING_RATE):
    t = []       
    for i in xrange(len(measurepoints_filtered)-1):
        if (measurepoints_filtered[i]<=0 and measurepoints_filtered[i+1]>=0):
            t.append(i - measurepoints_filtered[i]/(measurepoints_filtered[i+1]-measurepoints_filtered[i]))
    freqency_samplepoints = (t[len(t)-1]-t[1])/(len(t)-2)
    freqency_seconds = SAMPLING_RATE/freqency_samplepoints
    return freqency_seconds
    
def Rectangular_Filter(measurepoints):
    kern = signal.firwin(30, cutoff = 0.008, window = "rectangular")
    measurepoints_filtered = signal.lfilter(kern, 1, measurepoints)
    return measurepoints_filtered
    
if __name__ == '__main__':
    try:
        #Fourier Analysis:    
        #measurement = load_measurepoints(SAMPLEPOINTS)

        #example for the fourier analysis
        measurement = example_sin_wave(SAMPLEPOINTS, SAMPLING_RATE)    

        #FFT: Measured data are given in FFT-equation        
        FFTmeasurepoints, FFTfrequency = fast_fourier_transformation(measurement, SAMPLEPOINTS)
        
        #Data for plot mit beispielwerten werten
        plt_definition_FFT(FFTmeasurepoints, SAMPLEPOINTS, SAMPLING_RATE)
        
        #THD is calculated
        THD = THD(SAMPLEPOINTS, SAMPLING_RATE, FFTmeasurepoints)
        print("THD = " + str(THD))
        THD_Gruppierung = Oberschwingungen_Gruppierung(SAMPLEPOINTS, SAMPLING_RATE, FFTmeasurepoints)
        print("THD_Gruppierung = " + str(THD_Gruppierung))
        
        #rms voltage is calculated
        rms = calculate_rms(measurement)
        print("Effektivwert = " + str(rms))
        
        #freqency is calculated
        measurepoints_filtered = Rectangular_Filter(measurement)        
        freqency = Frequency(measurepoints_filtered, SAMPLING_RATE)
        print("Frequenz = " + str(freqency))

    except:
        print("there must be something wrong")
    
    finally:
        print("the analysis has been completed")
