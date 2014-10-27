# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 16:50:00 2014

@author: ckattmann
"""

import os
import glob
import numpy as np
import matplotlib.pyplot as plt

npyfiles = glob.glob('Data\*.npy')
a = np.load(npyfiles[1])

#os.path.getsize
#Plot array lengths

npylengths = [os.path.getsize(npyfiles[i]) for i in range(len(npyfiles))]

plt.plot(npylengths)