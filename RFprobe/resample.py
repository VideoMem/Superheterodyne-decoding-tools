from scipy import signal
from fractions import Fraction


class Arbitrary:

    def __init__(self, samp_rate):
        self.rate = samp_rate

    # returns an approximated rational of a float
    def rationalize(self, float_scale, limit=1000):
        fraction = Fraction(float_scale).limit_denominator(limit)
        return fraction.numerator, fraction.denominator

    def rational_resample(self, data, n, d):
        upsize = len(data) * n
        downsize = round(upsize / d)
        upscaled = signal.resample(data, upsize)
        return signal.resample(upscaled, downsize)

    # finds the best fraction to down resample
    def autorational_downsample(self, data, newrate):
        n, d = self.rationalize(newrate / self.rate)
        return self.rational_resample(data, n, d)

    # finds the best fraction to up resample
    def autorational_upsample(self, data, rate):
        n, d = self.rationalize(rate / self.rate)
        return self.rational_resample(data, d, n)

