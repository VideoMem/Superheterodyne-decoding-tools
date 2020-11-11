from parameters import Parameters
from standards import LDCarriers

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
    ld = LDCarriers(p.hsync)
    audio = ld.audio()
    print('expected analogue left carrier frequency: %.7f MHz' % toMHz(audio['L']))
    print('expected analogue right carrier frequency: %.7f MHz' % toMHz(audio['R']))
    print('expected AC3 QPSK carrier frequency: %.7f MHz' % toMHz(audio['AC3']))

def main():
    params = Parameters()
    print_parameters(params)
    print_standards(params)
    print('Starting FFT analysis ... ')


if __name__ == '__main__':
    main()
