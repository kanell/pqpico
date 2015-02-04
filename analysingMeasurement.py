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
import scipy.io as io


SAMPLING_RATE = 1000000#1000000  #Sampling Rate
SAMPLEPOINTS = 2**round(np.log(SAMPLING_RATE*0.2)/np.log(2))
Un = 230 #Volt
V_max = 32768/50
R1 = 993000
R2 = 82400
#class analysingMeasurement:
    
def load_measurepoints(SAMPLEPOINTS):
    #Load files from the directory        
    npyfiles = glob.glob('C:\\Users\Malte Gerber\Desktop\Messdaten\*.npy')
    measurepoints = np.load(npyfiles[0])
    #add the content from all files to one list
    i = 1
    while len(measurepoints) < SAMPLEPOINTS:
        #Messdaten werden solange in ein Array geladen, bis es mehr als die vorgegebene Samplepoints sind        
        measurepoints = np.concatenate([measurepoints, (np.load(npyfiles[i]))], axis=0) 
        i = i+1
    measurepoints = np.load('smoothed.npy')
    #io.savemat('Messpunkte_1000S.mat', mdict={'measurepoints':measurepoints})
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
    FFTfrequencys = np.fft.fftfreq(len(FFTmeasurepoints), 1.0/SAMPLING_RATE)
    #wegkürzen der negativen frequenzen und dafür verdoppeln der Amplituden
    FFTmeasurepoints = np.abs(FFTmeasurepoints[(len(FFTmeasurepoints)/2):])*2
    
    if (plot_FFT):
        plt.plot(FFTfrequencys[:SAMPLEPOINTS/2], FFTmeasurepoints) #Plot der Messwerte der FFT über die gegebene x-Achse fMax
        plt.xlabel("f in Hz") # y-Achse beschriefen
        plt.ylabel("FFT") # x-Achse beschriften
        plt.xlim([0,1500]) # länge der angezeigten x-Achse
    
    return FFTmeasurepoints, FFTfrequencys  
    
def calculate_rms(*measurepoints):
    #Laden der Messwerte
    if not measurepoints:
        measurepoints = load_measurepoints(SAMPLEPOINTS)
    elif measurepoints:
        measurepoints = measurepoints[0]
    #Der Effektivwert wird ueber alle Messpunkte gebildet    
    rms_points = np.sqrt(np.mean(np.power(np.float32(measurepoints), 2)))
    rms = rms_points/V_max*R1/R2
    return rms

def example_sin_waves(SAMPLEPOINTS, SAMPLING_RATE):  #Beispiel für Sinusschwingungen mit Oberschwingungen
    Tn = 0.02 #ms Frequenz der sinusspannung
    t = np.linspace(0.0,1.0*SAMPLEPOINTS/SAMPLING_RATE,num=SAMPLEPOINTS) #Zeitachse der Sinusschwingung als Samplepoints mit bestimmter Samplerate
    measurepoints1 = 230*np.sqrt(2)*np.sin(2*np.pi/Tn*t+0) #Array mit Messwerten
    measurepoints2 = 230*np.sqrt(2)*np.sin(2*np.pi/Tn*t+2*np.pi/3) #Array mit Messwerten
    measurepoints3 = 230*np.sqrt(2)*np.sin(2*np.pi/Tn*t+4*np.pi/3) #Array mit Messwerten    
    return measurepoints1, measurepoints2, measurepoints3
    
def calculate_THD_KlasseA(SAMPLEPOINTS, SAMPLING_RATE, *measured_frequency):
    #Lade Messpunkte der FFT
    FFTmeasurepoints, FFTfrequencys = fast_fourier_transformation(SAMPLEPOINTS, SAMPLING_RATE)
    THD = 0 #Startwert der THD
    if not measured_frequency:
        measured_frequency = calculate_Frequency(SAMPLING_RATE, *measurepoints)
    elif measured_frequency:
        measured_frequency = measured_frequency[0]
    Bereich_Amplituden = round(SAMPLEPOINTS/float(SAMPLING_RATE)*measured_frequency) #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden           
    for i in range(1,41): 
        #Berechnung des THD-Wertes über eine for-Schleife        
        THD_Amplituden = np.sum(FFTmeasurepoints[int(Bereich_Amplituden*i-1):int(Bereich_Amplituden*i+2)]**2) #direkter Amplitudenwert aus FFT           
        THD = THD + THD_Amplituden
        if (i==1):
            erste_Oberschwingung = THD
            THD = 0
    THD_KlasseA = np.sqrt(THD/erste_Oberschwingung)*100 #darf nicht größer als 8% betragen
    return THD_KlasseA

def calculate_THD_KlasseS(SAMPLEPOINTS, SAMPLING_RATE, *measured_frequency):
    #Lade Messpunkte der FFT   
    FFTmeasurepoints, FFTfrequencys= fast_fourier_transformation(SAMPLEPOINTS, SAMPLING_RATE)
    Gruppierung = 0
    if not measured_frequency:
        measured_frequency = calculate_Frequency(SAMPLING_RATE, *measurepoints)
    elif measured_frequency:
        measured_frequency = measured_frequency[0]
    Bereich_Amplituden = SAMPLEPOINTS/float(SAMPLING_RATE)*measured_frequency #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden 
    for i in range(1,41): 
        Gruppierung_teil1 = 0.5*FFTmeasurepoints[int(round(Bereich_Amplituden*i-Bereich_Amplituden/2))]**2
        Gruppierung_teil2 = 0.5*FFTmeasurepoints[int(round(Bereich_Amplituden*i+Bereich_Amplituden/2))]**2
        Gruppierung_teil3 = np.sum(FFTmeasurepoints[int(round(Bereich_Amplituden*i-Bereich_Amplituden/2)+1):int(round(Bereich_Amplituden*i+Bereich_Amplituden/2))]**2)       
        Gruppierung = Gruppierung_teil1+Gruppierung_teil2+Gruppierung_teil3+Gruppierung
        if (i==1):
            erste_Oberschwingung = Gruppierung
            Gruppierung = 0
    THD_KlasseS = np.sqrt(Gruppierung/erste_Oberschwingung)*100
    return THD_KlasseS

def calculate_Frequency(SAMPLING_RATE, *measurepoints):    
    measurepoints_filtered = Lowpass_Filter(*measurepoints)
    #measurepoints_filtered = measurepoints[0]
    #measurepoints_filtered = measurepoints[0]    
    t = []       
    for i in range(len(measurepoints_filtered)-1):
        if (measurepoints_filtered[i]<=0 and measurepoints_filtered[i+1]>0):           
            t.append(i - measurepoints_filtered[i]/(measurepoints_filtered[i+1]-measurepoints_filtered[i]))
    freqency_samplepoints = (t[len(t)-1]-t[0])/(len(t)-1)
    freqency_seconds = SAMPLING_RATE/freqency_samplepoints
            
    return freqency_seconds
    
def Lowpass_Filter(*measurepoints):
    show_filtered_measurement = 1    
    #Lade Messwerte
    if not measurepoints:    
        measurepoints = load_measurepoints(SAMPLEPOINTS)
    elif measurepoints:
        measurepoints = measurepoints[0]
    b_hp, a_hp = signal.butter(1, (2100/(SAMPLING_RATE/2)), 'lowpass')
    measurepoints_filtered = signal.lfilter(b_hp, a_hp, measurepoints)
    
    if (show_filtered_measurement):
        plt.plot(measurepoints, 'b') 
        plt.plot(measurepoints_filtered, 'r')
        plt.xlim(0, 40000)
        plt.grid(True) 
        
    
    return measurepoints_filtered
    
def calculate_phasediff():
    m1,m2,m3 = example_sin_waves(SAMPLEPOINTS, SAMPLING_RATE)
    a = np.e**(120j)
    F_matrix = np.matrix([[1,1,1],[1,a,a**2],[1,a**2,a]])
    u2_list = []
    u0_list = []
    for i in range(len(m1)):
        m_unsym = np.matrix([[m1[i]],[m2[i]],[m3[i]]])
        m_sym = 1/3*F_matrix*m_unsym
        u2 = np.abs(m_sym[2]/m_sym[1]*100)
        u0 = np.abs(m_sym[0]/m_sym[1]*100)
        u2_list.append(u2)
        u0_list.append(u0)
    u2 = np.mean(u2_list)
    u0 = np.mean(u0_list)
    return u2,u0
            
    
if __name__ == '__main__':
    try:
        time0 = time.time()
        measurepoints = load_measurepoints(SAMPLEPOINTS)
        time1 = time.time()
        #freqency is calculated
        measured_frequency = calculate_Frequency(SAMPLING_RATE, measurepoints)
        print("Frequenz = " + str(measured_frequency) + " Hz")        
        time2 = time.time()
        #rms voltage is calculated
        rms = calculate_rms(measurepoints)
        print("Effektivwert = " + str(rms)+ " V")
        time3 = time.time()
        #THD is calculated
        THD_KlasseA = calculate_THD_KlasseA(SAMPLEPOINTS, SAMPLING_RATE, measured_frequency)
        print("THD nach Klasse A = " + str(THD_KlasseA) + " %")
        time4 = time.time()        
        THD_KlasseS = calculate_THD_KlasseS(SAMPLEPOINTS, SAMPLING_RATE, measured_frequency)
        print("THD nach Klasse S = " + str(THD_KlasseS) + " %")
        time5 = time.time()
        Pst = fl.calculate_Pst(measurepoints, SAMPLING_RATE)
        print("Pst = " + str(Pst))
        time6 = time.time()
#        u2,u0 = calculate_phasediff()        
#        print(str(u2) + "\n" + str(u0))
        time7 = time.time()
        
        print("Messwerteladezeit = " + str(time1-time0) + " sek.")        
        print("Frequenzberechnungszeit = " + str(time2-time1) + " sek.")
        print("Effektivwert-Berechnungzeit = " + str(time3-time2) + " sek.")
        print("THD-Berechnungszeit (Klasse A) = " + str(time4-time3) + " sek.")
        print("THD-Berechnungszeit (Klasse S) = " + str(time5-time4) + " sek.")
        print("Flickerberechnungszeit = " + str(time6-time5) + " sek.")
        print("Unsym.-Berechnungszeit = " + str(time7-time6) + " sek.")
        print("Gesamtberechnungszeit = " + str(time7-time0) + " sek.")

    except:
        print("there must be something wrong")
    
    finally:
        print("Alle Daten wurden berechnet")
