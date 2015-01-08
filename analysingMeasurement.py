# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 10:05:32 2014

Analysing the measurement:

@author: Malte Gerber
"""

import numpy as np
import matplotlib.pyplot as plt
import glob
import scipy.signal as signal


SAMPLEPOINTS = 220000   #Samplepoints
SAMPLING_RATE = 1000000  #Sampling Rate
Un = 230 #Volt

    
def load_measurepoints(SAMPLEPOINTS):
    #Load files from the directory        
    npyfiles = glob.glob('C:\\Users\Malte Gerber\Desktop\Messdaten\*.npy')
    measurepoints = np.load(npyfiles[20])
    #add the content from all files to one list
    i = 20
    while len(measurepoints) < SAMPLEPOINTS:
        #Messdaten werden solange in ein Array geladen, bis es mehr als die vorgegebene Samplepoints sind        
        measurepoints = np.concatenate([measurepoints, (np.load(npyfiles[i]))], axis=0) 
        i = i+1
    #Messdaten werden genau auf die vorgegebenen Samplepoints gebracht
    measurepoints = measurepoints[:SAMPLEPOINTS]
    return measurepoints
    
def fast_fourier_transformation(SAMPLEPOINTS, SAMPLING_RATE):
    
    plot_FFT = 0    #Show FFT Signal Plot    
    
    #Laden der Messwerte    
    measurepoints = load_measurepoints(SAMPLEPOINTS)
    #berechnen der Fouriertransformation        
    FFTmeasurepoints = np.fft.fftshift(np.fft.fft(measurepoints))/SAMPLEPOINTS 
    #Frequenzen der Oberschwingungen    
    FFTfrequency = np.fft.fftfreq(len(FFTmeasurepoints), 1.0/SAMPLING_RATE)
    #wegkürzen der negativen frequenzen und dafür verdoppeln der Amplituden
    FFTmeasurepoints = np.abs(FFTmeasurepoints[(len(FFTmeasurepoints)/2):])*2
    
    if (plot_FFT):
        deltaT = 1.0/(SAMPLING_RATE)   #s ->Zeit von einem Messpunkt zum nächsten
        fMax = 1.0/deltaT   #Hz -> Maximale Frequenz der Fourieranalyse
        fAxis = np.linspace(0,fMax/2,SAMPLEPOINTS/2) #x-Achse von 0 bis nyquist-frequenz=fmax/2 mit SAMPLEPOINTS/2 Datenpunkten
        plt.plot(fAxis,FFTmeasurepoints) #Plot der Messwerte der FFT über die gegebene x-Achse fMax
        plt.xlabel("f in Hz") # y-Achse beschriefen
        plt.ylabel("FFT") # x-Achse beschriften
        plt.xlim([0,1500]) # länge der angezeigten x-Achse
    
    return FFTmeasurepoints, FFTfrequency  
    
def calculate_rms():
    #Laden der Messwerte
    measurepoints = load_measurepoints(SAMPLEPOINTS)
    #Der Effektivwert wird ueber alle Messpunkte gebildet    
    rms = np.sqrt(np.mean(np.power(np.float32(measurepoints), 2)))
    return rms

def example_sin_wave(SAMPLEPOINTS, SAMPLING_RATE):  #Beispiel für Sinusschwingungen mit Oberschwingungen
    Tn = 0.02 #ms Frequenz der sinusspannung
    t = np.linspace(0.0,1.0*SAMPLEPOINTS/SAMPLING_RATE,num=SAMPLEPOINTS) #Zeitachse der Sinusschwingung als Samplepoints mit bestimmter Samplerate
    measurepoints = 230*np.sqrt(2)*np.sin(2*np.pi/Tn*t)+2*np.sqrt(2)*np.sin(2*np.pi/Tn*3*t)+5*np.sqrt(2)*np.sin(2*np.pi/Tn*5*t)+6*np.sqrt(2)*np.sin(2*np.pi/Tn*7*t)+4*np.sqrt(2)*np.sin(2*np.pi/Tn*9*t)+2*np.sqrt(2)*np.sin(2*np.pi/Tn*11*t) #Array mit Messwerten
    return measurepoints
    
def THD(SAMPLEPOINTS, SAMPLING_RATE):
    #Lade Messpunkte der FFT
    FFTmeasurepoints = fast_fourier_transformation(SAMPLEPOINTS, SAMPLING_RATE)[0]
    THD = 0 #Startwert der THD
    for i in range(2,41): 
        Bereich_Amplituden = round(SAMPLEPOINTS/float(SAMPLING_RATE)/0.02*i) #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden           
        THD_Amplituden = FFTmeasurepoints[Bereich_Amplituden] #direkter Amplitudenwert aus FFT   
    #Berechnung des THD-Wertes über eine for-Schleife        
        THD_Amplituden = np.power((THD_Amplituden),2)  
        THD = THD + THD_Amplituden
    THD = np.sqrt(THD/(FFTmeasurepoints[SAMPLEPOINTS/float(SAMPLING_RATE)/0.02]**2)) #darf nicht größer als 8% betragen
    return THD

def Oberschwingungen_Gruppierung(SAMPLEPOINTS, SAMPLING_RATE):
    #Lade Messpunkte der FFT   
    FFTmeasurepoints = fast_fourier_transformation(SAMPLEPOINTS, SAMPLING_RATE)
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

def calculate_Frequency(SAMPLING_RATE):    
    measurepoints_filtered = Hamming_Filter()    
    
    t = []       
    for i in range(len(measurepoints_filtered)-1):
        if (measurepoints_filtered[i]<=0 and measurepoints_filtered[i+1]>0):           
            t.append(i - measurepoints_filtered[i]/(measurepoints_filtered[i+1]-measurepoints_filtered[i]))
    freqency_samplepoints = (t[len(t)-1]-t[0])/(len(t)-1)
    freqency_seconds = SAMPLING_RATE/freqency_samplepoints

#    
#    FFTmeasurepoints = fast_fourier_transformation(SAMPLEPOINTS)[0]
#    for index, item in enumerate(FFTmeasurepoints):
#        if (item==max(FFTmeasurepoints)):    
#            print("Frequenz = " + str(index))
            
    return freqency_seconds
    
def Hamming_Filter():
    
    show_filtered_measurement = 0    
        
    #Lade Messwerte
    #measurepoints = load_measurepoints(SAMPLEPOINTS)
    measurepoints = example_sin_wave(SAMPLEPOINTS, SAMPLING_RATE)    
    #Filterkern wird erstellt als Rechteck-Funktion mit 30 Stützstellen und einem cutoff von 0.008    
    kern = signal.firwin(5, cutoff = 0.008, window = "hamming")
    
    #Messdaten werden gefiltert
    measurepoints_filtered = signal.lfilter(kern, 1, measurepoints)
    
    if (show_filtered_measurement):
        plt.plot(measurepoints, 'b') 
        plt.plot(measurepoints_filtered, 'r')
        plt.xlim(0, 40000)    
        #plt.axis([19920, 19950, -100, 100])
    
    return measurepoints_filtered
    
if __name__ == '__main__':
    try:
        
        #THD is calculated
        THD = THD(SAMPLEPOINTS, SAMPLING_RATE)
        print("THD = " + str(THD))
#        THD_Gruppierung = Oberschwingungen_Gruppierung(SAMPLEPOINTS, SAMPLING_RATE)
#        print("THD_Gruppierung = " + str(THD_Gruppierung))
        
        #rms voltage is calculated
#        rms = calculate_rms()
#        print("Effektivwert = " + str(rms))
        
        #freqency is calculated
        freqency = calculate_Frequency(SAMPLING_RATE)
        print("Frequenz = " + str(freqency))
        

    except:
        print("there must be something wrong")
    
    finally:
        print("the analysis has been completed")
