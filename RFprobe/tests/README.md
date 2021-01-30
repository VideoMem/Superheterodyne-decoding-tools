
## Test / Benchmark the parallel resample/filter
```
ld-ldf-reader file.ldf | python3 filterthread.py 
```

## Sample output
```
RATE:40000
DURATION:41240985600
Designing IIR filter bank ...
Preparing LaserDisc PAL, L channel filter @ 966406.00 Hz
-> BandPass from (816406.0, 1116406.0), stopband (666406.0, 1266406.0), Butterworth order: 6
Preparing LaserDisc PAL, R channel filter @ 2580000.00 Hz
-> BandPass from (2430000.0, 2730000.0), stopband (2280000.0, 2880000.0), Butterworth order: 6
Preparing LaserDisc NTSC, L channel filter @ 2303437.50 Hz
-> BandPass from (2153437.5, 2453437.5), stopband (2003437.5, 2603437.5), Butterworth order: 6
Preparing LaserDisc NTSC, R channel filter @ 2815312.50 Hz
-> BandPass from (2665312.5, 2965312.5), stopband (2515312.5, 3115312.5), Butterworth order: 6
Preparing LaserDisc NTSC, AC3 channel filter @ 2879997.75 Hz
-> BandPass from (2729997.75, 3029997.75), stopband (2579997.75, 3179997.75), Butterworth order: 6
Preparing Compact Disc EFM, EFM channel filter @ 1750000.00 Hz
-> LowPass from (1600000.0, 1900000.0), stopband (100000.0, 3400000.0), Butterworth order: 6
Got 6 filters, for 6 channels
+ DC remover -> HighPass from 180, stopband 90.0, Butterworth order: 2
-> Block 10, read 90.52 Mb/s
-> Block 20, read 109.36 Mb/s
-> Block 30, read 110.08 Mb/s
-> Block 40, read 116.45 Mb/s
-> Block 50, read 114.63 Mb/s
-> Block 60, read 117.60 Mb/s
-> Block 70, read 117.63 Mb/s
-> Block 80, read 118.61 Mb/s
-> Block 90, read 117.40 Mb/s
-> Block 100, read 118.96 Mb/s
-> Block 110, read 117.54 Mb/s

```