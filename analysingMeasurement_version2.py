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
from threading import Thread
import queue

SAMPLING_RATE = 1000000  #Sampling Rate
SAMPLEPOINTS = 2**round(np.log(SAMPLING_RATE*0.2)/np.log(2))
Un = 230 #Volt
V_max = 32768/50
R1 = 993000 #Ohm
R2 = 82400*1000000/(82400+1000000) #Ohm
Resolution = (R1+R2)/R2



class analysingMeasurement:
    
    def load_measurepoints(self, SAMPLEPOINTS):
        #Load files from the directory        
#        npyfiles = glob.glob('C:\\Users\Malte Gerber\Desktop\Messdaten\*.npy')
#        measurepoints = np.load(npyfiles[0])
#        #add the content from all files to one list
#        i = 1
#        while len(measurepoints) < SAMPLEPOINTS:
#            #Messdaten werden solange in ein Array geladen, bis es mehr als die vorgegebene Samplepoints sind        
#            measurepoints = np.concatenate([measurepoints, (np.load(npyfiles[i]))], axis=0) 
#            i = i+1
        measurepoints = np.load('20150123_17_50_52_201410.npy')
        #Messdaten werden genau auf die vorgegebenen Samplepoints gebracht
        self.measurepoints = measurepoints[:SAMPLEPOINTS]
        #self.measurepoints = self.example_sin_waves(SAMPLEPOINTS,SAMPLING_RATE)[0]
        return self.measurepoints
        
    def Lowpass_Filter(self, measurepoints):
        show_filtered_measurement = 0    
        b_hp, a_hp = signal.butter(1, (2100/(SAMPLING_RATE/2)), 'lowpass')
        self.measurepoints_filtered = signal.lfilter(b_hp, a_hp, measurepoints)
        
        if (show_filtered_measurement):
            plt.plot(self.measurepoints, 'b') 
            plt.plot(self.measurepoints_filtered, 'r')
            plt.xlim(0, 40000)
            plt.grid(True)  
            
        
        return self.measurepoints_filtered

    def calculate_Frequency(self, SAMPLING_RATE, measurepoints):    
        self.Lowpass_Filter(measurepoints)    
        t = []       
        for i in range(len(self.measurepoints_filtered)-1):
            if (self.measurepoints_filtered[i]<=0 and self.measurepoints_filtered[i+1]>0):           
                t.append(i - self.measurepoints_filtered[i]/(self.measurepoints_filtered[i+1]-self.measurepoints_filtered[i]))
        self.freq_sample = (t[len(t)-1]-t[0])/(len(t)-1)
        self.measured_frequency = SAMPLING_RATE/self.freq_sample
                
        return self.measured_frequency, self.freq_sample
                
    def fast_fourier_transformation(self, measurepoints, SAMPLING_RATE):
        plot_FFT = 0    #Show FFT Signal Plot        
        #berechnen der Fouriertransformation        
        FFTmeasurepoints = np.fft.fftshift(np.fft.fft(measurepoints))/len(measurepoints)     
        #Frequenzen der Oberschwingungen    
        self.FFTfrequencys = np.fft.fftfreq(len(FFTmeasurepoints), 1.0/SAMPLING_RATE)
        #wegkürzen der negativen frequenzen und dafür verdoppeln der Amplituden
        self.FFTmeasurepoints = np.abs(FFTmeasurepoints[(len(FFTmeasurepoints)/2):])*2
        
        if (plot_FFT):
            plt.plot(self.FFTfrequencys[:len(measurepoints)/2], self.FFTmeasurepoints) #Plot der Messwerte der FFT über die gegebene x-Achse fMax
            plt.xlabel("f in Hz") # y-Achse beschriefen
            plt.ylabel("FFT") # x-Achse beschriften
            plt.xlim([0,1500]) # länge der angezeigten x-Achse
        
        return self.FFTmeasurepoints, self.FFTfrequencys  
        
    def calculate_rms(self, measurepoints):
        #Der Effektivwert wird ueber alle Messpunkte gebildet    
        #resolution =         
        rms_points = np.sqrt(np.mean(np.power(measurepoints, 2)))
        rms = rms_points/V_max*Resolution
        if (rms <= (0.9*230) and rms >= (0.1*230)):
            print ("Es ist eine Unterspannung aufgetreten!")
            #t.append(rms)
        elif rms < 0.1*230:
            print("Es liegt eine Spannungunterbrechung vor!")
            #t.append(rms)
        elif rms > 1.1*230:
            print ("Es ist eine Überspannung aufgetreten!")
            #t.append(rms)
        else:
            print("Alles OK!")
            #t.append(rms)
        return rms
    
    def calculate_rms_half_period(self, measurepoints, counter):        
                
        rms_points = np.sqrt(np.mean(np.power(measurepoints[int(round(self.freq_sample/2*counter)):int(round(self.freq_sample/2*(counter+1)))], 2)))
        rms_half_period = rms_points/V_max*Resolution
        if (rms_half_period <= (0.9*230) and rms_half_period >= (0.1*230)):
            print ("Es ist eine Unterspannung aufgetreten!")
            #t.append(rms_half_period)
        elif rms_half_period < 0.1*230:
            print("Es liegt eine Spannungunterbrechung vor!")
            #t.append(rms_half_period)
        elif rms_half_period > 1.1*230:
            print ("Es ist eine Überspannung aufgetreten!")
            #t.append(rms_half_period)
        else:
            print("Alles OK!")
            #t.append(rms_half_period)
        return rms_half_period
        
    def example_sin_waves(self, SAMPLEPOINTS, SAMPLING_RATE):  #Beispiel für Sinusschwingungen mit Oberschwingungen
        Tn = 0.02 #ms Frequenz der sinusspannung
        t = np.linspace(0.0,1.0*SAMPLEPOINTS/SAMPLING_RATE,num=SAMPLEPOINTS) #Zeitachse der Sinusschwingung als Samplepoints mit bestimmter Samplerate
        self.measurepoints1 = 230*np.sqrt(2)*np.sin(2*np.pi/Tn*t+0) #Array mit Messwerten
        self.measurepoints2 = 230*np.sqrt(2)*np.sin(2*np.pi/Tn*t+2*np.pi/3) #Array mit Messwerten
        self.measurepoints3 = 230*np.sqrt(2)*np.sin(2*np.pi/Tn*t+4*np.pi/3) #Array mit Messwerten    
        return self.measurepoints1, self.measurepoints2, self.measurepoints3
        
    def calculate_THD_KlasseA(self, measurepoints, SAMPLING_RATE):
        self.fast_fourier_transformation(measurepoints, SAMPLING_RATE)        
        THD = 0 #Startwert der THD
        Bereich_Amplituden = round(len(measurepoints)/float(SAMPLING_RATE)*self.measured_frequency) #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden           
        for i in range(1,41): 
            #Berechnung des THD-Wertes über eine for-Schleife        
            THD_Amplituden = np.sum(self.FFTmeasurepoints[int(Bereich_Amplituden*i-1):int(Bereich_Amplituden*i+2)]**2) #direkter Amplitudenwert aus FFT           
            THD = THD + THD_Amplituden
            if (i==1):
                erste_Oberschwingung = THD
                THD = 0
        self.THD_KlasseA = np.sqrt(THD/(erste_Oberschwingung))*100 #darf nicht größer als 8% betragen
        if self.THD_KlasseA <= 8:
            print("THD_A ist OK!")
        else:
            print("THD zu hoch: THD_A = " + str(self.THD_KlasseA))
        return self.THD_KlasseA
    
    def calculate_THD_KlasseS(self, measurepoints, SAMPLING_RATE):
        self.fast_fourier_transformation(measurepoints, SAMPLING_RATE)        
        Gruppierung = 0
        Bereich_Amplituden = len(measurepoints)/float(SAMPLING_RATE)*self.measured_frequency #an dieser Stelle sollte sich der Amplitudenausschlag der Oberschwingung befinden 
        for i in range(1,41): 
            Gruppierung_teil1 = 0.5*self.FFTmeasurepoints[int(round(Bereich_Amplituden*i-Bereich_Amplituden/2))]**2
            Gruppierung_teil2 = 0.5*self.FFTmeasurepoints[int(round(Bereich_Amplituden*i+Bereich_Amplituden/2))]**2
            Gruppierung_teil3 = np.sum(self.FFTmeasurepoints[int(round(Bereich_Amplituden*i-Bereich_Amplituden/2)+1):int(round(Bereich_Amplituden*i+Bereich_Amplituden/2))]**2)       
            Gruppierung = Gruppierung_teil1+Gruppierung_teil2+Gruppierung_teil3+Gruppierung
            if (i==1):
                erste_Oberschwingung = Gruppierung
                Gruppierung = 0
        self.THD_KlasseS = np.sqrt(Gruppierung/erste_Oberschwingung)*100
        if self.THD_KlasseS <= 8:
            print("THD_S ist OK!")
        else:
            print("THD zu hoch: THD_S = " + str(self.THD_KlasseS))
        return self.THD_KlasseS
    
    def calculate_phasediff(self):
        m1,m2,m3 = self.example_sin_waves(SAMPLEPOINTS, SAMPLING_RATE)
        a = np.e**(120j)
        F_matrix = np.matrix([[1,1,1],[1,a,a**2],[1,a**2,a]])
        u2_list = [1]
        u0_list = [1]
        for i in range(len(m1)):
            m_unsym = np.matrix([[m1[i]],[m2[i]],[m3[i]]])
            m_sym = 1/3*F_matrix*m_unsym
            u2 = np.abs(m_sym[2]/m_sym[1]*100)
            u0 = np.abs(m_sym[0]/m_sym[1]*100)
            u2_list.append(u2)
            u0_list.append(u0)
        self.u2 = np.mean(u2_list)
        self.u0 = np.mean(u0_list)
        return self.u2,self.u0
    
#if __name__ == '__main__':
#    try:
#        ana = analysingMeasurement()
#                
#            
#        time0 = time.time()
#        measurepoints = ana.load_measurepoints(SAMPLEPOINTS)
#        time1 = time.time()
#        #freqency is calculated
#        measured_frequency = ana.calculate_Frequency(SAMPLING_RATE)
#        print("Frequenz = " + str(measured_frequency) + " Hz")        
#        time2 = time.time()
#        #rms voltage is calculated
#        rms = ana.calculate_rms()
#        rms_1_2 = ana.calculate_rms_half_period()
#        print("Effektivwert = " + str(rms)+ " V")
#        print("Effektivwert 1/2 Periode = " + str(rms_1_2)+ " V")
#        time3 = time.time()
#        #THD is calculated
#        THD_KlasseA = ana.calculate_THD_KlasseA(SAMPLEPOINTS, SAMPLING_RATE)
#        print("THD nach Klasse A = " + str(THD_KlasseA) + " %")
#        time4 = time.time()        
#        THD_KlasseS = ana.calculate_THD_KlasseS(SAMPLEPOINTS, SAMPLING_RATE)
#        print("THD nach Klasse S = " + str(THD_KlasseS) + " %")
#        time5 = time.time()
#        Pst = fl.calculate_Pst(measurepoints, SAMPLING_RATE)
#        print("Pst = " + str(Pst))
#        time6 = time.time()
##        u2,u0,unsymm = ana.calculate_phasediff()        
##        print(str(u2) + "\n" + str(u0) + "\n" + str(unsymm))
#        time7 = time.time()
#        
#        print("Messwerteladezeit = " + str(time1-time0) + " sek.")        
#        print("Frequenzberechnungszeit = " + str(time2-time1) + " sek.")
#        print("Effektivwert-Berechnungzeit = " + str(time3-time2) + " sek.")
#        print("THD-Berechnungszeit (Klasse A) = " + str(time4-time3) + " sek.")
#        print("THD-Berechnungszeit (Klasse S) = " + str(time5-time4) + " sek.")
#        print("Flickerberechnungszeit = " + str(time6-time5) + " sek.")
#        print("Unsym.-Berechnungszeit = " + str(time7-time6) + " sek.")
#        print("Gesamtberechnungszeit = " + str(time7-time0) + " sek.")
#
#    except:
#        print("there must be something wrong")
#    
#    finally:
#        print("Alle Daten wurden berechnet")
