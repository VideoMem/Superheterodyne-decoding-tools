import numpy as np


#code borrowed partially from ld-decode/lddecode/fft8.py
class ReadFile:

    def __init__(self, filename, MAX_SAMPLES):
        self.filename = filename
        if filename.endswith('.ld') or \
                filename.endswith('.r16') or \
                filename.endswith('/urandom') or\
                filename.endswith('/zero'):
            self.ttype = np.uint16
            self.max_samples = MAX_SAMPLES * 2
            print('Assuming 16 bits per sample')
        else:
            self.ttype = np.uint8
            self.max_samples = MAX_SAMPLES
            print('Assuming 8 bits per sample')


    def read(self, xtra):
        with open(self.filename, "rb") as binfile:
            data = np.fromstring(binfile.read(self.max_samples), dtype=self.ttype)
            #print('Loaded %d bytes of file %s' % (self.max_samples, self.filename))
        return data
