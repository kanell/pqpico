# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 10:05:32 2014

Analysing the measurement:

@author: Malte Gerber
"""

import numpy as np
import matplotlib.pyplot as plt


#Fourier Analysis:

measurepoints = np.load("C:\Users\Malte Gerber\Desktop\PQdata\CH1_20141021_18_47_27_945307.npy")
measurepoints = measurepoints[:500000]
#must be modified for more measurepoints

#example for the fourier analysis
N = 500000
deltaT = 0.002 #ms
FFTmeasurepoints = np.fft.fftshift(np.fft.fft(measurepoints))
fMax = 1.0/deltaT
fAxis = np.linspace(-fMax/2,fMax/2,N)
deltaF =1.0/(deltaT*N)

fNyquist =0.5/deltaT
print(np.abs(FFTmeasurepoints))
plt.plot(fAxis,np.abs(FFTmeasurepoints))
#plt.plot(frequency1, max(np.abs(FFTmeasurepoints)),'ro',label="my guess!" )
#plt.plot(frequency2, max(np.abs(FFTmeasurepoints)),'r+',label="my guess!" )
plt.plot(fNyquist, max(np.abs(FFTmeasurepoints)),'go',label="Nyquist frequency" )
plt.xlabel("f in kHz")
plt.ylabel("FFT")
plt.xlim([min(fAxis),max(fAxis)])
