import numpy as np

class ring_array(np.ndarray):
    def __init__(self, size = 100000):
        self.data = np.array(np.zeros(size))
        self.index_end_data = 0

    def attach(self, data_to_attach):
        try:
            self.data[self.index_end_data:self.index_end_data + data_to_attach.size] = data_to_attach
        except AttributeError:
            print('data_to_attach has no .size attribute, should be of type numpy.ndarray')


if __name__ == '__main__':
    a = ring_array(1)
    a.attach(2)


