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


SAMPLEPOINTS = 2**22 #Samplepoints


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
    return measurepoints
    
def fast_fourier_transformation(measurepoints,SAMPLEPOINTS):
    #berechnen der Fouriertransformation        
    FFTmeasurepoints = np.fft.fftshift(np.fft.fft(measurepoints))/SAMPLEPOINTS 
    #wegkürzen der negativen frequenzen und dafür verdoppeln der Amplituden
    FFTmeasurepoints = np.absolute(FFTmeasurepoints[len(FFTmeasurepoints)/2.0:]*2.0)   
    return FFTmeasurepoints  
    
def calculate_rms(measurepoints):
    rms = np.sqrt(np.mean(np.power(np.int32(measurepoints), 2)))
    return rms

def example_sin_wave(SAMPLEPOINTS):
    Tn = 0.02 #ms Frequenz der sinusspannung
    t = np.linspace(0.0,0.2,num=SAMPLEPOINTS) #Zeit für 10 Perioden
    measurepoints = 230*np.sqrt(2)*np.sin(2*np.pi/Tn*t)
    return measurepoints
    
def plt_definition_sin_wave(FFTmeasurepoints, SAMPLEPOINTS):
    fs = 327680.0     #Samples/s Abtastrate        
    deltaT = 1/fs   #s ->Zeit von einem Messpunkt zum nächsten
    fMax = 1/deltaT   #Hz -> Maximale Frequenz der Fourieranalyse
    fAxis = np.linspace(0,fMax/2,SAMPLEPOINTS/2)
    plt.plot(fAxis,FFTmeasurepoints)
    plt.xlabel("f in Hz")
    plt.ylabel("FFT")
    plt.xlim([0,2000])


if __name__ == '__main__':
    try:
        #Fourier Analysis:    
        measurement = load_measurepoints(SAMPLEPOINTS)
        measurement = measurement[:SAMPLEPOINTS]
        
        #example for the fourier analysis
        #measurement = example_sin_wave(SAMPLEPOINTS)    

        #FFT: Measured data are given in FFT-equation        
        FFTmeasurepoints = fast_fourier_transformation(measurement, SAMPLEPOINTS)
        
        #Data for plot mit beispielwerten werten
        #plt_definition_sin_wave(measurement, SAMPLEPOINTS)
        
        #Data for plot mit echten werten
        deltaT = 0.002      #ms
        fMax = 1.0/deltaT   #KHz
        fAxis = np.linspace(0,fMax/2,SAMPLEPOINTS/2)
        plt.plot(fAxis,FFTmeasurepoints)
        plt.xlabel("f in kHz")
        plt.ylabel("FFT")
        plt.xlim([min(fAxis),max(fAxis)])
        plt.xlim([0,1.25])
        
        
        #THD is calculated
        
        THD = 0 #Startwert der THD
        for i in range(2,40): #ist bisher falsch
            freqency_guess = 10
            THD_Amplituden = np.max(FFTmeasurepoints[(freqency_guess*i-5):(freqency_guess*i+5)])    #max. amplitude nehmen im Bereich der harmonischen Schwingungen (muss noch angepasst werden)           
            THD_Amplituden = np.power(THD_Amplituden/(230*np.sqrt(2)),2)  #4000 just an example -> 4000 must be replaced with Un
            THD = THD + THD_Amplituden  #darf nicht größer als 8% betragen
        
        print("THD = " + str(THD))
        
        #rms voltage is calculated
        rms = calculate_rms(measurement)
        print("Effektivwert = " + str(rms))
        #freqency is calculated
        
#        for i in xrange(SAMPLEPOINTSPYLESAMPLEPOINTSGTH):
#            if measurepoints[i]<0 & measurepoints[i+1]>0 & measurepoints[i+1]<measurepoints[i+2]:
#                period_counter = 1                
#                period_begin = i + np.abs(measurepoints[i])/(measurepoints[i+1] + np.abs(measurepoints[i]))           
#                period_counter += 1
#                print(period_begin)
#                
#            else:
#                print("neuer durchlauf")
            

    except:
        print("there must be something wrong")
    
    finally:
        print("the analysis has been completed")
