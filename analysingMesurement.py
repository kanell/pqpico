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
import math

NPYLENGTH = 500000
N = 2**16 #Samplepoints

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
        #must be modified for more measurepoints -> brauch bei vielen Messwerten aber zu lange   

        #example for the fourier analysis
             
#        Tn = 0.02 #ms Frequenz der sinusspannung
#        t = np.linspace(0.0,0.2,num=N) #Zeit für 10 Perioden
#        measurepoints = 230*np.sqrt(2)*np.sin(2*np.pi/Tn*t)
     
        #FFT: Measured data are given in FFT-equation        
        FFTmeasurepoints = np.fft.fftshift(np.fft.fft(measurepoints))/N     #berechnen der Fouriertransformation 
        FFTmeasurepoints = np.absolute(FFTmeasurepoints[len(FFTmeasurepoints)/2.0:]*2.0)    #wegkürzen der negativen frequenzen und dafür verdoppeln der Amplituden
              
        
        #Data for plot mit beispielwerten werten
#        fs = 327680.0     #Samples/s Abtastrate        
#        deltaT = 1/fs   #s ->Zeit von einem Messpunkt zum nächsten
#        fMax = 1/deltaT   #Hz -> Maximale Frequenz der Fourieranalyse
#        fAxis = np.linspace(0,fMax/2,N/2)
#        plt.plot(fAxis,FFTmeasurepoints)
#        plt.xlabel("f in Hz")
#        plt.ylabel("FFT")
#        plt.xlim([0,2000])
        
        
        #Data for plot mit echten werten
        deltaT = 0.002      #ms
        fMax = 1.0/deltaT   #KHz
        fAxis = np.linspace(0,fMax/2,N/2.0)
        plt.plot(fAxis,FFTmeasurepoints)
        plt.xlabel("f in kHz")
        plt.ylabel("FFT")
        plt.xlim([min(fAxis),max(fAxis)])
        plt.xlim([0,1.25])

        #THD is calculated
       
        THD = 0 #Startwert der THD
        for i in range(2,40):
            freqency_guess = 10
            THD_Amplituden = np.max(FFTmeasurepoints[(freqency_guess*i-5):(freqency_guess*i+5)])    #max. amplitude nehmen im Bereich der harmonischen Schwingungen (muss noch angepasst werden)           
            THD_Amplituden = np.power(THD_Amplituden/(230*np.sqrt(2)),2)  #4000 just an example -> 4000 must be replaced with Un
            THD = THD + THD_Amplituden  #darf nicht größer als 8% betragen
        
        print("THD = " + str(THD))
        
        #rms voltage is calculated

        time1 = time.time()
        rms = 0.0   #Startwert des rms
        for i in range(N): #Effektivwert über N Messwerte
            rms = measurepoints[i]**2+rms
         
        rms = np.sqrt(rms/N) 
        time2 = time.time()
        print("rms = " + str(rms)) #braucht für viele messwerte exponetiell länger
        
#        rms2 = np.absolute(measurepoints)
#        rms2 = np.power(measurepoints,2)
#        
#        rms2 = math.fsum(rms2)
#        
#        rms2 = np.sqrt(rms2/N)
#        time3 = time.time()
#        print("rms2 = " + str(rms2))
#        print("Time_for = " + str(time2-time1))
#        print("Time_sum = " + str(time3-time2))
    
        #freqency is calculated
        
        
    
    #except:
        print("there must be something wrong")
    
    finally:
        print("the analysis has been completed")
