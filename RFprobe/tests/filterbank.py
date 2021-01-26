import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from math import pow, log10
import nearest

# 0 quiet, 1 info, 3 debug
def LOGLEVEL():
    return 2


def LOG(level, txt):
    if level < LOGLEVEL():
        print(txt)


# signal processing specs
class SSpecs:
    def __init__(self, samp_rate=40e6):  # 40MSPS default
        self.s_rate = samp_rate
        #self.fsm = round(samp_rate / self.ratio()) #pow(2, 23)  # 8388608 Hz
        self.fsm = nearest.power(2, samp_rate / self.ratio())  # 8388608 Hz

    def ratio(self):
        return 5

    def samp_rate(self):
        return self.s_rate

    def fs(self):
        return self.fsm

    def nyq(self):
        return self.fsm / 2


# LaserDisc audio spec skeleton class
class LaserDisc:
    def type(self):
        return 'LaserDisc'

    def lines(self):
        return 0

    def vF(self):
        return 0

    # horizontal frequency (Hz)
    def hF(self):
        return self.vF() * self.lines() / 2

    # maximum FM audio deviation (Hz)
    def audio_VCO_deviation(self):
        return 300e3

    def half_audio_VCO_deviation(self):
        return self.audio_VCO_deviation() / 2

    # expected normal FM audio deviation (Hz)
    def op_audio_VCO_deviation(self):
        return 100e3

    # DC offset removal HPF (Hz), third harmonic of the rotation frequency
    def FM_HPF(self):
        return self.vF() * 3

    # filter transition width (Hz)
    def sharpness(self):
        return 150e3


# LaserDisc PAL specs
class LD_PAL(LaserDisc):
    def standard(self):
        return 'PAL'

    def lines(self):
        return 625

    def vF(self):
        return 50

    def filterbank(self):
        return {
            'L': {'type': 'BPF', 'fc': 61.849984 * self.hF(), 'transition': self.sharpness()},
            'R': {'type': 'BPF', 'fc': 165.12 * self.hF(), 'transition': self.sharpness()}
        }


# LaserDisc NTSC specs
class LD_NTSC(LaserDisc):
    def standard(self):
        return 'NTSC'

    def lines(self):
        return 525

    def vF(self):
        return 60

    def filterbank(self):
        return {
            'L': {'type': 'BPF', 'fc': 146.25 * self.hF(), 'transition': self.sharpness()},
            'R': {'type': 'BPF', 'fc': 178.75 * self.hF(), 'transition': self.sharpness()},
            'AC3': {'type': 'BPF', 'fc': 182.857 * self.hF(), 'transition': self.sharpness()}
        }


# CD audio
class EFM_CDA(LaserDisc):
    def type(self):
        return 'Compact Disc'

    def standard(self):
        return 'EFM'

    def filterbank(self):
        return {
            'EFM': {'type': 'LPF', 'fc': 1.75e6, 'transition': 10 * self.sharpness()}
        }


class FilterStack(list):
    def name(self):
        n = 1
        for f in self.copy():
            LOG(2, 'Filter bank number %.2d:' % n)
            LOG(2, (f.type(), f.standard()))
            LOG(2, f.filterbank())
            n += 1


class FilterBank:
    def __init__(self, filterStack):
        self.stack = filterStack
        self.filters = list()
        self.LD = LaserDisc()

    # calculates the passband frequencies
    def passband(self, filt):
        return filt['fc'] - self.LD.half_audio_VCO_deviation(), filt['fc'] + self.LD.half_audio_VCO_deviation()

    # calculates the stopband frequencies
    def stopband(self, filt):
        passb = self.passband(filt)
        return passb[0] - filt['transition'], passb[1] + filt['transition']

    def get_bands(self, filt):
        return self.passband(filt), self.stopband(filt)

    # plots the frequency response of the filter
    def plot(self, sample_specs, iir_b, iir_a, title, type):
        w, h = signal.freqz(iir_b, iir_a, worN=np.logspace(0, log10(sample_specs.nyq()), 10000), fs=sample_specs.fs())
        fig = plt.figure()
        plt.semilogx(w, 20 * np.log10(abs(h)))
        ax1 = fig.add_subplot()
        plt.ylim([-42, 3])
        plt.xlim([800e3, sample_specs.nyq()])
        plt.title('Butterworth IIR %s fit to\n%s' % (type, title))
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Amplitude [dB]')
        plt.grid(which='both', axis='both')
        ax2 = ax1.twinx()
        angles = np.unwrap(np.angle(h))
        plt.plot(w, angles, 'g')
        plt.ylabel('Angle [degrees]', color='g')
        plt.show()


class IIR_FilterBank(FilterBank):

    def get_bandpass_params(self, filt, sample_specs):
        passband, stopband = self.get_bands(filt)
        max_loss_passband = 3  # The maximum loss allowed in the passband
        min_loss_stopband = 30  # The minimum loss allowed in the stopband
        order, normal_cutoff = signal.buttord(passband, stopband, max_loss_passband,
                                              min_loss_stopband, sample_specs.fs())
        return passband, stopband, order, normal_cutoff

    def get_bandpass(self, filt, sample_specs, identifier):
        passband, stopband, order, normal_cutoff = self.get_bandpass_params(filt, sample_specs)
        iir_b, iir_a = signal.butter(order, normal_cutoff, btype="bandpass", fs=sample_specs.fs())
        LOG(1, '-> BandPass from %s, stopband %s, Butterworth order: %d' % (passband, stopband, order))
        if LOGLEVEL() > 2:
            self.plot(sample_specs, iir_b, iir_a, identifier, 'bandpass')
        return { 'iir_b':iir_b, 'iir_a':iir_a }

    def get_lowpass_params(self, filt, sample_specs):
        passband, stopband = self.get_bands(filt)
        max_loss_passband = 3  # The maximum loss allowed in the passband
        min_loss_stopband = 30  # The minimum loss allowed in the stopband
        order, normal_cutoff = signal.buttord(passband[1], stopband[1], max_loss_passband,
                                              min_loss_stopband, sample_specs.fs())
        return passband, stopband, order, normal_cutoff

    def get_lowpass(self, filt, sample_specs, identifier):
        passband, stopband, order, normal_cutoff = self.get_lowpass_params(filt, sample_specs)
        iir_b, iir_a = signal.butter(order, normal_cutoff, btype="lowpass", fs=sample_specs.fs())
        LOG(1, '-> LowPass from %s, stopband %s, Butterworth order: %d' % (passband, stopband, order))
        if LOGLEVEL() > 2:
            self.plot(sample_specs, iir_b, iir_a, identifier, 'lowpass')
        return { 'iir_b':iir_b, 'iir_a':iir_a }

    def channel_count(self):
        channel_count = 0
        for group in self.stack:
            for channel, filt in group.filterbank().items():
                channel_count += 1
        return channel_count

    def design(self, sample_specs):
        LOG(1, 'Designing IIR filter bank ...')
        for group in self.stack:
            for channel, filt in group.filterbank().items():
                identifier = '%s %s, %s channel filter @ %.2f Hz' % (group.type(), group.standard(), channel, filt['fc'])
                LOG(1, 'Preparing %s' % identifier)

                if filt['type'] == 'BPF':
                    iir = self.get_bandpass(filt, sample_specs, identifier)
                elif filt['type'] == 'LPF':
                    iir = self.get_lowpass(filt, sample_specs, identifier)
                else:
                    iir = None

                self.filters.append(
                    {
                        'filter': filt,
                        'identifier': identifier,
                        'sample_specs': sample_specs,
                        'handler': iir
                    }
                )

        return self.filters


def filterbank():
    filters_parameters = FilterStack()
    PAL = LD_PAL()
    NTSC = LD_NTSC()
    CDA = EFM_CDA()
    sample_specs = SSpecs()

    filters_parameters.append(PAL)
    filters_parameters.append(NTSC)
    filters_parameters.append(CDA)

    filters_parameters.name()
    IIRbank = IIR_FilterBank(filters_parameters)
    filters = IIRbank.design(sample_specs)
    LOG(1, 'Got %d filters, for %d channels' % (len(filters), IIRbank.channel_count()))
    assert len(filters) == IIRbank.channel_count(), 'That\'s bad'
    LOG(2, filters)
    return filters

if __name__ == '__main__':
    filterbank()