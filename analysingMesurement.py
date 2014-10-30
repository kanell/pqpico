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

NPYLENGTH = 5000000
N = 2**22 #Samplepoints

#def FFT_output(measurepoints):
#    FFTmeasurepoints = np.fft.fftshift(np.fft.fft(measurepoints))
#    return FFTmeasurepoints

if __name__ == '__main__':
    try:
        #Fourier Analysis:
        npyfiles = glob.glob('C:\Users\Malte Gerber\Desktop\PQdata\*.npy')
        measurepoints = np.load(npyfiles[0])

        i = 0
        while len(measurepoints) < NPYLENGTH:
            measurepoints = np.concatenate([measurepoints, (np.load(npyfiles[i]))], axis=0) 
            i = i+1
        measurepoints = measurepoints[:N]
        #must be modified for more measurepoints   

        #example for the fourier analysis
        #N=500000        
        #Tn = 0.02 #ms
        #t = np.linspace(0.0,1.0,num=N) 
        #measurepoints = np.sin(2*np.pi/Tn*t)
        
        #FFT: Measured data are given in FFT-equation        
        FFTmeasurepoints = np.fft.fftshift(np.fft.fft(measurepoints))/N
        FFTmeasurepoints = FFTmeasurepoints[len(FFTmeasurepoints)/2.0:]*2.0
        
        
        #Data for plot
        deltaT = 0.002      #ms
        fMax = 1.0/deltaT   #Hz
        fAxis = np.linspace(0,fMax/2,N/2.0)
        deltaF =1.0/(deltaT*N)
        #fNyquist =0.5/deltaT
        #plt.plot(measurepoints[:10000])
        plt.plot(fAxis,np.abs(FFTmeasurepoints))
        plt.plot(0.05, max(np.abs(FFTmeasurepoints)),'ro',label="1. harmonic vibration -> my guess!!" )
        plt.xlabel("f in kHz")
        plt.ylabel("FFT")
        #plt.xlim([min(fAxis),max(fAxis)])
        plt.xlim([0,1.25])        

    except:
        print("there must be something wrong")
    
    finally:
        print("the analysis has been completed")
