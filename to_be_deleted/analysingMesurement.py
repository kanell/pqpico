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
import mpmath
import math


SAMPLEPOINTS = 100000   #Samplepoints
SAMPLING_RATE = 500000  #Sampling Rate


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
    #wegkürzen der negativen frequenzen und dafür verdoppeln der Amplituden
    FFTmeasurepoints = np.abs(FFTmeasurepoints[(len(FFTmeasurepoints)/2):])*2
    return FFTmeasurepoints  
    
def calculate_rms(measurepoints):
    rms = np.sqrt(np.mean(np.power(np.int32(measurepoints), 2)))
    return rms

def example_sin_wave(SAMPLEPOINTS, SAMPLING_RATE):
    Tn = 0.02 #ms Frequenz der sinusspannung
    t = np.linspace(0.0,1.0*SAMPLEPOINTS/SAMPLING_RATE,num=SAMPLEPOINTS)
    measurepoints = 230*np.sqrt(2)*np.sin(2*np.pi/Tn*t)   
    return measurepoints
    
def plt_definition_FFT(FFTmeasurepoints, SAMPLEPOINTS, SAMPLING_RATE):
    deltaT = 1.0/(SAMPLING_RATE/1000)   #ms ->Zeit von einem Messpunkt zum nächsten
    fMax = 1.0/deltaT   #kHz -> Maximale Frequenz der Fourieranalyse
    fAxis = np.linspace(0,fMax/2,SAMPLEPOINTS/2)
    plt.plot(fAxis,FFTmeasurepoints)
    plt.xlabel("f in kHz")
    plt.ylabel("FFT")
    plt.xlim([min(fAxis),max(fAxis)])
    plt.xlim([0,1.5])

def THD(SAMPLEPOINTS, SAMPLING_RATE, FFTmeasurepoints):
    THD = 0 #Startwert der THD
    for i in range(2,41): 
        Bereich_Amplituden = SAMPLEPOINTS/float(SAMPLING_RATE)/0.02*i #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden           
        THD_Amplituden = FFTmeasurepoints[Bereich_Amplituden]    
        THD_Amplituden = np.power((THD_Amplituden),2)  #1300 just an example -> 1300 must be replaced with rms 
        THD = THD + THD_Amplituden
    THD = np.sqrt(THD/np.power(1300,2)) #darf nicht größer als 8% betragen
    return THD

def THD_Gruppierung(SAMPLEPOINTS, SAMPLING_RATE, FFTmeasurepoints):
    THD_Gruppierung = 0
    for i in range(2,41): 
        Bereich_Amplituden = SAMPLEPOINTS/float(SAMPLING_RATE)/0.02*i #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden           
        THD_Gruppierung_teil1 = 0.5*FFTmeasurepoints[Bereich_Amplituden-(SAMPLEPOINTS/float(SAMPLING_RATE)/0.02)/2]**2
        THD_Gruppierung_teil2 = 0.5*FFTmeasurepoints[Bereich_Amplituden+(SAMPLEPOINTS/float(SAMPLING_RATE)/0.02)/2]**2
        FFTmeasurepoints_Bereich = FFTmeasurepoints[(Bereich_Amplituden-(SAMPLEPOINTS/float(SAMPLING_RATE)/0.02)/2+1):(Bereich_Amplituden+(SAMPLEPOINTS/float(SAMPLING_RATE)/0.02)/2)]**2       
        THD_Gruppierung_teil3 = np.sum(FFTmeasurepoints_Bereich)
        THD_Gruppierung = THD_Gruppierung_teil1+THD_Gruppierung_teil2+THD_Gruppierung_teil3+THD_Gruppierung
    THD_Gruppierung = np.sqrt(THD_Gruppierung/np.power(1300,2))    
    return THD_Gruppierung
    
if __name__ == '__main__':
    try:
        #Fourier Analysis:    
        measurement = load_measurepoints(SAMPLEPOINTS)

        #example for the fourier analysis
        #measurement = example_sin_wave(SAMPLEPOINTS, SAMPLING_RATE)    

        #FFT: Measured data are given in FFT-equation        
        FFTmeasurepoints = fast_fourier_transformation(measurement, SAMPLEPOINTS)
       
        #Data for plot mit beispielwerten werten
        plt_definition_FFT(FFTmeasurepoints, SAMPLEPOINTS, SAMPLING_RATE)
        
        #THD is calculated
        THD = THD(SAMPLEPOINTS, SAMPLING_RATE, FFTmeasurepoints)
        print("THD = " + str(THD))
        THD_Gruppierung = THD_Gruppierung(SAMPLEPOINTS, SAMPLING_RATE, FFTmeasurepoints)
        print("THD_Gruppierung = " + str(THD_Gruppierung))
        
        #rms voltage is calculated
        rms = calculate_rms(measurement)
        print("Effektivwert = " + str(rms))
        
        #freqency is calculated
        
            

    except:
        print("there must be something wrong")
    
    finally:
        print("the analysis has been completed")
