Based on:
https://web.archive.org/web/20141031003122/http://www1.tek.com/Measurement/cgi-bin/framed.pl?Document=%2FMeasurement%2FApp_Notes%2FNTSC_Video_Msmt%2Fvideotesting2.html


```

$ python3 multiburst_generator.py --help

usage: multiburst_generator.py [-h] [-l [LINES]] [-s [SCALE]] [-d [DEVICE]]
                               [-c [COLOR]] [-a [ASPECT]] [-w [WHITE]]
                               [-b [BLACK]] [-o [OUTPUT]]

Generates multiburst testing charts for video bandwidth testing

optional arguments:
  -h, --help            show this help message and exit
  -l [LINES], --lines [LINES]
                        lines per frame (default 525)
  -s [SCALE], --scale [SCALE]
                        scale of the output image (default 1)
  -d [DEVICE], --device [DEVICE]
                        target device -> 0: VTR, 1: CRT monitor (default 0)
  -c [COLOR], --color [COLOR]
                        color pattern -> 0: grayscale, 1: red, 2: blue
                        (default 0)
  -a [ASPECT], --aspect [ASPECT]
                        aspect ratio (default 1.333333 [4:3])
  -w [WHITE], --white [WHITE]
                        white clip level (default 70 IRE)
  -b [BLACK], --black [BLACK]
                        black clip level (default 10 IRE)
  -o [OUTPUT], --output [OUTPUT]
                        write to file (default, None)
```