# -*- coding: utf-8 -*-
"""
Created on Wed Sep  3 13:43:46 2014

@author: ckattmann
"""

import sys, time, ctypes
from functools import partial
import numpy as np
import matplotlib.pyplot as plt

import cProfile


VERBOSE = 1

## Constants of PS2000.dll
# channel identifiers
PS2000_CHANNEL_A = 0
PS2000_CHANNEL_B = 1

# channel range values/codes
RANGE_20MV  = 1  # 20 mV
RANGE_50MV  = 2  # 50 mV
RANGE_100MV = 3  # 100 mV
RANGE_200MV = 4  # 200 mV
RANGE_500MV = 5  # 500 mV
RANGE_1V    = 6  # 1 V
RANGE_2V    = 7  # 2 V
RANGE_5V    = 8  # 5 V
RANGE_10V   = 9  # 10 V
RANGE_20V   = 10 # 20 V

# map the range the the scale factor
RANGE_SCALE_MAP = {
RANGE_20MV  : 0.02,
RANGE_50MV  : 0.05,
RANGE_100MV : 0.1,
RANGE_200MV : 0.2,
RANGE_500MV : 0.5,
RANGE_1V    : 1.0,
RANGE_2V    : 2.0,
RANGE_5V    : 5.0,
RANGE_10V   : 10.0,
RANGE_20V   : 20.0,
}

if sys.platform == 'win32':
    LIBNAME = 'C:\Program Files\Pico Technology\PicoScope6\PS2000.dll'
else:
    LIBNAME = '/usr/local/lib/libps2000.so.2.0.7'
    
class PicoError(Exception):
    '''pico scope error'''
        
    
class Picoscope:
    
    def __init__(self):
        self.handle = None

        # load the library
        if sys.platform == 'win32':
            self.lib = ctypes.windll.LoadLibrary(LIBNAME)
        else:
            self.lib = ctypes.cdll.LoadLibrary(LIBNAME)
        if not self.lib:
            raise PicoError('could not open library: %s' % LIBNAME)
            
        # open the picoscope
        self.handle = self.open_unit()
#        
    def open_unit(self):
        '''open interface to unit'''
        if VERBOSE == 1:
            print('Opening Picoscope')
        self.handle = self.lib.ps2000_open_unit()
        return self.handle

    def close_unit(self):
        '''close the interface to the unit'''
        if VERBOSE == 1:
            print('Closing Picoscope')
        res = self.lib.ps2000_close_unit(self.handle)
        self.handle = None
        return res
        
    def set_channel(self, channel=PS2000_CHANNEL_A, enabled=True, dc=True, vertrange=RANGE_1V):
        '''Default Values: channel: Channel A | channel enabled: true | ac/dc coupling mode: dc(=true) | vertical range: 2Vpp'''
        try:
            self.lib.ps2000_set_channel(self.handle, channel, enabled, dc, vertrange)
            if VERBOSE == 1:
                print('Channel set to Channel '+str(channel))
        finally:
            pass
        
    def run_streaming(self, sample_interval_ms=1, max_samples=1000, windowed=0):
        '''Default Values: Sample Rate: 10ms | Max Samples: 100 | Windowed: No (=0) '''
        try:
            res = self.lib.ps2000_run_streaming(self.handle, sample_interval_ms, max_samples, windowed)
        finally:
            pass
        return res
        
    def get_values(self, no_of_values=1000):
        try:
            buffer_a = (ctypes.c_short * no_of_values)()
            buffer_b = (ctypes.c_short * no_of_values)()
            buffer_c = None
            buffer_d = None
            overflow = ctypes.c_short()
            no_of_values = ctypes.c_long(no_of_values)
            self.lib.ps2000_get_values(self.handle, 
                                        ctypes.byref(buffer_a), ctypes.byref(buffer_b), 
                                        buffer_c, buffer_d, overflow,
                                        ctypes.byref(no_of_values))
            return np.ctypeslib.as_array(buffer_a)
        finally:
            pass
    
if __name__ == '__main__':
    try:
        pr=cProfile.Profile()
        pr.enable()
        # Picoscope
        resolution = 1 #in ms        
        samplepoints = 1000 # samples collected, max is 60000
        vertrange = RANGE_2V
        
        # Numpy and Matplotlib
        plotarray = np.array([])
        yticklocations = [-32767, -32767/2, 0, 32768/2, 32768]
        ytickstrings = [    str(-RANGE_SCALE_MAP[vertrange])+' V', 
                            str(-RANGE_SCALE_MAP[vertrange]/2)+' V', 
                            str(0*RANGE_SCALE_MAP[vertrange])+' V', 
                            str(RANGE_SCALE_MAP[vertrange]/2)+' V',
                            str(RANGE_SCALE_MAP[vertrange])+' V']
                            
        xticklocations = np.arange(0,1001,200)
        xtickstrings = [str(x)+' ms' for x in xticklocations]
        
        pico = Picoscope()
        pico.set_channel(channel = PS2000_CHANNEL_A,vertrange=vertrange)
        pico.run_streaming(sample_interval_ms=resolution, max_samples=samplepoints)
        plt.ion()
        plt.pause(0.1)
        
        
        for i in range(100):
            
            b = pico.get_values()
            b = np.trim_zeros(b)
            print(str(b.size)+' sample points collected')
            
            plotarray = np.append(plotarray,b)
            plotarray = plotarray[-samplepoints:]
            plt.plot(plotarray)
            plt.yticks(yticklocations, ytickstrings)
            plt.xticks(xticklocations, xtickstrings)
            plt.grid(True)
            plt.hold(False)
            
            plt.draw()
            plt.pause(0.001)
            plt.grid(1)
            
        pr.disable()
        sys.stdout = open('profile.txt','w')
        pr.print_stats(sort='cumtime')
        
    finally:
        pico.close_unit()
