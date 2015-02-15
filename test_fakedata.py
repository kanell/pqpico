import Picoscope4000
import matplotlib.pyplot as plt
import time

pico = Picoscope4000.Picoscope4000()
pico.run_streaming()

for i in xrange(1):
    data = pico.get_queue_data()
    print(str(data))
    plt.show()
    plt.plot(data)
    plt.grid()
    plt.show()
    time.sleep(0.2) 
