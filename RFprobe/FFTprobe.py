import threading
from asyncio import Queue
import asyncio
from threading import Thread
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
        self.exit = False
        self.gui = spectra.GUIspectra()
        self.gui.show()

    def end(self):
        self.exit = True

    async def worker(self, queue):
        while not self.exit:
            data = await queue.get()
            self.gui.publish(data)
            queue.task_done()

        print('Consumer thread ended')


class Main(Thread):
    def __init__(self):
        super().__init__()
        self.queue = Queue()
        self.consumer = Consumer()
        self.loop = asyncio.get_event_loop()
        self.task = self.setup_worker()
        self.exit = False

    def end(self):
        self.exit = True

    def setup_worker(self):
        return self.loop.create_task(self.consumer.worker(self.queue))

    def run(self):
        params = Parameters()
        print_parameters(params)
        print_standards(params)
        ld = LDCarriers(params.hsync())
        audio = ld.audioNTSC()
        efm = ld.efm()
        carriers = { audio['L'], audio['R'], audio['AC3'], efm['L'], efm['H'] }
        carrier_hist = { audio['L']: 0, audio['R']: 0, audio['AC3']: 0, efm['L']: 0, efm['H']: 0 }
        print('Starting FFT analysis ... ')
        FFT_points = 256
        low_rate = nearest.power(params.samp_rate()/4, 2)
        #self_test(params, low_rate, FFT_points)

        fft = FFT(FFT_points, low_rate)

        m = params.samp_rate() / low_rate
        read_size = round(FFT_points * m)
        print('read size', read_size)
        skip = 32760
        res = ar(params.samp_rate())

        while skip > 0 and not self.exit:
            x = read_block16(read_size)
            xl = res.autorational_downsample(x, low_rate)
            xn = fft.removeDC(xl)
            yf = fft.do(xn)
            self.queue.put_nowait(fft.plot(yf))
            foo, bar, peaks = fft.peaks(yf)
            #print(peaks)
            carrier_hist = fft.carrier_hist(carriers, peaks, 1, carrier_hist)
            skip -= 1
        print(carrier_hist)
        print('Reading thread ended')


if __name__ == '__main__':
    app = QApplication([])
    t = Main()
    t.daemon = True
    t.start()
    app.exec()
    t.end()
    t.join()
