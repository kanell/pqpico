import numpy as np
import PQTools3 as pq
import time

class ring_array_global_data():
    def __init__(self, size = 1000000):
        self.ringBuffer = np.array(np.zeros(size))
        self.zero_indices = np.array(np.zeros(200), dtype=np.int64)
        self.size = 0
        self.size_zero_indices = 0

    def get_data_view(self):
        return self.ringBuffer[:self.size]

    def get_index(self, index):
        return self.ringBuffer[index]
    
    def attach_to_back(self, data_to_attach):
        try:
            zero_indices_to_attach = pq.detect_zero_crossings(data_to_attach)            
            self.zero_indices[self.size_zero_indices:self.size_zero_indices + zero_indices_to_attach.size] = zero_indices_to_attach + self.size            
            self.ringBuffer[self.size:self.size + data_to_attach.size] = data_to_attach
        except AttributeError:
            print('data_to_attach has no .size attribute, should be of type numpy.ndarray')
        self.size += data_to_attach.size
        self.size_zero_indices += zero_indices_to_attach.size

    def cut_off_front(self, index, zero_crossing):
        self.ringBuffer = np.roll(self.ringBuffer,-index)
        self.zero_indices = np.roll(self.zero_indices,-zero_crossing)-index        
        self.size -= index
        self.size_zero_indices -= zero_crossing
        return self.ringBuffer[-index:]
    
    def get_zero_indices(self):
        return self.zero_indices[:self.size_zero_indices]
        
    def attach_to_front(self, data_to_attach):
        self.ringBuffer = np.roll(self.ringBuffer, data_to_attach.size)
        self.ringBuffer[:data_to_attach.size] = data_to_attach      
        self.size += data_to_attach.size
        self.zero_indices = pq.detect_zero_crossings(self.ringBuffer[:self.size])
        self.size_zero_indices = self.zero_indices.size
        
class ring_array():
    def __init__(self, size = 1000000):
        self.ringBuffer = np.array(np.zeros(size))
        self.size = 0

    def get_data_view(self):
        return self.ringBuffer[:self.size]

    def get_index(self, index):
        return self.ringBuffer[index]
    
    def attach_to_back(self, data_to_attach):       
        try:
            self.ringBuffer[self.size:self.size + data_to_attach.size] = data_to_attach
        except AttributeError:
            print('data_to_attach has no .size attribute, should be of type numpy.ndarray')
        self.size += data_to_attach.size

    def cut_off_front(self,index):
        self.ringBuffer = np.roll(self.ringBuffer,-index)
        self.size -= index
        return self.ringBuffer[-index:].copy()

if __name__ == '__main__':
    a = ring_array_global_data()
    #print(str(a.get_data_view()))
    b = np.array([4,5,6])
    #print(str(b))
    a.attach_to_back(b)
    #print(str(a.get_data_view()))
    a.attach_to_back(b)
    #print(str(a.get_zero_indices()))
    t1 = time.time()    
    print(a.cut_off_front(4,0))
    t2 = time.time()
    print(str(a.get_data_view()))
    c = a.get_data_view()
    t = a.get_zero_indices()
    print(str(t2-t1))

def test_ring_array():
    
    a = ring_array()
    b = np.array([4,5,6])
    a.attach_to_back(b)