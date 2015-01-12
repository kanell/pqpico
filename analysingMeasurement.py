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
import time
import flicker as fl

SAMPLEPOINTS = 2**18#220000   #Samplepoints
SAMPLING_RATE = 1000000  #Sampling Rate
Un = 230 #Volt

    
def load_measurepoints(SAMPLEPOINTS):
    #Load files from the directory        
    npyfiles = glob.glob('C:\\Users\Malte Gerber\Desktop\Messdaten\*.npy')
    measurepoints = np.load(npyfiles[0])
    #add the content from all files to one list
    i = 0
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
              
    #FFTphase = np.angle(FFTmeasurepoints)    
    #Frequenzen der Oberschwingungen    
    FFTfrequencys = np.fft.fftfreq(len(FFTmeasurepoints), 1.0/SAMPLING_RATE)
    #wegkürzen der negativen frequenzen und dafür verdoppeln der Amplituden
    FFTmeasurepoints = np.abs(FFTmeasurepoints[(len(FFTmeasurepoints)/2):])*2
    
    if (plot_FFT):
        #deltaT = 1.0/(SAMPLING_RATE)   #s ->Zeit von einem Messpunkt zum nächsten
        #fMax = 1.0/deltaT   #Hz -> Maximale Frequenz der Fourieranalyse
        #fAxis = np.linspace(0,fMax/2,SAMPLEPOINTS/2) #x-Achse von 0 bis nyquist-frequenz=fmax/2 mit SAMPLEPOINTS/2 Datenpunkten
        plt.plot(FFTfrequencys[:SAMPLEPOINTS/2], FFTmeasurepoints) #Plot der Messwerte der FFT über die gegebene x-Achse fMax
        plt.xlabel("f in Hz") # y-Achse beschriefen
        plt.ylabel("FFT") # x-Achse beschriften
        plt.xlim([0,1500]) # länge der angezeigten x-Achse
    
    return FFTmeasurepoints, FFTfrequencys  
    
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
    
def calculate_THD_KlasseA(SAMPLEPOINTS, SAMPLING_RATE):
    #Lade Messpunkte der FFT
    FFTmeasurepoints, FFTfrequencys = fast_fourier_transformation(SAMPLEPOINTS, SAMPLING_RATE)
    THD = 0 #Startwert der THD
    Bereich_Amplituden = round(SAMPLEPOINTS/float(SAMPLING_RATE)*calculate_Frequency(SAMPLING_RATE)) #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden           
    for i in range(2,41): 
        THD_Amplituden = FFTmeasurepoints[round(Bereich_Amplituden*i)] #direkter Amplitudenwert aus FFT   
        #Berechnung des THD-Wertes über eine for-Schleife        
        THD_Amplituden = np.power((THD_Amplituden),2)  
        THD = THD + THD_Amplituden
    THD_KlasseA = np.sqrt(THD/(FFTmeasurepoints[SAMPLEPOINTS/float(SAMPLING_RATE)/0.02]**2)) #darf nicht größer als 8% betragen
    return THD_KlasseA

def calculate_THD_KlasseS(SAMPLEPOINTS, SAMPLING_RATE):
    #Lade Messpunkte der FFT   
    FFTmeasurepoints, FFTfrequencys= fast_fourier_transformation(SAMPLEPOINTS, SAMPLING_RATE)
    Gruppierung = 0
    Bereich_Amplituden = int(round(SAMPLEPOINTS/float(SAMPLING_RATE)*calculate_Frequency(SAMPLING_RATE))) #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden 
    for i in range(1,41): 
        Gruppierung_teil1 = 0.5*FFTmeasurepoints[int(round(Bereich_Amplituden*i-Bereich_Amplituden/2))]**2
        Gruppierung_teil2 = 0.5*FFTmeasurepoints[int(round(Bereich_Amplituden*i+Bereich_Amplituden/2))]**2
        FFTmeasurepoints_Bereich = FFTmeasurepoints[int(round(Bereich_Amplituden*i-Bereich_Amplituden/2+1)):int(round(Bereich_Amplituden+Bereich_Amplituden/2)-1)]**2       
        Gruppierung_teil3 = np.sum(FFTmeasurepoints_Bereich)
        Gruppierung = Gruppierung_teil1+Gruppierung_teil2+Gruppierung_teil3+Gruppierung
        if (i==1):
            erste_Oberschwingung = Gruppierung
            Gruppierung = 0
    THD_KlasseS = np.sqrt(Gruppierung/erste_Oberschwingung)
    return THD_KlasseS

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
    measurepoints = load_measurepoints(SAMPLEPOINTS)    
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
        time1 = time.time()
        #THD is calculated
        THD_KlasseA = calculate_THD_KlasseA(SAMPLEPOINTS, SAMPLING_RATE)
        print("THD nach Klasse A = " + str(THD_KlasseA))
        time2 = time.time()        
        THD_KlasseS = calculate_THD_KlasseS(SAMPLEPOINTS, SAMPLING_RATE)
        print("THD nach Klasse S = " + str(THD_KlasseS))
        time3 = time.time()
        #rms voltage is calculated
        rms = calculate_rms()
        print("Effektivwert = " + str(rms))
        time4 = time.time()
        #freqency is calculated
        freqency = calculate_Frequency(SAMPLING_RATE)
        print("Frequenz = " + str(freqency))
        time5 = time.time()
        Pst = fl.calculate_Pst()
        print("Pst = " + str(Pst))
        time6 = time.time()
        
        print("THD-Berechnungszeit (Klasse A) = " + str(time2-time1) + " sekunden")
        print("THD-Berechnungszeit (Klasse S) = " + str(time3-time2) + " sekunden")
        print("Effektivwert-Berechnungzeit = " + str(time4-time3) + " sekunden")
        print("Frequenzberechnungszeit = " + str(time5-time4) + " sekunden")
        print("Flickerberechnungszeit = " + str(time6-time5) + " sekunden")
        print("Gesamtberechnungszeit = " + str(time6-time1) + " sekunden")

    #except:
        print("there must be something wrong")
    
    finally:
        print("Alle Daten wurden berechnet")
