#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: VTR Luma decoder
# Author: VideoMem
# Copyright: ( ͡° ͜ʖ ͡°)
# GNU Radio version: 3.8.1.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from fractions import Fraction
from gnuradio import analog
import math
from gnuradio import blocks
import pmt
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import video_sdl
from gnuradio.qtgui import Range, RangeWidget
from string import Formatter
import nearest  # embedded python module
import time
import threading

from gnuradio import qtgui

class vtr(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "VTR Luma decoder")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("VTR Luma decoder")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "vtr")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.in_rate = in_rate = 35812500
        self.Fh = Fh = 15.625e3
        self.samples_per_line = samples_per_line = in_rate/Fh
        self.interpolator = interpolator = 2
        self.samp_rate = samp_rate = in_rate*interpolator
        self.luma_fm_carrier = luma_fm_carrier = Fh * (284-1/4) + Fh/625
        self.lines_per_frame = lines_per_frame = 625
        self.if_lo_reference_fc = if_lo_reference_fc = 40*Fh+(Fh/8)
        self.disp_width = disp_width = nearest.power(samples_per_line,2)/2
        self.chroma_fine = chroma_fine = 0
        self.chroma_coarse = chroma_coarse = 0
        self.vco_deviation = vco_deviation = 1e6
        self.sharpener = sharpener = 0.06
        self.one_line_samples = one_line_samples = nearest.power(samp_rate/Fh,2)
        self.luma_min_probe = luma_min_probe = 0
        self.luma_fm_carrier_filter_peak = luma_fm_carrier_filter_peak = 5.4886e6
        self.lines_per_field = lines_per_field = lines_per_frame/2
        self.line_average = line_average = 2
        self.fh_comb_delay = fh_comb_delay = samp_rate/(Fh*8)
        self.display_scale = display_scale = samples_per_line / disp_width
        self.disp_height = disp_height = lines_per_frame
        self.contrast = contrast = 3
        self.comb_gain = comb_gain = 0.1
        self.comb_delay = comb_delay = samp_rate/(luma_fm_carrier*4)
        self.chroma_adjusted = chroma_adjusted = if_lo_reference_fc+chroma_fine+chroma_coarse
        self.brightness = brightness = 0.4
        self.auto_luma_gain = auto_luma_gain = 0.1
        self.audio_rate = audio_rate = round(48e3*4)
        self.Fv = Fv = 60
        self.Fcc_Fcl = Fcc_Fcl = 455/80

        ##################################################
        # Blocks
        ##################################################
        self.tabs = Qt.QTabWidget()
        self.tabs_widget_0 = Qt.QWidget()
        self.tabs_layout_0 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_0)
        self.tabs_grid_layout_0 = Qt.QGridLayout()
        self.tabs_layout_0.addLayout(self.tabs_grid_layout_0)
        self.tabs.addTab(self.tabs_widget_0, 'Main Y')
        self.tabs_widget_1 = Qt.QWidget()
        self.tabs_layout_1 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_1)
        self.tabs_grid_layout_1 = Qt.QGridLayout()
        self.tabs_layout_1.addLayout(self.tabs_grid_layout_1)
        self.tabs.addTab(self.tabs_widget_1, 'Chroma Controls')
        self.tabs_widget_2 = Qt.QWidget()
        self.tabs_layout_2 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_2)
        self.tabs_grid_layout_2 = Qt.QGridLayout()
        self.tabs_layout_2.addLayout(self.tabs_grid_layout_2)
        self.tabs.addTab(self.tabs_widget_2, 'Output')
        self.top_grid_layout.addWidget(self.tabs)
        self.luma_min = blocks.probe_signal_f()
        self.luma_gain_signal = blocks.probe_signal_f()
        self._sharpener_range = Range(0, 0.2, 0.001, 0.06, 200)
        self._sharpener_win = RangeWidget(self._sharpener_range, self.set_sharpener, 'Sharpness', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._sharpener_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        def _luma_min_probe_probe():
            while True:

                val = self.luma_min.level()
                try:
                    self.set_luma_min_probe(val)
                except AttributeError:
                    pass
                time.sleep(1.0 / (audio_rate))
        _luma_min_probe_thread = threading.Thread(target=_luma_min_probe_probe)
        _luma_min_probe_thread.daemon = True
        _luma_min_probe_thread.start()

        self._contrast_range = Range(0, 6, 0.1, 3, 200)
        self._contrast_win = RangeWidget(self._contrast_range, self.set_contrast, 'Contrast bias', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._contrast_win, 4, 0, 1, 1)
        for r in range(4, 5):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self._comb_gain_range = Range(0, 0.2, 0.001, 0.1, 200)
        self._comb_gain_win = RangeWidget(self._comb_gain_range, self.set_comb_gain, 'Comb gain', "counter_slider", float)
        self.tabs_layout_2.addWidget(self._comb_gain_win)
        self._comb_delay_range = Range(0, samp_rate/luma_fm_carrier, 1, samp_rate/(luma_fm_carrier*4), 200)
        self._comb_delay_win = RangeWidget(self._comb_delay_range, self.set_comb_delay, 'Comb filter delay', "counter_slider", float)
        self.tabs_layout_2.addWidget(self._comb_delay_win)
        self._brightness_range = Range(-2, 2, 0.1, 0.4, 200)
        self._brightness_win = RangeWidget(self._brightness_range, self.set_brightness, 'Brightness bias', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._brightness_win, 5, 0, 1, 1)
        for r in range(5, 6):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        def _auto_luma_gain_probe():
            while True:

                val = self.luma_gain_signal.level()
                try:
                    self.set_auto_luma_gain(val)
                except AttributeError:
                    pass
                time.sleep(1.0 / (audio_rate))
        _auto_luma_gain_thread = threading.Thread(target=_auto_luma_gain_probe)
        _auto_luma_gain_thread.daemon = True
        _auto_luma_gain_thread.start()

        self.video_sdl_sink_0 = video_sdl.sink_uc(Fv/2, round(disp_width), round(disp_height), 0, round(disp_width), round(disp_height))
        self.rational_resampler_xxx_3 = filter.rational_resampler_fff(
                interpolation=Fraction(in_rate/samp_rate).limit_denominator(1000).numerator,
                decimation=Fraction(in_rate/samp_rate).limit_denominator(1000).denominator,
                taps=None,
                fractional_bw=None)
        self.rational_resampler_xxx_2 = filter.rational_resampler_fff(
                interpolation=Fraction(display_scale).limit_denominator(1000).denominator,
                decimation=Fraction(display_scale).limit_denominator(1000).numerator,
                taps=None,
                fractional_bw=None)
        self.rational_resampler_xxx_1_0 = filter.rational_resampler_fff(
                interpolation=Fraction(audio_rate/samp_rate).limit_denominator(1000).denominator,
                decimation=Fraction(audio_rate/samp_rate).limit_denominator(1000).numerator,
                taps=None,
                fractional_bw=None)
        self.rational_resampler_xxx_1 = filter.rational_resampler_fff(
                interpolation=Fraction(audio_rate/samp_rate).limit_denominator(1000).numerator,
                decimation=Fraction(audio_rate/samp_rate).limit_denominator(1000).denominator,
                taps=None,
                fractional_bw=None)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=interpolator,
                decimation=1,
                taps=None,
                fractional_bw=None)
        self.qtgui_time_sink_x_2_2 = qtgui.time_sink_f(
            round(2*samp_rate/Fh), #size
            samp_rate, #samp_rate
            "Luma AWB", #name
            4 #number of inputs
        )
        self.qtgui_time_sink_x_2_2.set_update_time(0.10)
        self.qtgui_time_sink_x_2_2.set_y_axis(-0.41, 1.1)

        self.qtgui_time_sink_x_2_2.set_y_label('IRE/100', "")

        self.qtgui_time_sink_x_2_2.enable_tags(False)
        self.qtgui_time_sink_x_2_2.set_trigger_mode(qtgui.TRIG_MODE_AUTO, qtgui.TRIG_SLOPE_POS, 0.85, 0, 0, "")
        self.qtgui_time_sink_x_2_2.enable_autoscale(False)
        self.qtgui_time_sink_x_2_2.enable_grid(False)
        self.qtgui_time_sink_x_2_2.enable_axis_labels(True)
        self.qtgui_time_sink_x_2_2.enable_control_panel(True)
        self.qtgui_time_sink_x_2_2.enable_stem_plot(False)

        self.qtgui_time_sink_x_2_2.disable_legend()

        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'cyan', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 2, 2, 4, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(4):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_2_2.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_2_2.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_2_2.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_2_2.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_2_2.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_2_2.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_2_2.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_2_2_win = sip.wrapinstance(self.qtgui_time_sink_x_2_2.pyqwidget(), Qt.QWidget)
        self.tabs_grid_layout_0.addWidget(self._qtgui_time_sink_x_2_2_win, 3, 0, 1, 1)
        for r in range(3, 4):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self.qtgui_number_sink_1 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1
        )
        self.qtgui_number_sink_1.set_update_time(0.10)
        self.qtgui_number_sink_1.set_title('')

        labels = ['Y AWB', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_1.set_min(i, 0)
            self.qtgui_number_sink_1.set_max(i, 2)
            self.qtgui_number_sink_1.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_1.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_1.set_label(i, labels[i])
            self.qtgui_number_sink_1.set_unit(i, units[i])
            self.qtgui_number_sink_1.set_factor(i, factor[i])

        self.qtgui_number_sink_1.enable_autoscale(False)
        self._qtgui_number_sink_1_win = sip.wrapinstance(self.qtgui_number_sink_1.pyqwidget(), Qt.QWidget)
        self.tabs_grid_layout_0.addWidget(self._qtgui_number_sink_1_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self.qtgui_number_sink_0 = qtgui.number_sink(
            gr.sizeof_float,
            1,
            qtgui.NUM_GRAPH_HORIZ,
            1
        )
        self.qtgui_number_sink_0.set_update_time(0.05)
        self.qtgui_number_sink_0.set_title('')

        labels = ['Input Volts', '', '', '', '',
            '', '', '', '', '']
        units = ['Vpp', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0.set_min(i, 0)
            self.qtgui_number_sink_0.set_max(i, 1)
            self.qtgui_number_sink_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0.set_label(i, labels[i])
            self.qtgui_number_sink_0.set_unit(i, units[i])
            self.qtgui_number_sink_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0.enable_autoscale(False)
        self._qtgui_number_sink_0_win = sip.wrapinstance(self.qtgui_number_sink_0.pyqwidget(), Qt.QWidget)
        self.tabs_grid_layout_0.addWidget(self._qtgui_number_sink_0_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0_0_1 = qtgui.freq_sink_c(
            2048, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "Luma band", #name
            1
        )
        self.qtgui_freq_sink_x_0_0_1.set_update_time(0.10)
        self.qtgui_freq_sink_x_0_0_1.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0_0_1.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0_1.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0_1.enable_grid(False)
        self.qtgui_freq_sink_x_0_0_1.set_fft_average(0.05)
        self.qtgui_freq_sink_x_0_0_1.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0_1.enable_control_panel(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_0_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0_1.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0_1.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0_1.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_1_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0_1.pyqwidget(), Qt.QWidget)
        self.tabs_layout_1.addWidget(self._qtgui_freq_sink_x_0_0_1_win)
        self.qtgui_freq_sink_x_0_0_0 = qtgui.freq_sink_f(
            2048, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "Y demodulated", #name
            1
        )
        self.qtgui_freq_sink_x_0_0_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0_0_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0_0.enable_grid(False)
        self.qtgui_freq_sink_x_0_0_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0_0.enable_control_panel(False)


        self.qtgui_freq_sink_x_0_0_0.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0_0.pyqwidget(), Qt.QWidget)
        self.tabs_layout_2.addWidget(self._qtgui_freq_sink_x_0_0_0_win)
        self.luma_max = blocks.probe_signal_f()
        self.low_pass_filter_3 = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                1,
                audio_rate,
                Fh*3,
                10e3,
                firdes.WIN_HAMMING,
                6.76))
        self.low_pass_filter_2_0 = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                sharpener,
                samp_rate,
                luma_fm_carrier-100e3,
                100e3,
                firdes.WIN_HAMMING,
                6.76))
        self.low_pass_filter_2 = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                luma_fm_carrier-100e3,
                100e3,
                firdes.WIN_HAMMING,
                6.76))
        self.low_pass_filter_1 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                8e6,
                8e6-luma_fm_carrier_filter_peak,
                firdes.WIN_HAMMING,
                6.76))
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                0.2,
                samp_rate,
                200e3,
                chroma_adjusted - 375e3,
                firdes.WIN_HAMMING,
                6.76))
        self.high_pass_filter_2 = filter.fir_filter_fff(
            1,
            firdes.high_pass(
                comb_gain,
                samp_rate,
                luma_fm_carrier,
                1e6,
                firdes.WIN_HAMMING,
                6.76))
        self.high_pass_filter_1 = filter.fir_filter_ccf(
            1,
            firdes.high_pass(
                1,
                samp_rate,
                chroma_adjusted,
                luma_fm_carrier_filter_peak-chroma_adjusted,
                firdes.WIN_HAMMING,
                6.76))
        self.high_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.high_pass(
                0.1,
                samp_rate,
                10e6,
                2e6,
                firdes.WIN_HAMMING,
                6.76))
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, [1], luma_fm_carrier, samp_rate)
        self.dc_blocker_xx_0 = filter.dc_blocker_ff(round(samp_rate/100), True)
        self._chroma_fine_range = Range(-1, 1, 0.0001, 0, 200)
        self._chroma_fine_win = RangeWidget(self._chroma_fine_range, self.set_chroma_fine, 'Fine', "counter_slider", float)
        self.tabs_grid_layout_1.addWidget(self._chroma_fine_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.tabs_grid_layout_1.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_1.setColumnStretch(c, 1)
        self._chroma_coarse_range = Range(-5e3, 1e3, 1, 0, 200)
        self._chroma_coarse_win = RangeWidget(self._chroma_coarse_range, self.set_chroma_coarse, 'C Coarse', "counter_slider", float)
        self.tabs_grid_layout_1.addWidget(self._chroma_coarse_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_1.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_1.setColumnStretch(c, 1)
        self.blocks_uchar_to_float_0 = blocks.uchar_to_float()
        self.blocks_sub_xx_2 = blocks.sub_ff(1)
        self.blocks_stream_to_vector_1_0 = blocks.stream_to_vector(gr.sizeof_float*1, one_line_samples*line_average)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_float*1, one_line_samples*line_average)
        self.blocks_multiply_const_vxx_7_0 = blocks.multiply_const_ff(255)
        self.blocks_multiply_const_vxx_6 = blocks.multiply_const_ff(auto_luma_gain)
        self.blocks_multiply_const_vxx_2 = blocks.multiply_const_ff(2/255)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff(1/1.4)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(10)
        self.blocks_moving_average_xx_0_1 = blocks.moving_average_ff(line_average*100, 1/(line_average*100), 4000, 1)
        self.blocks_moving_average_xx_0_0 = blocks.moving_average_ff(line_average*100, 1/(line_average*100), 100, 1)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(line_average*100, 1/(line_average*100), 4000, 1)
        self.blocks_min_xx_0 = blocks.min_ff(one_line_samples*line_average,1)
        self.blocks_max_xx_0 = blocks.max_ff(one_line_samples*line_average, 1)
        self.blocks_float_to_uchar_0_0 = blocks.float_to_uchar()
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, '/home/sebastian/Downloads/VTR/vhs_pal_multiburst_cropped/vhs_pal_sp_multiburst.r8', False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_divide_xx_0 = blocks.divide_ff(1)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_float*1, round(comb_delay))
        self.blocks_add_xx_2_0 = blocks.add_vff(1)
        self.blocks_add_xx_2 = blocks.add_vff(1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.blocks_add_const_vxx_3 = blocks.add_const_ff(-64)
        self.blocks_add_const_vxx_2 = blocks.add_const_ff(0.4)
        self.blocks_add_const_vxx_1 = blocks.add_const_ff(contrast)
        self.blocks_add_const_vxx_0 = blocks.add_const_ff(-(luma_min_probe+brightness))
        self.blocks_abs_xx_0 = blocks.abs_ff(1)
        self.band_reject_filter_0 = filter.fir_filter_fff(
            1,
            firdes.band_reject(
                1,
                samp_rate,
                luma_fm_carrier - 100e3,
                luma_fm_carrier + 100e3,
                100e3,
                firdes.WIN_HAMMING,
                6.76))
        self.analog_rail_ff_0_0 = analog.rail_ff(0.01, 10)
        self.analog_rail_ff_0 = analog.rail_ff(-0.4, 1)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(samp_rate/(2*math.pi*vco_deviation/8.0))
        self.analog_fm_preemph_0 = analog.fm_preemph(fs=samp_rate, tau=1.25e-6, fh=-1.0)
        self.analog_fm_deemph_0_0 = analog.fm_deemph(fs=samp_rate, tau=1.25e-6)
        self.analog_const_source_x_2 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 1)
        self.analog_const_source_x_1_0_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)
        self.analog_const_source_x_1_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0.1)
        self.analog_const_source_x_1 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0.7)
        self.analog_agc2_xx_0 = analog.agc2_cc(10/Fh, 10/Fh, 1, 1)
        self.analog_agc2_xx_0.set_max_gain(65536)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_agc2_xx_0, 0), (self.high_pass_filter_0, 0))
        self.connect((self.analog_agc2_xx_0, 0), (self.high_pass_filter_1, 0))
        self.connect((self.analog_agc2_xx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.analog_const_source_x_1, 0), (self.qtgui_time_sink_x_2_2, 1))
        self.connect((self.analog_const_source_x_1_0, 0), (self.qtgui_time_sink_x_2_2, 2))
        self.connect((self.analog_const_source_x_1_0_0, 0), (self.qtgui_time_sink_x_2_2, 3))
        self.connect((self.analog_const_source_x_2, 0), (self.blocks_divide_xx_0, 0))
        self.connect((self.analog_fm_deemph_0_0, 0), (self.blocks_add_xx_2, 0))
        self.connect((self.analog_fm_deemph_0_0, 0), (self.high_pass_filter_2, 0))
        self.connect((self.analog_fm_preemph_0, 0), (self.low_pass_filter_2_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.analog_fm_deemph_0_0, 0))
        self.connect((self.analog_rail_ff_0, 0), (self.blocks_add_const_vxx_2, 0))
        self.connect((self.analog_rail_ff_0, 0), (self.qtgui_time_sink_x_2_2, 0))
        self.connect((self.analog_rail_ff_0_0, 0), (self.luma_gain_signal, 0))
        self.connect((self.band_reject_filter_0, 0), (self.blocks_add_xx_2_0, 0))
        self.connect((self.blocks_abs_xx_0, 0), (self.blocks_moving_average_xx_0_1, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_multiply_const_vxx_6, 0))
        self.connect((self.blocks_add_const_vxx_1, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.blocks_add_const_vxx_2, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_add_const_vxx_3, 0), (self.blocks_multiply_const_vxx_2, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_freq_sink_x_0_0_1, 0))
        self.connect((self.blocks_add_xx_2, 0), (self.analog_fm_preemph_0, 0))
        self.connect((self.blocks_add_xx_2, 0), (self.band_reject_filter_0, 0))
        self.connect((self.blocks_add_xx_2_0, 0), (self.low_pass_filter_2, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_add_xx_2, 1))
        self.connect((self.blocks_divide_xx_0, 0), (self.analog_rail_ff_0_0, 0))
        self.connect((self.blocks_divide_xx_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_uchar_to_float_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.analog_agc2_xx_0, 0))
        self.connect((self.blocks_float_to_uchar_0_0, 0), (self.video_sdl_sink_0, 0))
        self.connect((self.blocks_max_xx_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_min_xx_0, 0), (self.blocks_moving_average_xx_0_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_sub_xx_2, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.luma_max, 0))
        self.connect((self.blocks_moving_average_xx_0_0, 0), (self.blocks_sub_xx_2, 1))
        self.connect((self.blocks_moving_average_xx_0_0, 0), (self.luma_min, 0))
        self.connect((self.blocks_moving_average_xx_0_1, 0), (self.qtgui_number_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_number_sink_1, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.rational_resampler_xxx_3, 0))
        self.connect((self.blocks_multiply_const_vxx_2, 0), (self.blocks_abs_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_6, 0), (self.analog_rail_ff_0, 0))
        self.connect((self.blocks_multiply_const_vxx_7_0, 0), (self.rational_resampler_xxx_2, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.blocks_max_xx_0, 0))
        self.connect((self.blocks_stream_to_vector_1_0, 0), (self.blocks_min_xx_0, 0))
        self.connect((self.blocks_sub_xx_2, 0), (self.blocks_divide_xx_0, 1))
        self.connect((self.blocks_uchar_to_float_0, 0), (self.dc_blocker_xx_0, 0))
        self.connect((self.dc_blocker_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.high_pass_filter_0, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.high_pass_filter_1, 0), (self.low_pass_filter_1, 0))
        self.connect((self.high_pass_filter_2, 0), (self.blocks_delay_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.low_pass_filter_1, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.low_pass_filter_2, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.low_pass_filter_2, 0), (self.qtgui_freq_sink_x_0_0_0, 0))
        self.connect((self.low_pass_filter_2, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.low_pass_filter_2_0, 0), (self.blocks_add_xx_2_0, 1))
        self.connect((self.low_pass_filter_3, 0), (self.rational_resampler_xxx_1_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_add_const_vxx_3, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.low_pass_filter_3, 0))
        self.connect((self.rational_resampler_xxx_1_0, 0), (self.blocks_add_const_vxx_1, 0))
        self.connect((self.rational_resampler_xxx_1_0, 0), (self.blocks_stream_to_vector_1_0, 0))
        self.connect((self.rational_resampler_xxx_2, 0), (self.blocks_float_to_uchar_0_0, 0))
        self.connect((self.rational_resampler_xxx_3, 0), (self.blocks_multiply_const_vxx_7_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "vtr")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_in_rate(self):
        return self.in_rate

    def set_in_rate(self, in_rate):
        self.in_rate = in_rate
        self.set_samp_rate(self.in_rate*self.interpolator)
        self.set_samples_per_line(self.in_rate/self.Fh)

    def get_Fh(self):
        return self.Fh

    def set_Fh(self, Fh):
        self.Fh = Fh
        self.set_fh_comb_delay(self.samp_rate/(self.Fh*8))
        self.set_if_lo_reference_fc(40*self.Fh+(self.Fh/8))
        self.set_luma_fm_carrier(self.Fh * (284-1/4) + self.Fh/625)
        self.set_one_line_samples(nearest.power(self.samp_rate/self.Fh,2))
        self.set_samples_per_line(self.in_rate/self.Fh)
        self.analog_agc2_xx_0.set_attack_rate(10/self.Fh)
        self.analog_agc2_xx_0.set_decay_rate(10/self.Fh)
        self.low_pass_filter_3.set_taps(firdes.low_pass(1, self.audio_rate, self.Fh*3, 10e3, firdes.WIN_HAMMING, 6.76))

    def get_samples_per_line(self):
        return self.samples_per_line

    def set_samples_per_line(self, samples_per_line):
        self.samples_per_line = samples_per_line
        self.set_disp_width(nearest.power(self.samples_per_line,2)/2)
        self.set_display_scale(self.samples_per_line / self.disp_width)

    def get_interpolator(self):
        return self.interpolator

    def set_interpolator(self, interpolator):
        self.interpolator = interpolator
        self.set_samp_rate(self.in_rate*self.interpolator)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_comb_delay(self.samp_rate/(self.luma_fm_carrier*4))
        self.set_fh_comb_delay(self.samp_rate/(self.Fh*8))
        self.set_one_line_samples(nearest.power(self.samp_rate/self.Fh,2))
        self.analog_quadrature_demod_cf_0.set_gain(self.samp_rate/(2*math.pi*self.vco_deviation/8.0))
        self.band_reject_filter_0.set_taps(firdes.band_reject(1, self.samp_rate, self.luma_fm_carrier - 100e3, self.luma_fm_carrier + 100e3, 100e3, firdes.WIN_HAMMING, 6.76))
        self.high_pass_filter_0.set_taps(firdes.high_pass(0.1, self.samp_rate, 10e6, 2e6, firdes.WIN_HAMMING, 6.76))
        self.high_pass_filter_1.set_taps(firdes.high_pass(1, self.samp_rate, self.chroma_adjusted, self.luma_fm_carrier_filter_peak-self.chroma_adjusted, firdes.WIN_HAMMING, 6.76))
        self.high_pass_filter_2.set_taps(firdes.high_pass(self.comb_gain, self.samp_rate, self.luma_fm_carrier, 1e6, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0.set_taps(firdes.low_pass(0.2, self.samp_rate, 200e3, self.chroma_adjusted - 375e3, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.samp_rate, 8e6, 8e6-self.luma_fm_carrier_filter_peak, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_2.set_taps(firdes.low_pass(1, self.samp_rate, self.luma_fm_carrier-100e3, 100e3, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_2_0.set_taps(firdes.low_pass(self.sharpener, self.samp_rate, self.luma_fm_carrier-100e3, 100e3, firdes.WIN_HAMMING, 6.76))
        self.qtgui_freq_sink_x_0_0_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_freq_sink_x_0_0_1.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_2_2.set_samp_rate(self.samp_rate)

    def get_luma_fm_carrier(self):
        return self.luma_fm_carrier

    def set_luma_fm_carrier(self, luma_fm_carrier):
        self.luma_fm_carrier = luma_fm_carrier
        self.set_comb_delay(self.samp_rate/(self.luma_fm_carrier*4))
        self.band_reject_filter_0.set_taps(firdes.band_reject(1, self.samp_rate, self.luma_fm_carrier - 100e3, self.luma_fm_carrier + 100e3, 100e3, firdes.WIN_HAMMING, 6.76))
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.luma_fm_carrier)
        self.high_pass_filter_2.set_taps(firdes.high_pass(self.comb_gain, self.samp_rate, self.luma_fm_carrier, 1e6, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_2.set_taps(firdes.low_pass(1, self.samp_rate, self.luma_fm_carrier-100e3, 100e3, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_2_0.set_taps(firdes.low_pass(self.sharpener, self.samp_rate, self.luma_fm_carrier-100e3, 100e3, firdes.WIN_HAMMING, 6.76))

    def get_lines_per_frame(self):
        return self.lines_per_frame

    def set_lines_per_frame(self, lines_per_frame):
        self.lines_per_frame = lines_per_frame
        self.set_disp_height(self.lines_per_frame)
        self.set_lines_per_field(self.lines_per_frame/2)

    def get_if_lo_reference_fc(self):
        return self.if_lo_reference_fc

    def set_if_lo_reference_fc(self, if_lo_reference_fc):
        self.if_lo_reference_fc = if_lo_reference_fc
        self.set_chroma_adjusted(self.if_lo_reference_fc+self.chroma_fine+self.chroma_coarse)

    def get_disp_width(self):
        return self.disp_width

    def set_disp_width(self, disp_width):
        self.disp_width = disp_width
        self.set_display_scale(self.samples_per_line / self.disp_width)

    def get_chroma_fine(self):
        return self.chroma_fine

    def set_chroma_fine(self, chroma_fine):
        self.chroma_fine = chroma_fine
        self.set_chroma_adjusted(self.if_lo_reference_fc+self.chroma_fine+self.chroma_coarse)

    def get_chroma_coarse(self):
        return self.chroma_coarse

    def set_chroma_coarse(self, chroma_coarse):
        self.chroma_coarse = chroma_coarse
        self.set_chroma_adjusted(self.if_lo_reference_fc+self.chroma_fine+self.chroma_coarse)

    def get_vco_deviation(self):
        return self.vco_deviation

    def set_vco_deviation(self, vco_deviation):
        self.vco_deviation = vco_deviation
        self.analog_quadrature_demod_cf_0.set_gain(self.samp_rate/(2*math.pi*self.vco_deviation/8.0))

    def get_sharpener(self):
        return self.sharpener

    def set_sharpener(self, sharpener):
        self.sharpener = sharpener
        self.low_pass_filter_2_0.set_taps(firdes.low_pass(self.sharpener, self.samp_rate, self.luma_fm_carrier-100e3, 100e3, firdes.WIN_HAMMING, 6.76))

    def get_one_line_samples(self):
        return self.one_line_samples

    def set_one_line_samples(self, one_line_samples):
        self.one_line_samples = one_line_samples

    def get_luma_min_probe(self):
        return self.luma_min_probe

    def set_luma_min_probe(self, luma_min_probe):
        self.luma_min_probe = luma_min_probe
        self.blocks_add_const_vxx_0.set_k(-(self.luma_min_probe+self.brightness))

    def get_luma_fm_carrier_filter_peak(self):
        return self.luma_fm_carrier_filter_peak

    def set_luma_fm_carrier_filter_peak(self, luma_fm_carrier_filter_peak):
        self.luma_fm_carrier_filter_peak = luma_fm_carrier_filter_peak
        self.high_pass_filter_1.set_taps(firdes.high_pass(1, self.samp_rate, self.chroma_adjusted, self.luma_fm_carrier_filter_peak-self.chroma_adjusted, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.samp_rate, 8e6, 8e6-self.luma_fm_carrier_filter_peak, firdes.WIN_HAMMING, 6.76))

    def get_lines_per_field(self):
        return self.lines_per_field

    def set_lines_per_field(self, lines_per_field):
        self.lines_per_field = lines_per_field

    def get_line_average(self):
        return self.line_average

    def set_line_average(self, line_average):
        self.line_average = line_average
        self.blocks_moving_average_xx_0.set_length_and_scale(self.line_average*100, 1/(self.line_average*100))
        self.blocks_moving_average_xx_0_0.set_length_and_scale(self.line_average*100, 1/(self.line_average*100))
        self.blocks_moving_average_xx_0_1.set_length_and_scale(self.line_average*100, 1/(self.line_average*100))

    def get_fh_comb_delay(self):
        return self.fh_comb_delay

    def set_fh_comb_delay(self, fh_comb_delay):
        self.fh_comb_delay = fh_comb_delay

    def get_display_scale(self):
        return self.display_scale

    def set_display_scale(self, display_scale):
        self.display_scale = display_scale

    def get_disp_height(self):
        return self.disp_height

    def set_disp_height(self, disp_height):
        self.disp_height = disp_height

    def get_contrast(self):
        return self.contrast

    def set_contrast(self, contrast):
        self.contrast = contrast
        self.blocks_add_const_vxx_1.set_k(self.contrast)

    def get_comb_gain(self):
        return self.comb_gain

    def set_comb_gain(self, comb_gain):
        self.comb_gain = comb_gain
        self.high_pass_filter_2.set_taps(firdes.high_pass(self.comb_gain, self.samp_rate, self.luma_fm_carrier, 1e6, firdes.WIN_HAMMING, 6.76))

    def get_comb_delay(self):
        return self.comb_delay

    def set_comb_delay(self, comb_delay):
        self.comb_delay = comb_delay
        self.blocks_delay_0.set_dly(round(self.comb_delay))

    def get_chroma_adjusted(self):
        return self.chroma_adjusted

    def set_chroma_adjusted(self, chroma_adjusted):
        self.chroma_adjusted = chroma_adjusted
        self.high_pass_filter_1.set_taps(firdes.high_pass(1, self.samp_rate, self.chroma_adjusted, self.luma_fm_carrier_filter_peak-self.chroma_adjusted, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0.set_taps(firdes.low_pass(0.2, self.samp_rate, 200e3, self.chroma_adjusted - 375e3, firdes.WIN_HAMMING, 6.76))

    def get_brightness(self):
        return self.brightness

    def set_brightness(self, brightness):
        self.brightness = brightness
        self.blocks_add_const_vxx_0.set_k(-(self.luma_min_probe+self.brightness))

    def get_auto_luma_gain(self):
        return self.auto_luma_gain

    def set_auto_luma_gain(self, auto_luma_gain):
        self.auto_luma_gain = auto_luma_gain
        self.blocks_multiply_const_vxx_6.set_k(self.auto_luma_gain)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.low_pass_filter_3.set_taps(firdes.low_pass(1, self.audio_rate, self.Fh*3, 10e3, firdes.WIN_HAMMING, 6.76))

    def get_Fv(self):
        return self.Fv

    def set_Fv(self, Fv):
        self.Fv = Fv

    def get_Fcc_Fcl(self):
        return self.Fcc_Fcl

    def set_Fcc_Fcl(self, Fcc_Fcl):
        self.Fcc_Fcl = Fcc_Fcl





def main(top_block_cls=vtr, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
