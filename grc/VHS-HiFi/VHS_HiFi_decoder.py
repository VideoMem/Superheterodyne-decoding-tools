#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: VHS HI-FI decoder
# Author: VideoMem
# Description: ( ͡° ͜ʖ ͡°)
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
from gnuradio.qtgui import Range, RangeWidget
import nearest  # embedded python module
import time
import threading

from gnuradio import qtgui

class VHS_HiFi_decoder(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "VHS HI-FI decoder")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("VHS HI-FI decoder")
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

        self.settings = Qt.QSettings("GNU Radio", "VHS_HiFi_decoder")

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
        self.carrier_distance = carrier_distance = 400e3
        self.R_carrier_ref = R_carrier_ref = 1.8e6
        self.pop_time = pop_time = 2e-3
        self.lines_per_frame = lines_per_frame = 624
        self.center_freq = center_freq = -4591.900
        self.carrierR_fine = carrierR_fine = 3603
        self.carrierL_fine = carrierL_fine = 0
        self.balance = balance = 0.48
        self.audio_rate = audio_rate = 192e3
        self.VCO_deviation = VCO_deviation = 300e3
        self.L_carrier_ref = L_carrier_ref = R_carrier_ref - carrier_distance
        self.Fv = Fv = 50
        self.samp_rate = samp_rate = 35.8e6
        self.pop_len = pop_len = audio_rate*(pop_time/2)
        self.op_VCO_deviation = op_VCO_deviation = VCO_deviation/3
        self.left_balance = left_balance = 1 - balance
        self.R_carrier = R_carrier = R_carrier_ref + carrierR_fine + center_freq
        self.L_carrier = L_carrier = L_carrier_ref + carrierL_fine + center_freq
        self.Fh = Fh = Fv*lines_per_frame/2
        self.volume = volume = 0.7
        self.sharpness = sharpness = round(op_VCO_deviation/2)
        self.right_squelch = right_squelch = 0
        self.right_balance = right_balance = 1-left_balance
        self.q_tip = q_tip = L_carrier+ abs(L_carrier-R_carrier)/2
        self.left_squelch = left_squelch = 0
        self.if_rate = if_rate = nearest.power(samp_rate/6,2)
        self.half_VCO_deviation = half_VCO_deviation = VCO_deviation/2
        self.fh_comb_delay = fh_comb_delay = round(audio_rate/(2*Fh))
        self.channel_width = channel_width = 2*(20e3+VCO_deviation)
        self.RMS_threshold = RMS_threshold = 0.05
        self.RMS_average = RMS_average = round(pop_len*10/2)

        ##################################################
        # Blocks
        ##################################################
        self.tabs = Qt.QTabWidget()
        self.tabs_widget_0 = Qt.QWidget()
        self.tabs_layout_0 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_0)
        self.tabs_grid_layout_0 = Qt.QGridLayout()
        self.tabs_layout_0.addLayout(self.tabs_grid_layout_0)
        self.tabs.addTab(self.tabs_widget_0, 'Main')
        self.tabs_widget_1 = Qt.QWidget()
        self.tabs_layout_1 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_1)
        self.tabs_grid_layout_1 = Qt.QGridLayout()
        self.tabs_layout_1.addLayout(self.tabs_grid_layout_1)
        self.tabs.addTab(self.tabs_widget_1, 'Noise gate')
        self.tabs_widget_2 = Qt.QWidget()
        self.tabs_layout_2 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_2)
        self.tabs_grid_layout_2 = Qt.QGridLayout()
        self.tabs_layout_2.addLayout(self.tabs_grid_layout_2)
        self.tabs.addTab(self.tabs_widget_2, 'Output')
        self.tabs_widget_3 = Qt.QWidget()
        self.tabs_layout_3 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_widget_3)
        self.tabs_grid_layout_3 = Qt.QGridLayout()
        self.tabs_layout_3.addLayout(self.tabs_grid_layout_3)
        self.tabs.addTab(self.tabs_widget_3, 'Input')
        self.top_grid_layout.addWidget(self.tabs)
        self.RS_signal = blocks.probe_signal_f()
        self.LS_signal = blocks.probe_signal_f()
        self._volume_range = Range(0, 2, 0.01, 0.7, 200)
        self._volume_win = RangeWidget(self._volume_range, self.set_volume, 'Volume', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._volume_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(1, 2):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self._sharpness_range = Range(int(op_VCO_deviation/4), int(op_VCO_deviation*2), 1, round(op_VCO_deviation/2), 300)
        self._sharpness_win = RangeWidget(self._sharpness_range, self.set_sharpness, 'Transition', "counter_slider", int)
        self.tabs_layout_1.addWidget(self._sharpness_win)
        def _right_squelch_probe():
            while True:

                val = self.RS_signal.level()
                try:
                    self.set_right_squelch(val)
                except AttributeError:
                    pass
                time.sleep(1.0 / (audio_rate))
        _right_squelch_thread = threading.Thread(target=_right_squelch_probe)
        _right_squelch_thread.daemon = True
        _right_squelch_thread.start()

        def _left_squelch_probe():
            while True:

                val = self.LS_signal.level()
                try:
                    self.set_left_squelch(val)
                except AttributeError:
                    pass
                time.sleep(1.0 / (audio_rate))
        _left_squelch_thread = threading.Thread(target=_left_squelch_probe)
        _left_squelch_thread.daemon = True
        _left_squelch_thread.start()

        self._RMS_threshold_range = Range(0, 0.1, 0.0001, 0.05, 200)
        self._RMS_threshold_win = RangeWidget(self._RMS_threshold_range, self.set_RMS_threshold, 'Gate Peak', "counter_slider", float)
        self.tabs_layout_1.addWidget(self._RMS_threshold_win)
        self._RMS_average_range = Range(1, round(pop_len*10), 1, round(pop_len*10/2), 200)
        self._RMS_average_win = RangeWidget(self._RMS_average_range, self.set_RMS_average, 'Gate Average', "counter_slider", float)
        self.tabs_layout_1.addWidget(self._RMS_average_win)
        self.rational_resampler_xxx_1_1 = filter.rational_resampler_fff(
                interpolation=Fraction(audio_rate/if_rate).limit_denominator(1000).numerator,
                decimation=Fraction(audio_rate/if_rate).limit_denominator(1000).denominator,
                taps=None,
                fractional_bw=None)
        self.rational_resampler_xxx_1_0_0 = filter.rational_resampler_fff(
                interpolation=Fraction(audio_rate/if_rate).limit_denominator(1000).numerator,
                decimation=Fraction(audio_rate/if_rate).limit_denominator(1000).denominator,
                taps=None,
                fractional_bw=None)
        self.rational_resampler_xxx_1_0 = filter.rational_resampler_fff(
                interpolation=Fraction(audio_rate/if_rate).limit_denominator(1000).numerator,
                decimation=Fraction(audio_rate/if_rate).limit_denominator(1000).denominator,
                taps=None,
                fractional_bw=None)
        self.rational_resampler_xxx_1 = filter.rational_resampler_fff(
                interpolation=Fraction(audio_rate/if_rate).limit_denominator(1000).numerator,
                decimation=Fraction(audio_rate/if_rate).limit_denominator(1000).denominator,
                taps=None,
                fractional_bw=None)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=Fraction(if_rate/samp_rate).limit_denominator(1000).numerator,
                decimation=Fraction(if_rate/samp_rate).limit_denominator(1000).denominator,
                taps=None,
                fractional_bw=None)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_f(
            1024, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            audio_rate, #bw
            "Main", #name
            2 #number of inputs
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)


        self.qtgui_waterfall_sink_x_0.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.pyqwidget(), Qt.QWidget)
        self.tabs_layout_2.addWidget(self._qtgui_waterfall_sink_x_0_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            64, #size
            if_rate, #samp_rate
            "", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-3, 3)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_AUTO, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)

        self.qtgui_time_sink_x_0.disable_legend()

        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.tabs_layout_3.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_number_sink_0_1_1 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1
        )
        self.qtgui_number_sink_0_1_1.set_update_time(0.05)
        self.qtgui_number_sink_0_1_1.set_title("Vu-Meter")

        labels = ['L', 'R', 'Squelch', '', '',
            '', '', '', '', '']
        units = ['V', 'V', 'V', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0_1_1.set_min(i, 0)
            self.qtgui_number_sink_0_1_1.set_max(i, 2)
            self.qtgui_number_sink_0_1_1.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_1_1.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_1_1.set_label(i, labels[i])
            self.qtgui_number_sink_0_1_1.set_unit(i, units[i])
            self.qtgui_number_sink_0_1_1.set_factor(i, factor[i])

        self.qtgui_number_sink_0_1_1.enable_autoscale(False)
        self._qtgui_number_sink_0_1_1_win = sip.wrapinstance(self.qtgui_number_sink_0_1_1.pyqwidget(), Qt.QWidget)
        self.tabs_layout_1.addWidget(self._qtgui_number_sink_0_1_1_win)
        self.qtgui_number_sink_0_1 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            2
        )
        self.qtgui_number_sink_0_1.set_update_time(0.05)
        self.qtgui_number_sink_0_1.set_title("Vu-Meter")

        labels = ['L', 'R', 'Squelch', '', '',
            '', '', '', '', '']
        units = ['Vpp x10', 'Vpp x10', 'V', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(2):
            self.qtgui_number_sink_0_1.set_min(i, 0)
            self.qtgui_number_sink_0_1.set_max(i, 5)
            self.qtgui_number_sink_0_1.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_1.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_1.set_label(i, labels[i])
            self.qtgui_number_sink_0_1.set_unit(i, units[i])
            self.qtgui_number_sink_0_1.set_factor(i, factor[i])

        self.qtgui_number_sink_0_1.enable_autoscale(False)
        self._qtgui_number_sink_0_1_win = sip.wrapinstance(self.qtgui_number_sink_0_1.pyqwidget(), Qt.QWidget)
        self.tabs_grid_layout_0.addWidget(self._qtgui_number_sink_0_1_win, 3, 0, 1, 2)
        for r in range(3, 4):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 2):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_f(
            2048, #size
            firdes.WIN_KAISER, #wintype
            0, #fc
            if_rate, #bw
            "", #name
            3
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(True)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(0.05)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)

        self.qtgui_freq_sink_x_0.disable_legend()

        self.qtgui_freq_sink_x_0.set_plot_pos_half(not False)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(3):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.tabs_layout_0.addWidget(self._qtgui_freq_sink_x_0_win)
        self.low_pass_filter_0_1 = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                0.35*volume,
                audio_rate,
                20000,
                4000,
                firdes.WIN_KAISER,
                6.76))
        self.low_pass_filter_0_0_0 = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                0.35*volume,
                audio_rate,
                20000,
                4000,
                firdes.WIN_KAISER,
                6.76))
        self.high_pass_filter_1_0 = filter.fir_filter_fff(
            1,
            firdes.high_pass(
                right_balance,
                audio_rate,
                30,
                15,
                firdes.WIN_KAISER,
                6.76))
        self.high_pass_filter_1 = filter.fir_filter_fff(
            1,
            firdes.high_pass(
                left_balance,
                audio_rate,
                30,
                15,
                firdes.WIN_KAISER,
                6.76))
        self.freq_xlating_fir_filter_xxx_0_0 = filter.freq_xlating_fir_filter_ccc(1, [1], R_carrier, if_rate)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, [1], L_carrier, if_rate)
        self._center_freq_range = Range(-30e3, 30e3, 0.1, -4591.900, 300)
        self._center_freq_win = RangeWidget(self._center_freq_range, self.set_center_freq, 'Center Fine', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._center_freq_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self._carrierR_fine_range = Range(-100e3, 100e3, 1, 3603, 200)
        self._carrierR_fine_win = RangeWidget(self._carrierR_fine_range, self.set_carrierR_fine, 'R Fine Tune', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._carrierR_fine_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(1, 2):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self._carrierL_fine_range = Range(-100e3, 100e3, 1, 0, 200)
        self._carrierL_fine_win = RangeWidget(self._carrierL_fine_range, self.set_carrierL_fine, 'L Fine Tune', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._carrierL_fine_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink('vhs_hifi_test.wav', 2, round(audio_rate), 16)
        self.blocks_uchar_to_float_0 = blocks.uchar_to_float()
        self.blocks_threshold_ff_0_0 = blocks.threshold_ff(RMS_threshold*volume, RMS_threshold*volume, 0)
        self.blocks_threshold_ff_0 = blocks.threshold_ff(RMS_threshold*volume, RMS_threshold*volume, 0)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_rms_xx_0_2 = blocks.rms_ff(1/RMS_average)
        self.blocks_rms_xx_0_0_0 = blocks.rms_ff(1/RMS_average)
        self.blocks_rms_xx_0_0 = blocks.rms_ff(1/1024)
        self.blocks_rms_xx_0 = blocks.rms_ff(1/1024)
        self.blocks_multiply_const_vxx_8 = blocks.multiply_const_ff(left_squelch)
        self.blocks_multiply_const_vxx_7 = blocks.multiply_const_ff(right_squelch)
        self.blocks_multiply_const_vxx_6 = blocks.multiply_const_ff(1-right_squelch)
        self.blocks_multiply_const_vxx_5 = blocks.multiply_const_ff(1-left_squelch)
        self.blocks_multiply_const_vxx_4_0 = blocks.multiply_const_ff(1)
        self.blocks_multiply_const_vxx_4 = blocks.multiply_const_ff(1)
        self.blocks_multiply_const_vxx_3_0 = blocks.multiply_const_ff(0.5)
        self.blocks_multiply_const_vxx_3 = blocks.multiply_const_ff(0.5)
        self.blocks_multiply_const_vxx_2 = blocks.multiply_const_ff(10)
        self.blocks_multiply_const_vxx_10 = blocks.multiply_const_ff(1/64)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff(10)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff(1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(1)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(round(if_rate /  120), 1/round(if_rate / 120), 4000, 1)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, '/home/sebastian/Downloads/VTR/HIFI/test_hifi.r8', False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_delay_1 = blocks.delay(gr.sizeof_float*1, round(if_rate /  120))
        self.blocks_delay_0_0 = blocks.delay(gr.sizeof_float*1, fh_comb_delay)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_float*1, fh_comb_delay)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_add_xx_3_0 = blocks.add_vff(1)
        self.blocks_add_xx_3 = blocks.add_vff(1)
        self.blocks_add_xx_2_0 = blocks.add_vff(1)
        self.blocks_add_xx_2 = blocks.add_vff(1)
        self.blocks_add_xx_1 = blocks.add_vcc(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.blocks_add_const_vxx_2 = blocks.add_const_ff(-128)
        self.band_pass_filter_1 = filter.fir_filter_fff(
            1,
            firdes.band_pass(
                1,
                if_rate,
                1e6,
                2e6,
                500e3,
                firdes.WIN_KAISER,
                14))
        self.band_pass_filter_0_0 = filter.fir_filter_ccf(
            1,
            firdes.band_pass(
                1,
                if_rate,
                R_carrier - VCO_deviation / 2 ,
                R_carrier + VCO_deviation / 2,
                sharpness,
                firdes.WIN_KAISER,
                6.76))
        self.band_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.band_pass(
                1,
                if_rate,
                L_carrier - VCO_deviation /2,
                L_carrier + VCO_deviation /2,
                sharpness,
                firdes.WIN_KAISER,
                6.76))
        self._balance_range = Range(0.25, 0.75, 0.01, 0.48, 200)
        self._balance_win = RangeWidget(self._balance_range, self.set_balance, 'Balance', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._balance_win, 4, 0, 1, 2)
        for r in range(4, 5):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 2):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self.analog_sig_source_x_0_0 = analog.sig_source_f(if_rate, analog.GR_COS_WAVE, R_carrier, 1, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_f(if_rate, analog.GR_COS_WAVE, L_carrier, 1, 0, 0)
        self.analog_rail_ff_1_1_1_0 = analog.rail_ff(-0.999, 0.999)
        self.analog_rail_ff_1_1_1 = analog.rail_ff(-0.999, 0.999)
        self.analog_rail_ff_1_1_0 = analog.rail_ff(-0.999, 0.999)
        self.analog_rail_ff_1_1 = analog.rail_ff(-0.999, 0.999)
        self.analog_quadrature_demod_cf_0_0 = analog.quadrature_demod_cf(if_rate/(2*math.pi*VCO_deviation/8.0))
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(if_rate/(2*math.pi*VCO_deviation/8.0))
        self.analog_fm_preemph_0 = analog.fm_preemph(fs=if_rate, tau=1.25e-6, fh=-1.0)
        self.analog_fm_deemph_0_0 = analog.fm_deemph(fs=if_rate, tau=50e-6)
        self.analog_fm_deemph_0 = analog.fm_deemph(fs=if_rate, tau=50e-6)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_fm_deemph_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.analog_fm_deemph_0_0, 0), (self.rational_resampler_xxx_1_0, 0))
        self.connect((self.analog_fm_preemph_0, 0), (self.blocks_delay_1, 0))
        self.connect((self.analog_fm_preemph_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.analog_fm_deemph_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.rational_resampler_xxx_1_1, 0))
        self.connect((self.analog_quadrature_demod_cf_0_0, 0), (self.analog_fm_deemph_0_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0_0, 0), (self.rational_resampler_xxx_1_0_0, 0))
        self.connect((self.analog_rail_ff_1_1, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.analog_rail_ff_1_1, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.analog_rail_ff_1_1_0, 0), (self.blocks_wavfile_sink_0, 1))
        self.connect((self.analog_rail_ff_1_1_0, 0), (self.qtgui_waterfall_sink_x_0, 1))
        self.connect((self.analog_rail_ff_1_1_1, 0), (self.blocks_add_xx_2, 0))
        self.connect((self.analog_rail_ff_1_1_1, 0), (self.blocks_delay_0, 0))
        self.connect((self.analog_rail_ff_1_1_1, 0), (self.blocks_multiply_const_vxx_8, 0))
        self.connect((self.analog_rail_ff_1_1_1_0, 0), (self.blocks_add_xx_2_0, 0))
        self.connect((self.analog_rail_ff_1_1_1_0, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.analog_rail_ff_1_1_1_0, 0), (self.blocks_multiply_const_vxx_7, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.qtgui_freq_sink_x_0, 1))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.qtgui_freq_sink_x_0, 2))
        self.connect((self.band_pass_filter_0, 0), (self.blocks_add_xx_1, 1))
        self.connect((self.band_pass_filter_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.band_pass_filter_0_0, 0), (self.blocks_add_xx_1, 0))
        self.connect((self.band_pass_filter_0_0, 0), (self.freq_xlating_fir_filter_xxx_0_0, 0))
        self.connect((self.band_pass_filter_1, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_add_const_vxx_2, 0), (self.blocks_multiply_const_vxx_10, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_number_sink_0_1_1, 0))
        self.connect((self.blocks_add_xx_1, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.blocks_add_xx_2, 0), (self.blocks_multiply_const_vxx_3, 0))
        self.connect((self.blocks_add_xx_2_0, 0), (self.blocks_multiply_const_vxx_3_0, 0))
        self.connect((self.blocks_add_xx_3, 0), (self.high_pass_filter_1, 0))
        self.connect((self.blocks_add_xx_3_0, 0), (self.high_pass_filter_1_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_multiply_const_vxx_5, 0))
        self.connect((self.blocks_delay_0_0, 0), (self.blocks_multiply_const_vxx_6, 0))
        self.connect((self.blocks_delay_1, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_uchar_to_float_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.band_pass_filter_0_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.analog_rail_ff_1_1_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_rms_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.analog_rail_ff_1_1_1_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_rms_xx_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.qtgui_number_sink_0_1, 0))
        self.connect((self.blocks_multiply_const_vxx_10, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_2, 0), (self.qtgui_number_sink_0_1, 1))
        self.connect((self.blocks_multiply_const_vxx_3, 0), (self.analog_rail_ff_1_1, 0))
        self.connect((self.blocks_multiply_const_vxx_3_0, 0), (self.analog_rail_ff_1_1_0, 0))
        self.connect((self.blocks_multiply_const_vxx_4, 0), (self.blocks_add_xx_3, 0))
        self.connect((self.blocks_multiply_const_vxx_4_0, 0), (self.blocks_add_xx_3_0, 1))
        self.connect((self.blocks_multiply_const_vxx_5, 0), (self.blocks_add_xx_2, 1))
        self.connect((self.blocks_multiply_const_vxx_6, 0), (self.blocks_add_xx_2_0, 1))
        self.connect((self.blocks_multiply_const_vxx_7, 0), (self.blocks_add_xx_2_0, 2))
        self.connect((self.blocks_multiply_const_vxx_8, 0), (self.blocks_add_xx_2, 2))
        self.connect((self.blocks_rms_xx_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_rms_xx_0_0, 0), (self.blocks_multiply_const_vxx_2, 0))
        self.connect((self.blocks_rms_xx_0_0_0, 0), (self.blocks_threshold_ff_0_0, 0))
        self.connect((self.blocks_rms_xx_0_2, 0), (self.blocks_threshold_ff_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.band_pass_filter_1, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.LS_signal, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_threshold_ff_0_0, 0), (self.RS_signal, 0))
        self.connect((self.blocks_threshold_ff_0_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_uchar_to_float_0, 0), (self.blocks_add_const_vxx_2, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0_0, 0), (self.analog_quadrature_demod_cf_0_0, 0))
        self.connect((self.high_pass_filter_1, 0), (self.low_pass_filter_0_1, 0))
        self.connect((self.high_pass_filter_1_0, 0), (self.low_pass_filter_0_0_0, 0))
        self.connect((self.low_pass_filter_0_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.low_pass_filter_0_0_0, 0), (self.blocks_rms_xx_0_0_0, 0))
        self.connect((self.low_pass_filter_0_1, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.low_pass_filter_0_1, 0), (self.blocks_rms_xx_0_2, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_fm_preemph_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.blocks_add_xx_3, 1))
        self.connect((self.rational_resampler_xxx_1_0, 0), (self.blocks_add_xx_3_0, 0))
        self.connect((self.rational_resampler_xxx_1_0_0, 0), (self.blocks_multiply_const_vxx_4_0, 0))
        self.connect((self.rational_resampler_xxx_1_1, 0), (self.blocks_multiply_const_vxx_4, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "VHS_HiFi_decoder")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_carrier_distance(self):
        return self.carrier_distance

    def set_carrier_distance(self, carrier_distance):
        self.carrier_distance = carrier_distance
        self.set_L_carrier_ref(self.R_carrier_ref - self.carrier_distance)

    def get_R_carrier_ref(self):
        return self.R_carrier_ref

    def set_R_carrier_ref(self, R_carrier_ref):
        self.R_carrier_ref = R_carrier_ref
        self.set_L_carrier_ref(self.R_carrier_ref - self.carrier_distance)
        self.set_R_carrier(self.R_carrier_ref + self.carrierR_fine + self.center_freq)

    def get_pop_time(self):
        return self.pop_time

    def set_pop_time(self, pop_time):
        self.pop_time = pop_time
        self.set_pop_len(self.audio_rate*(self.pop_time/2))

    def get_lines_per_frame(self):
        return self.lines_per_frame

    def set_lines_per_frame(self, lines_per_frame):
        self.lines_per_frame = lines_per_frame
        self.set_Fh(self.Fv*self.lines_per_frame/2)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.set_L_carrier(self.L_carrier_ref + self.carrierL_fine + self.center_freq)
        self.set_R_carrier(self.R_carrier_ref + self.carrierR_fine + self.center_freq)

    def get_carrierR_fine(self):
        return self.carrierR_fine

    def set_carrierR_fine(self, carrierR_fine):
        self.carrierR_fine = carrierR_fine
        self.set_R_carrier(self.R_carrier_ref + self.carrierR_fine + self.center_freq)

    def get_carrierL_fine(self):
        return self.carrierL_fine

    def set_carrierL_fine(self, carrierL_fine):
        self.carrierL_fine = carrierL_fine
        self.set_L_carrier(self.L_carrier_ref + self.carrierL_fine + self.center_freq)

    def get_balance(self):
        return self.balance

    def set_balance(self, balance):
        self.balance = balance
        self.set_left_balance(1 - self.balance)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.set_fh_comb_delay(round(self.audio_rate/(2*self.Fh)))
        self.set_pop_len(self.audio_rate*(self.pop_time/2))
        self.high_pass_filter_1.set_taps(firdes.high_pass(self.left_balance, self.audio_rate, 30, 15, firdes.WIN_KAISER, 6.76))
        self.high_pass_filter_1_0.set_taps(firdes.high_pass(self.right_balance, self.audio_rate, 30, 15, firdes.WIN_KAISER, 6.76))
        self.low_pass_filter_0_0_0.set_taps(firdes.low_pass(0.35*self.volume, self.audio_rate, 20000, 4000, firdes.WIN_KAISER, 6.76))
        self.low_pass_filter_0_1.set_taps(firdes.low_pass(0.35*self.volume, self.audio_rate, 20000, 4000, firdes.WIN_KAISER, 6.76))
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.audio_rate)

    def get_VCO_deviation(self):
        return self.VCO_deviation

    def set_VCO_deviation(self, VCO_deviation):
        self.VCO_deviation = VCO_deviation
        self.set_channel_width(2*(20e3+self.VCO_deviation))
        self.set_half_VCO_deviation(self.VCO_deviation/2)
        self.set_op_VCO_deviation(self.VCO_deviation/3)
        self.analog_quadrature_demod_cf_0.set_gain(self.if_rate/(2*math.pi*self.VCO_deviation/8.0))
        self.analog_quadrature_demod_cf_0_0.set_gain(self.if_rate/(2*math.pi*self.VCO_deviation/8.0))
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.if_rate, self.L_carrier - self.VCO_deviation /2, self.L_carrier + self.VCO_deviation /2, self.sharpness, firdes.WIN_KAISER, 6.76))
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1, self.if_rate, self.R_carrier - self.VCO_deviation / 2 , self.R_carrier + self.VCO_deviation / 2, self.sharpness, firdes.WIN_KAISER, 6.76))

    def get_L_carrier_ref(self):
        return self.L_carrier_ref

    def set_L_carrier_ref(self, L_carrier_ref):
        self.L_carrier_ref = L_carrier_ref
        self.set_L_carrier(self.L_carrier_ref + self.carrierL_fine + self.center_freq)

    def get_Fv(self):
        return self.Fv

    def set_Fv(self, Fv):
        self.Fv = Fv
        self.set_Fh(self.Fv*self.lines_per_frame/2)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_if_rate(nearest.power(self.samp_rate/6,2))

    def get_pop_len(self):
        return self.pop_len

    def set_pop_len(self, pop_len):
        self.pop_len = pop_len
        self.set_RMS_average(round(self.pop_len*10/2))

    def get_op_VCO_deviation(self):
        return self.op_VCO_deviation

    def set_op_VCO_deviation(self, op_VCO_deviation):
        self.op_VCO_deviation = op_VCO_deviation
        self.set_sharpness(round(self.op_VCO_deviation/2))

    def get_left_balance(self):
        return self.left_balance

    def set_left_balance(self, left_balance):
        self.left_balance = left_balance
        self.set_right_balance(1-self.left_balance)
        self.high_pass_filter_1.set_taps(firdes.high_pass(self.left_balance, self.audio_rate, 30, 15, firdes.WIN_KAISER, 6.76))

    def get_R_carrier(self):
        return self.R_carrier

    def set_R_carrier(self, R_carrier):
        self.R_carrier = R_carrier
        self.set_q_tip(self.L_carrier+ abs(self.L_carrier-self.R_carrier)/2)
        self.analog_sig_source_x_0_0.set_frequency(self.R_carrier)
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1, self.if_rate, self.R_carrier - self.VCO_deviation / 2 , self.R_carrier + self.VCO_deviation / 2, self.sharpness, firdes.WIN_KAISER, 6.76))
        self.freq_xlating_fir_filter_xxx_0_0.set_center_freq(self.R_carrier)

    def get_L_carrier(self):
        return self.L_carrier

    def set_L_carrier(self, L_carrier):
        self.L_carrier = L_carrier
        self.set_q_tip(self.L_carrier+ abs(self.L_carrier-self.R_carrier)/2)
        self.analog_sig_source_x_0.set_frequency(self.L_carrier)
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.if_rate, self.L_carrier - self.VCO_deviation /2, self.L_carrier + self.VCO_deviation /2, self.sharpness, firdes.WIN_KAISER, 6.76))
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.L_carrier)

    def get_Fh(self):
        return self.Fh

    def set_Fh(self, Fh):
        self.Fh = Fh
        self.set_fh_comb_delay(round(self.audio_rate/(2*self.Fh)))

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.blocks_threshold_ff_0.set_hi(self.RMS_threshold*self.volume)
        self.blocks_threshold_ff_0.set_lo(self.RMS_threshold*self.volume)
        self.blocks_threshold_ff_0_0.set_hi(self.RMS_threshold*self.volume)
        self.blocks_threshold_ff_0_0.set_lo(self.RMS_threshold*self.volume)
        self.low_pass_filter_0_0_0.set_taps(firdes.low_pass(0.35*self.volume, self.audio_rate, 20000, 4000, firdes.WIN_KAISER, 6.76))
        self.low_pass_filter_0_1.set_taps(firdes.low_pass(0.35*self.volume, self.audio_rate, 20000, 4000, firdes.WIN_KAISER, 6.76))

    def get_sharpness(self):
        return self.sharpness

    def set_sharpness(self, sharpness):
        self.sharpness = sharpness
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.if_rate, self.L_carrier - self.VCO_deviation /2, self.L_carrier + self.VCO_deviation /2, self.sharpness, firdes.WIN_KAISER, 6.76))
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1, self.if_rate, self.R_carrier - self.VCO_deviation / 2 , self.R_carrier + self.VCO_deviation / 2, self.sharpness, firdes.WIN_KAISER, 6.76))

    def get_right_squelch(self):
        return self.right_squelch

    def set_right_squelch(self, right_squelch):
        self.right_squelch = right_squelch
        self.blocks_multiply_const_vxx_6.set_k(1-self.right_squelch)
        self.blocks_multiply_const_vxx_7.set_k(self.right_squelch)

    def get_right_balance(self):
        return self.right_balance

    def set_right_balance(self, right_balance):
        self.right_balance = right_balance
        self.high_pass_filter_1_0.set_taps(firdes.high_pass(self.right_balance, self.audio_rate, 30, 15, firdes.WIN_KAISER, 6.76))

    def get_q_tip(self):
        return self.q_tip

    def set_q_tip(self, q_tip):
        self.q_tip = q_tip

    def get_left_squelch(self):
        return self.left_squelch

    def set_left_squelch(self, left_squelch):
        self.left_squelch = left_squelch
        self.blocks_multiply_const_vxx_5.set_k(1-self.left_squelch)
        self.blocks_multiply_const_vxx_8.set_k(self.left_squelch)

    def get_if_rate(self):
        return self.if_rate

    def set_if_rate(self, if_rate):
        self.if_rate = if_rate
        self.analog_quadrature_demod_cf_0.set_gain(self.if_rate/(2*math.pi*self.VCO_deviation/8.0))
        self.analog_quadrature_demod_cf_0_0.set_gain(self.if_rate/(2*math.pi*self.VCO_deviation/8.0))
        self.analog_sig_source_x_0.set_sampling_freq(self.if_rate)
        self.analog_sig_source_x_0_0.set_sampling_freq(self.if_rate)
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.if_rate, self.L_carrier - self.VCO_deviation /2, self.L_carrier + self.VCO_deviation /2, self.sharpness, firdes.WIN_KAISER, 6.76))
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1, self.if_rate, self.R_carrier - self.VCO_deviation / 2 , self.R_carrier + self.VCO_deviation / 2, self.sharpness, firdes.WIN_KAISER, 6.76))
        self.band_pass_filter_1.set_taps(firdes.band_pass(1, self.if_rate, 1e6, 2e6, 500e3, firdes.WIN_KAISER, 14))
        self.blocks_delay_1.set_dly(round(self.if_rate /  120))
        self.blocks_moving_average_xx_0.set_length_and_scale(round(self.if_rate /  120), 1/round(self.if_rate / 120))
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.if_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.if_rate)

    def get_half_VCO_deviation(self):
        return self.half_VCO_deviation

    def set_half_VCO_deviation(self, half_VCO_deviation):
        self.half_VCO_deviation = half_VCO_deviation

    def get_fh_comb_delay(self):
        return self.fh_comb_delay

    def set_fh_comb_delay(self, fh_comb_delay):
        self.fh_comb_delay = fh_comb_delay
        self.blocks_delay_0.set_dly(self.fh_comb_delay)
        self.blocks_delay_0_0.set_dly(self.fh_comb_delay)

    def get_channel_width(self):
        return self.channel_width

    def set_channel_width(self, channel_width):
        self.channel_width = channel_width

    def get_RMS_threshold(self):
        return self.RMS_threshold

    def set_RMS_threshold(self, RMS_threshold):
        self.RMS_threshold = RMS_threshold
        self.blocks_threshold_ff_0.set_hi(self.RMS_threshold*self.volume)
        self.blocks_threshold_ff_0.set_lo(self.RMS_threshold*self.volume)
        self.blocks_threshold_ff_0_0.set_hi(self.RMS_threshold*self.volume)
        self.blocks_threshold_ff_0_0.set_lo(self.RMS_threshold*self.volume)

    def get_RMS_average(self):
        return self.RMS_average

    def set_RMS_average(self, RMS_average):
        self.RMS_average = RMS_average
        self.blocks_rms_xx_0_0_0.set_alpha(1/self.RMS_average)
        self.blocks_rms_xx_0_2.set_alpha(1/self.RMS_average)





def main(top_block_cls=VHS_HiFi_decoder, options=None):

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
