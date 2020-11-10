#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Superheterodyne HIFI decoder
# Author: VideoMem
# Copyright: GPL
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
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
import math
import nearest  # embedded python module
import pipe

from gnuradio import qtgui

class Superheterodyne_HIFI_decoder(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Superheterodyne HIFI decoder")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Superheterodyne HIFI decoder")
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

        self.settings = Qt.QSettings("GNU Radio", "Superheterodyne_HIFI_decoder")

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
        self.lines_per_frame = lines_per_frame = 525
        self.Fv = Fv = 60
        self.samp_rate = samp_rate = 40e6
        self.Fh = Fh = Fv*lines_per_frame/2
        self.FFT_points_order = FFT_points_order = 8
        self.if_rate = if_rate = nearest.power(samp_rate/4,2)
        self.center_freq = center_freq = -2181
        self.carrierL_fine = carrierL_fine = 0
        self.VCO_deviation = VCO_deviation = 300e3
        self.L_carrier_ref = L_carrier_ref = 146.25* Fh
        self.FFT_points = FFT_points = pow(2,FFT_points_order)
        self.op_VCO_deviation = op_VCO_deviation = VCO_deviation/3
        self.L_carrier = L_carrier = L_carrier_ref + carrierL_fine + center_freq
        self.FFT_bin_size = FFT_bin_size = if_rate/FFT_points
        self.volume = volume = 0.7
        self.sharpness = sharpness = round(op_VCO_deviation/2)
        self.half_VCO_deviation = half_VCO_deviation = VCO_deviation/2
        self.audio_rate = audio_rate = 8e3
        self.R_carrier_ref = R_carrier_ref = 178.75 * Fh
        self.FFT_carrier_bin = FFT_carrier_bin = round(L_carrier/FFT_bin_size)

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
        self.tabs.addTab(self.tabs_widget_3, 'Filter delay')
        self.top_grid_layout.addWidget(self.tabs)
        self._sharpness_range = Range(int(op_VCO_deviation/4), int(op_VCO_deviation*2), 1, round(op_VCO_deviation/2), 300)
        self._sharpness_win = RangeWidget(self._sharpness_range, self.set_sharpness, 'Transition', "counter_slider", int)
        self.tabs_layout_1.addWidget(self._sharpness_win)
        self._volume_range = Range(0, 2, 0.01, 0.7, 200)
        self._volume_win = RangeWidget(self._volume_range, self.set_volume, 'Volume', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._volume_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(1, 2):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self.rational_resampler_xxx_1 = filter.rational_resampler_fff(
                interpolation=Fraction((if_rate/FFT_points)/audio_rate).limit_denominator(1000).denominator,
                decimation=Fraction((if_rate/FFT_points)/audio_rate).limit_denominator(1000).numerator,
                taps=None,
                fractional_bw=None)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=Fraction(if_rate/samp_rate).limit_denominator(1000).numerator,
                decimation=Fraction(if_rate/samp_rate).limit_denominator(1000).denominator,
                taps=None,
                fractional_bw=None)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            1024, #size
            if_rate/FFT_points, #samp_rate
            "", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


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
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_f(
            2048, #size
            firdes.WIN_KAISER, #wintype
            0, #fc
            if_rate, #bw
            "", #name
            2
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

        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.tabs_layout_0.addWidget(self._qtgui_freq_sink_x_0_win)
        self.pipe_source_1 = pipe.source(gr.sizeof_short*1, 'ld-ldf-reader /home/sebastian/Downloads/VTR/LD/AC3.ldf')
        self.low_pass_filter_0 = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                1,
                if_rate/FFT_points,
                60,
                10,
                firdes.WIN_KAISER,
                6.76))
        self.fft_vxx_0_0 = fft.fft_vcc(FFT_points, True, window.blackmanharris(FFT_points), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(FFT_points, True, window.blackmanharris(FFT_points), True, 1)
        self.dc_blocker_xx_1 = filter.dc_blocker_ff(round(if_rate/FFT_points), True)
        self.dc_blocker_xx_0 = filter.dc_blocker_ff(round(samp_rate/100), True)
        self._center_freq_range = Range(-10e3, 10e3, 0.1, -2181, 300)
        self._center_freq_win = RangeWidget(self._center_freq_range, self.set_center_freq, 'Center Fine', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._center_freq_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self._carrierL_fine_range = Range(-5e3, 5e3, 1, 0, 200)
        self._carrierL_fine_win = RangeWidget(self._carrierL_fine_range, self.set_carrierL_fine, 'L Fine Tune', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._carrierL_fine_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self.blocks_wavfile_sink_0_0 = blocks.wavfile_sink('phase_note.wav', 1, round(audio_rate), 16)
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink('phase_shift.wav', 1, round(if_rate/FFT_points), 16)
        self.blocks_vector_to_stream_0_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, FFT_points)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, FFT_points)
        self.blocks_vco_f_0 = blocks.vco_f(audio_rate, 2*math.pi*440, 0.5)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, FFT_points)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, FFT_points)
        self.blocks_skiphead_0_0 = blocks.skiphead(gr.sizeof_gr_complex*1, FFT_carrier_bin+1)
        self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_gr_complex*1, FFT_carrier_bin+1)
        self.blocks_short_to_float_0 = blocks.short_to_float(1, 1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(2)
        self.blocks_keep_one_in_n_0_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, FFT_points)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, FFT_points)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_arg_0_0 = blocks.complex_to_arg(1)
        self.blocks_complex_to_arg_0 = blocks.complex_to_arg(1)
        self.blocks_add_const_vxx_0 = blocks.add_const_ff(1)
        self.band_pass_filter_0_0 = filter.fir_filter_ccf(
            1,
            firdes.band_pass(
                1,
                if_rate,
                L_carrier - VCO_deviation / 2 ,
                L_carrier + VCO_deviation / 2,
                sharpness,
                firdes.WIN_KAISER,
                6.76))
        self.analog_sig_source_x_0_1 = analog.sig_source_c(if_rate, analog.GR_COS_WAVE, L_carrier_ref, 1, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_f(if_rate, analog.GR_COS_WAVE, L_carrier, 1, 0, 0)
        self.analog_agc2_xx_0 = analog.agc2_cc(1/Fh, 1/Fh, 1, 1)
        self.analog_agc2_xx_0.set_max_gain(65536)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_agc2_xx_0, 0), (self.band_pass_filter_0_0, 0))
        self.connect((self.analog_agc2_xx_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.qtgui_freq_sink_x_0, 1))
        self.connect((self.analog_sig_source_x_0_1, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.band_pass_filter_0_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.band_pass_filter_0_0, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_vco_f_0, 0))
        self.connect((self.blocks_complex_to_arg_0, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.blocks_complex_to_arg_0_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.blocks_complex_to_real_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.analog_agc2_xx_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.blocks_complex_to_arg_0, 0))
        self.connect((self.blocks_keep_one_in_n_0_0, 0), (self.blocks_complex_to_arg_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.blocks_short_to_float_0, 0), (self.dc_blocker_xx_0, 0))
        self.connect((self.blocks_skiphead_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_skiphead_0_0, 0), (self.blocks_keep_one_in_n_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.fft_vxx_0_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.blocks_vco_f_0, 0), (self.blocks_wavfile_sink_0_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_skiphead_0, 0))
        self.connect((self.blocks_vector_to_stream_0_0, 0), (self.blocks_skiphead_0_0, 0))
        self.connect((self.dc_blocker_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.dc_blocker_xx_1, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.fft_vxx_0_0, 0), (self.blocks_vector_to_stream_0_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.dc_blocker_xx_1, 0))
        self.connect((self.low_pass_filter_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.pipe_source_1, 0), (self.blocks_short_to_float_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.blocks_multiply_const_vxx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "Superheterodyne_HIFI_decoder")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_lines_per_frame(self):
        return self.lines_per_frame

    def set_lines_per_frame(self, lines_per_frame):
        self.lines_per_frame = lines_per_frame
        self.set_Fh(self.Fv*self.lines_per_frame/2)

    def get_Fv(self):
        return self.Fv

    def set_Fv(self, Fv):
        self.Fv = Fv
        self.set_Fh(self.Fv*self.lines_per_frame/2)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_if_rate(nearest.power(self.samp_rate/4,2))

    def get_Fh(self):
        return self.Fh

    def set_Fh(self, Fh):
        self.Fh = Fh
        self.set_L_carrier_ref(146.25* self.Fh)
        self.set_R_carrier_ref(178.75 * self.Fh)
        self.analog_agc2_xx_0.set_attack_rate(1/self.Fh)
        self.analog_agc2_xx_0.set_decay_rate(1/self.Fh)

    def get_FFT_points_order(self):
        return self.FFT_points_order

    def set_FFT_points_order(self, FFT_points_order):
        self.FFT_points_order = FFT_points_order
        self.set_FFT_points(pow(2,self.FFT_points_order))

    def get_if_rate(self):
        return self.if_rate

    def set_if_rate(self, if_rate):
        self.if_rate = if_rate
        self.set_FFT_bin_size(self.if_rate/self.FFT_points)
        self.analog_sig_source_x_0.set_sampling_freq(self.if_rate)
        self.analog_sig_source_x_0_1.set_sampling_freq(self.if_rate)
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1, self.if_rate, self.L_carrier - self.VCO_deviation / 2 , self.L_carrier + self.VCO_deviation / 2, self.sharpness, firdes.WIN_KAISER, 6.76))
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.if_rate/self.FFT_points, 60, 10, firdes.WIN_KAISER, 6.76))
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.if_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.if_rate/self.FFT_points)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.set_L_carrier(self.L_carrier_ref + self.carrierL_fine + self.center_freq)

    def get_carrierL_fine(self):
        return self.carrierL_fine

    def set_carrierL_fine(self, carrierL_fine):
        self.carrierL_fine = carrierL_fine
        self.set_L_carrier(self.L_carrier_ref + self.carrierL_fine + self.center_freq)

    def get_VCO_deviation(self):
        return self.VCO_deviation

    def set_VCO_deviation(self, VCO_deviation):
        self.VCO_deviation = VCO_deviation
        self.set_half_VCO_deviation(self.VCO_deviation/2)
        self.set_op_VCO_deviation(self.VCO_deviation/3)
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1, self.if_rate, self.L_carrier - self.VCO_deviation / 2 , self.L_carrier + self.VCO_deviation / 2, self.sharpness, firdes.WIN_KAISER, 6.76))

    def get_L_carrier_ref(self):
        return self.L_carrier_ref

    def set_L_carrier_ref(self, L_carrier_ref):
        self.L_carrier_ref = L_carrier_ref
        self.set_L_carrier(self.L_carrier_ref + self.carrierL_fine + self.center_freq)
        self.analog_sig_source_x_0_1.set_frequency(self.L_carrier_ref)

    def get_FFT_points(self):
        return self.FFT_points

    def set_FFT_points(self, FFT_points):
        self.FFT_points = FFT_points
        self.set_FFT_bin_size(self.if_rate/self.FFT_points)
        self.blocks_keep_one_in_n_0.set_n(self.FFT_points)
        self.blocks_keep_one_in_n_0_0.set_n(self.FFT_points)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.if_rate/self.FFT_points, 60, 10, firdes.WIN_KAISER, 6.76))
        self.qtgui_time_sink_x_0.set_samp_rate(self.if_rate/self.FFT_points)

    def get_op_VCO_deviation(self):
        return self.op_VCO_deviation

    def set_op_VCO_deviation(self, op_VCO_deviation):
        self.op_VCO_deviation = op_VCO_deviation
        self.set_sharpness(round(self.op_VCO_deviation/2))

    def get_L_carrier(self):
        return self.L_carrier

    def set_L_carrier(self, L_carrier):
        self.L_carrier = L_carrier
        self.set_FFT_carrier_bin(round(self.L_carrier/self.FFT_bin_size))
        self.analog_sig_source_x_0.set_frequency(self.L_carrier)
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1, self.if_rate, self.L_carrier - self.VCO_deviation / 2 , self.L_carrier + self.VCO_deviation / 2, self.sharpness, firdes.WIN_KAISER, 6.76))

    def get_FFT_bin_size(self):
        return self.FFT_bin_size

    def set_FFT_bin_size(self, FFT_bin_size):
        self.FFT_bin_size = FFT_bin_size
        self.set_FFT_carrier_bin(round(self.L_carrier/self.FFT_bin_size))

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume

    def get_sharpness(self):
        return self.sharpness

    def set_sharpness(self, sharpness):
        self.sharpness = sharpness
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1, self.if_rate, self.L_carrier - self.VCO_deviation / 2 , self.L_carrier + self.VCO_deviation / 2, self.sharpness, firdes.WIN_KAISER, 6.76))

    def get_half_VCO_deviation(self):
        return self.half_VCO_deviation

    def set_half_VCO_deviation(self, half_VCO_deviation):
        self.half_VCO_deviation = half_VCO_deviation

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate

    def get_R_carrier_ref(self):
        return self.R_carrier_ref

    def set_R_carrier_ref(self, R_carrier_ref):
        self.R_carrier_ref = R_carrier_ref

    def get_FFT_carrier_bin(self):
        return self.FFT_carrier_bin

    def set_FFT_carrier_bin(self, FFT_carrier_bin):
        self.FFT_carrier_bin = FFT_carrier_bin





def main(top_block_cls=Superheterodyne_HIFI_decoder, options=None):

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
