from queue import Queue
from threading import Thread

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from parameters import Parameters
from standards import LDCarriers
from sys import stdin
import nearest
from FFTtools import FFTtools as FFT
from resample import Arbitrary as ar
from gui import spectra

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


def read_block16(samples):
    xf = list()
    mid = 0xFFFF / 2
    while len(xf) < samples:
        x = int.from_bytes(stdin.buffer.read(2), byteorder='little', signed=False)
        xf.append((x - mid/2) / mid)
    return xf


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
        efm = self.ld.efm()
        self.carriers = { audio['L'], audio['R'], audio['AC3'], efm['L'], efm['H'] }
        self.carrier_hist = { audio['L']: 0, audio['R']: 0, audio['AC3']: 0, efm['L']: 0, efm['H']: 0 }
        self.FFT_points = 64
        self.audio = audio
        self.efm = efm
        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.publish)
        self.consumer = Consumer()
        self.verbose_print()
        #self.timer.start()


    def end(self):
        self.timer.stop()
        self.exit = True

    def verbose_print(self):
        print_parameters(self.params)
        print_standards(self.params)
        print('Starting FFT analysis ... ')

    def publish(self):
        self.consumer.worker(self.queue)

    def run(self):
        while not self.exit:
            self.consumer.worker(self.produce())

    def produce(self):
        low_rate = nearest.power(self.params.samp_rate()/4, 2)
        #self_test(params, low_rate, FFT_points)

        fft = FFT(self.FFT_points, low_rate)

        m = self.params.samp_rate() / low_rate
        read_size = round(self.FFT_points * m)
        #print('read size', read_size)
        res = ar(self.params.samp_rate())

        x = read_block16(read_size)
        xl = res.autorational_downsample(x, low_rate)
        xn = fft.removeDC(xl)
        yf = fft.do(xn)
        return fft.plot(yf)
        #foo, bar, peaks = fft.peaks(yf)
        #print(peaks)
        #carrier_hist = fft.carrier_hist(self.carriers, peaks, 1, carrier_hist)

        #print(carrier_hist)
        #print('Reading thread ended')


if __name__ == '__main__':
    app = QApplication([])
    main = Main()
    main.daemon = True
    main.start()
    #main.run()
    app.exec()
    main.end()
    main.join()
