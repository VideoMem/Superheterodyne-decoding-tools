from queue import Queue
from threading import Thread

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from parameters import Parameters
from standards import LDCarriers

import nearest
from FFTtools import FFTtools as FFT
from resample import Arbitrary as ar
from gui import spectra
from tests import stdin

def toMHz(v):
    return v/1e6

def tokHz(v):
    return v/1e3

def print_parameters(p):
    print('input sample rate: %d' % p.samp_rate())
    print('lines per frame: %d' % p.lines_per_frame())
    print('vsync frequency: %d Hz' % p.vsync())
    print('hsync frequency: %.3f kHz' % tokHz(p.hsync()))

def print_standards(p):
    ld = LDCarriers(p.hsync())
    audio = ld.audioNTSC()
    print('expected analogue left carrier frequency: %.7f MHz' % toMHz(audio['L']))
    print('expected analogue right carrier frequency: %.7f MHz' % toMHz(audio['R']))
    print('expected AC3 QPSK carrier frequency: %.7f MHz' % toMHz(audio['AC3']))


#def read_block16(samples):
#    xf = list()
#    mid = 0xFFFF / 2
#    while len(xf) < samples:
#        x = int.from_bytes(stdin.buffer.read(2), byteorder='little', signed=False)
#        xf.append((x - mid/2) / mid)
#    return xf


def self_test(p, rate, FFT_points):
    fft = FFT(FFT_points, rate)
    x = fft.test_signal(p.hsync())
    xn = fft.removeDC(x)
    yf = fft.do(xn)
    fft.plot(yf)


class Consumer:
    def __init__(self):
        self.gui = spectra.GUIspectra()
        self.gui.show()

    def worker(self, data):
        self.gui.publish(data)


class Main(Thread):
    def __init__(self):
        super().__init__()
        self.exit = False
        self.params = Parameters()
        self.ld = LDCarriers(self.params.hsync())
        audio = self.ld.audioNTSC()
        audioPAL = self.ld.audioPAL()
        efm = self.ld.efm()
        self.carriers = { efm['L'], efm['H'], audioPAL['L'], audioPAL['R'], audio['L'], audio['R'], audio['AC3'] }
        self.carrier_hist = { efm['L']: 0, efm['H']: 0, audioPAL['L']: 0, audioPAL['R']: 0, audio['L']: 0, audio['R']: 0, audio['AC3']: 0 }
        self.FFT_points = 256
        self.audio = audio
        self.efm = efm
        self.consumer = Consumer()
        self.verbose_print()
        self.reads = 0
        if self.params.start_at() > 0:
            self.skip_head()

    def end(self):
        self.exit = True

    def verbose_print(self):
        print_parameters(self.params)
        print_standards(self.params)
        print('Starting FFT analysis ... ')

    def run(self):
        while not self.exit:
            self.consumer.worker(self.produce())

    def low_rate(self):
        return nearest.power(self.params.samp_rate()/4, 2)

    def skip_head(self):
        skip_samples = self.params.samp_rate() * self.params.start_at()
        m = self.params.samp_rate() / self.low_rate()
        read_size = round(self.FFT_points * m)
        print('skipping %f seconds' % self.params.start_at())
        while skip_samples > 0:
            stdin.read_block16(read_size)
            skip_samples -= read_size

    def produce(self):
        #self_test(params, low_rate, FFT_points)

        fft = FFT(self.FFT_points, self.low_rate(), self.carriers)

        m = self.params.samp_rate() / self.low_rate()
        read_size = round(self.FFT_points * m)
        #print('read size', read_size)
        res = ar(self.params.samp_rate())

        x = stdin.read_block16(read_size)
        xl = res.autorational_downsample(x, self.low_rate())
        xn = fft.removeDC(xl)
        yf = fft.do(xn)
        yp = fft.peaks(yf)
        self.reads += read_size
        block = round(self.reads / read_size)
        xd, yd, peaks = yp
        self.carrier_hist = fft.carrier_hist(self.carriers, peaks, fft.get_error(), self.carrier_hist)
        if block % 10 == 0:
            print('Secs elapsed: %f' % (self.reads/self.params.samp_rate()))
        if block % 100 == 0:
            print('block: %d' % block, self.carrier_hist)

        return fft.plot(yp)


if __name__ == '__main__':
    app = QApplication([])
    main = Main()
    main.daemon = True
    main.start()
    app.exec()
    main.end()
    main.join()
