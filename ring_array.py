import numpy as np

class ring_array():
    def __init__(self, size = 1000000):
        self.ringBuffer = np.array(np.zeros(size))
        self.zero_indices = np.array(np.zeros(size/1000))
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
    a = ring_array()
    print(str(a.get_data_view()))
    b = np.array([4,5,6])
    print(str(b))
    a.attach_to_back(b)
    print(str(a.get_data_view()))
    a.attach_to_back(b)
    print(str(a.get_data_view()))

    print(a.cut_off_front(4))
    print(str(a.get_data_view()))

def test_ring_array():
    
    a = ring_array()
    b = np.array([4,5,6])
    a.attach_to_back(b)
