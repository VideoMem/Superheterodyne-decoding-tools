import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from scipy import signal
import scipy.fftpack as FFT
from standards import LDCarriers
import nearest

class FFTtools:

    def __init__(self, FFTsize, samp_rate):
        self.FFTpoints = nearest.power(FFTsize, 2)
        self.T = 1/samp_rate
        self.samp_rate = samp_rate
        self.nyquist = int(samp_rate/2)
        self.savg = list()
        self.scount = 0


    def removeDC(self, x):
        mean = sum(x) / len(x)
        return [n - mean for n in x]

    def test_signal(self, hsync):
        ld = LDCarriers(hsync)
        audio = ld.audioNTSC()
        x = np.linspace(0.0, self.FFTpoints * self.T, self.FFTpoints)
        y = 0.5 * np.sin(audio['L'] * 2.0 * np.pi * x) + 0.5 * np.sin(audio['R'] * 2.0 * np.pi * x)
        return y

    # it averages the spectra from n FFTs and returns the average spectra
    def stack(self, x, n):
        length = len(self.savg)
        if length == 0:
            self.savg = list(x)
        else:
            i = 0
            for sample in x:
                self.savg[i] += sample
                i += 1

        self.scount += 1

        if self.scount >= n:
            xn = self.savg.copy()
            #xn = [sample / self.scount for sample in self.savg]
            self.scount = 0
            self.savg.clear()
            return True, xn
        else:
            return False, 0

    def do(self, y):
        fy = y[:self.FFTpoints]
        w = signal.windows.kaiser(self.FFTpoints, 14)
        fft = FFT.fft(np.multiply(fy, w))
        #fft = FFT.fft(fy, self.FFTpoints)
        dB = 10 * np.log10(np.abs(fft[:self.FFTpoints]/self.FFTpoints))
        return dB

    def in_range(self, x, ref, error):
        upper = (100 + error) / 100
        lower = (100 - error) / 100
        ref_up = ref * upper
        ref_dw = ref * lower
        if ref_dw <= x <= ref_up:
            return True
        else:
            return False

    def carrier_hist(self, carriers, peaks, error, last_hist):
        for carrier in carriers:
            for peak in peaks:
                if self.in_range(peak, carrier, error):
                    last_hist[carrier] += 1
        return last_hist

    def peaks(self, yf):
        xf = np.linspace(0.0, self.nyquist, int(self.FFTpoints / 2))
        yn = 2.0 / self.FFTpoints * yf[:self.FFTpoints // 2]
        peakind = signal.find_peaks_cwt(yn, np.arange(1, 10))
        peaks = list()
        for ind in peakind:
            peaks.append(xf[ind])
        return xf, yn, peaks

    def plot(self, yf):
        x, y, peaks = self.peaks(yf)
        fig, ax = plt.subplots()
        ax.plot(x, y)
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        s, (width, height) = canvas.print_to_buffer()
        X = np.fromstring(s, np.uint8).reshape((height, width, 4))
        plt.close('all')
        return X.tobytes(), width, height

