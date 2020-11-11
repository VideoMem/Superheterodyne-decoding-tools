#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: CX decoder
# Author: VideoMem
# Copyright: GPL
# Description: Audio CX Noise Reduction
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
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
from gnuradio.qtgui import Range, RangeWidget
import math
import time
import threading

from gnuradio import qtgui

class CX_NR(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "CX decoder")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("CX decoder")
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

        self.settings = Qt.QSettings("GNU Radio", "CX_NR")

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
        self.samp_rate = samp_rate = 192e3
        self.decimation = decimation = 4
        self.volume = volume = 0.5
        self.tp1_gain = tp1_gain = 0.52
        self.test_tone_enable = test_tone_enable = 0.0
        self.test_gain = test_gain = 1
        self.min_average = min_average = 128
        self.knee_point = knee_point = 0.2900
        self.dry = dry = 1
        self.diode_drop = diode_drop = 0.5
        self.ctrl_rate = ctrl_rate = round(samp_rate/decimation)
        self.ctrl_gain = ctrl_gain = 1
        self.ctrl_envelope = ctrl_envelope = 1
        self.ctrl_delay = ctrl_delay = 7721

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
        self.tabs.addTab(self.tabs_widget_1, 'Advanced')
        self.top_grid_layout.addWidget(self.tabs)
        self.envelope_probe = blocks.probe_signal_f()
        self._volume_range = Range(0, 2, 0.01, 0.5, 200)
        self._volume_win = RangeWidget(self._volume_range, self.set_volume, 'Volume', "counter_slider", float)
        self.top_grid_layout.addWidget(self._volume_win)
        self._tp1_gain_range = Range(0, 2, 0.01, 0.52, 200)
        self._tp1_gain_win = RangeWidget(self._tp1_gain_range, self.set_tp1_gain, 'TP1 gain', "counter_slider", float)
        self.tabs_layout_1.addWidget(self._tp1_gain_win)
        _test_tone_enable_check_box = Qt.QCheckBox('Test Tone')
        self._test_tone_enable_choices = {True: 1.0, False: 0.0}
        self._test_tone_enable_choices_inv = dict((v,k) for k,v in self._test_tone_enable_choices.items())
        self._test_tone_enable_callback = lambda i: Qt.QMetaObject.invokeMethod(_test_tone_enable_check_box, "setChecked", Qt.Q_ARG("bool", self._test_tone_enable_choices_inv[i]))
        self._test_tone_enable_callback(self.test_tone_enable)
        _test_tone_enable_check_box.stateChanged.connect(lambda i: self.set_test_tone_enable(self._test_tone_enable_choices[bool(i)]))
        self.tabs_layout_1.addWidget(_test_tone_enable_check_box)
        self._test_gain_range = Range(0, 2, 0.01, 1, 200)
        self._test_gain_win = RangeWidget(self._test_gain_range, self.set_test_gain, 'Preamp Gain', "counter_slider", float)
        self.tabs_layout_0.addWidget(self._test_gain_win)
        self._knee_point_range = Range(0, 2, 0.01, 0.2900, 200)
        self._knee_point_win = RangeWidget(self._knee_point_range, self.set_knee_point, 'Knee point', "counter_slider", float)
        self.tabs_layout_0.addWidget(self._knee_point_win)
        self._dry_range = Range(0, 1, 0.01, 1, 200)
        self._dry_win = RangeWidget(self._dry_range, self.set_dry, 'Dry', "counter_slider", float)
        self.tabs_layout_0.addWidget(self._dry_win)
        self._ctrl_gain_range = Range(1/12, 2, 0.001, 1, 200)
        self._ctrl_gain_win = RangeWidget(self._ctrl_gain_range, self.set_ctrl_gain, 'Control Gain', "counter_slider", float)
        self.tabs_layout_0.addWidget(self._ctrl_gain_win)
        def _ctrl_envelope_probe():
            while True:

                val = self.envelope_probe.level()
                try:
                    self.set_ctrl_envelope(val)
                except AttributeError:
                    pass
                time.sleep(1.0 / (ctrl_rate))
        _ctrl_envelope_thread = threading.Thread(target=_ctrl_envelope_probe)
        _ctrl_envelope_thread.daemon = True
        _ctrl_envelope_thread.start()

        self._ctrl_delay_range = Range(0, 40e3, 1, 7721, 200)
        self._ctrl_delay_win = RangeWidget(self._ctrl_delay_range, self.set_ctrl_delay, 'Control Delay', "counter_slider", float)
        self.tabs_layout_1.addWidget(self._ctrl_delay_win)
        self.zeromq_req_source_0 = zeromq.req_source(gr.sizeof_gr_complex, 1, 'tcp://localhost:5555', 1000, False, -1)
        self.rational_resampler_xxx_2 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=decimation,
                taps=None,
                fractional_bw=None)
        self.rational_resampler_xxx_1 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=decimation,
                taps=None,
                fractional_bw=None)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            86*1024, #size
            ctrl_rate, #samp_rate
            "Envelope", #name
            2 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-0.1, 2.2)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_AUTO, qtgui.TRIG_SLOPE_POS, 0.1, 0.1, 1, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
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
        alphas = [1.0, 0.3, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
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
        self.qtgui_number_sink_1 = qtgui.number_sink(
            gr.sizeof_float,
            1,
            qtgui.NUM_GRAPH_HORIZ,
            2
        )
        self.qtgui_number_sink_1.set_update_time(0.10)
        self.qtgui_number_sink_1.set_title('Output')

        labels = ['L', 'R', '', '', '',
            '', '', '', '', '']
        units = ['Vpp x10', 'Vpp x10', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(2):
            self.qtgui_number_sink_1.set_min(i, 0)
            self.qtgui_number_sink_1.set_max(i, 5)
            self.qtgui_number_sink_1.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_1.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_1.set_label(i, labels[i])
            self.qtgui_number_sink_1.set_unit(i, units[i])
            self.qtgui_number_sink_1.set_factor(i, factor[i])

        self.qtgui_number_sink_1.enable_autoscale(False)
        self._qtgui_number_sink_1_win = sip.wrapinstance(self.qtgui_number_sink_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_1_win)
        self.qtgui_number_sink_0 = qtgui.number_sink(
            gr.sizeof_float,
            1,
            qtgui.NUM_GRAPH_HORIZ,
            1
        )
        self.qtgui_number_sink_0.set_update_time(0.10)
        self.qtgui_number_sink_0.set_title('')

        labels = ['Gain', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("white", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
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
        self.tabs_layout_0.addWidget(self._qtgui_number_sink_0_win)
        self.low_pass_filter_1 = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                1,
                ctrl_rate,
                10,
                10,
                firdes.WIN_HAMMING,
                6.76))
        self.low_pass_filter_0 = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                9.3,
                ctrl_rate,
                300,
                150,
                firdes.WIN_KAISER,
                6.76))
        self.high_pass_filter_0_1 = filter.fir_filter_fff(
            decimation,
            firdes.high_pass(
                1,
                samp_rate,
                500,
                250,
                firdes.WIN_KAISER,
                6.76))
        self.high_pass_filter_0 = filter.fir_filter_fff(
            decimation,
            firdes.high_pass(
                1,
                samp_rate,
                500,
                250,
                firdes.WIN_KAISER,
                6.76))
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink('CX_decoded_output.wav', 2, round(samp_rate), 16)
        self.blocks_threshold_ff_1_1_0 = blocks.threshold_ff(0, 0, 0)
        self.blocks_threshold_ff_1_1 = blocks.threshold_ff(0, 0, 0)
        self.blocks_threshold_ff_1_0_2 = blocks.threshold_ff(diode_drop, diode_drop, 0)
        self.blocks_threshold_ff_1_0_1 = blocks.threshold_ff(-diode_drop, 0, 0)
        self.blocks_threshold_ff_1_0 = blocks.threshold_ff(0, diode_drop, 0)
        self.blocks_threshold_ff_0 = blocks.threshold_ff(diode_drop, diode_drop, 0)
        self.blocks_sub_xx_1_1 = blocks.sub_ff(1)
        self.blocks_sub_xx_1_0_0 = blocks.sub_ff(1)
        self.blocks_sub_xx_1_0 = blocks.sub_ff(1)
        self.blocks_sample_and_hold_xx_0_0_0_0 = blocks.sample_and_hold_ff()
        self.blocks_sample_and_hold_xx_0_0_0 = blocks.sample_and_hold_ff()
        self.blocks_sample_and_hold_xx_0_0 = blocks.sample_and_hold_ff()
        self.blocks_null_sink_1_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_multiply_xx_5_0_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_5_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_5 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_4_2_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_4_2 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_4_1_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_4_1 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_4_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_4 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_3 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_2 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_1_1_0_1 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_1_1_0_0_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_1_1_0_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_1_1_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_1_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_1 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vff(1)
        self.blocks_multiply_const_vxx_9_1_0 = blocks.multiply_const_ff(10)
        self.blocks_multiply_const_vxx_9_1 = blocks.multiply_const_ff(10)
        self.blocks_multiply_const_vxx_9_0 = blocks.multiply_const_ff(0.5)
        self.blocks_multiply_const_vxx_9 = blocks.multiply_const_ff(0.5)
        self.blocks_multiply_const_vxx_8_0 = blocks.multiply_const_ff(volume)
        self.blocks_multiply_const_vxx_8 = blocks.multiply_const_ff(volume)
        self.blocks_multiply_const_vxx_7 = blocks.multiply_const_ff(ctrl_envelope+dry)
        self.blocks_multiply_const_vxx_6 = blocks.multiply_const_ff(ctrl_envelope+dry)
        self.blocks_multiply_const_vxx_5 = blocks.multiply_const_ff(0.04)
        self.blocks_multiply_const_vxx_4 = blocks.multiply_const_ff(tp1_gain)
        self.blocks_multiply_const_vxx_3_0 = blocks.multiply_const_ff(test_gain)
        self.blocks_multiply_const_vxx_3 = blocks.multiply_const_ff(test_gain)
        self.blocks_multiply_const_vxx_2_1 = blocks.multiply_const_ff(-1)
        self.blocks_multiply_const_vxx_2_0_1_0_1 = blocks.multiply_const_ff(-1)
        self.blocks_multiply_const_vxx_2_0_1_0_0 = blocks.multiply_const_ff(-1)
        self.blocks_multiply_const_vxx_2_0_1_0 = blocks.multiply_const_ff(-1)
        self.blocks_multiply_const_vxx_2_0_1 = blocks.multiply_const_ff(-1)
        self.blocks_multiply_const_vxx_2_0 = blocks.multiply_const_ff(-1)
        self.blocks_multiply_const_vxx_2 = blocks.multiply_const_ff(-1)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff(ctrl_gain)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff(2)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(2)
        self.blocks_float_to_uchar_0_0_0_0 = blocks.float_to_uchar()
        self.blocks_float_to_uchar_0_0_0 = blocks.float_to_uchar()
        self.blocks_float_to_uchar_0_0 = blocks.float_to_uchar()
        self.blocks_delay_0_0_0 = blocks.delay(gr.sizeof_float*1, ctrl_delay)
        self.blocks_delay_0_0 = blocks.delay(gr.sizeof_float*1, ctrl_delay)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_float*1, ctrl_delay)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.blocks_add_xx_6 = blocks.add_vff(1)
        self.blocks_add_xx_5_0 = blocks.add_vff(1)
        self.blocks_add_xx_5 = blocks.add_vff(1)
        self.blocks_add_xx_4_0 = blocks.add_vff(1)
        self.blocks_add_xx_4 = blocks.add_vff(1)
        self.blocks_add_xx_3 = blocks.add_vff(1)
        self.blocks_add_xx_2_0 = blocks.add_vff(1)
        self.blocks_add_xx_2 = blocks.add_vff(1)
        self.blocks_add_xx_1 = blocks.add_vff(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.blocks_add_const_vxx_0_1 = blocks.add_const_ff(1)
        self.blocks_add_const_vxx_0_0_1_0_1 = blocks.add_const_ff(1)
        self.blocks_add_const_vxx_0_0_1_0_0 = blocks.add_const_ff(1)
        self.blocks_add_const_vxx_0_0_1_0 = blocks.add_const_ff(1)
        self.blocks_add_const_vxx_0_0_1 = blocks.add_const_ff(1)
        self.blocks_add_const_vxx_0_0 = blocks.add_const_ff(1)
        self.blocks_add_const_vxx_0 = blocks.add_const_ff(1)
        self.blocks_abs_xx_1_1 = blocks.abs_ff(1)
        self.blocks_abs_xx_1 = blocks.abs_ff(1)
        self.blocks_abs_xx_0_0 = blocks.abs_ff(1)
        self.blocks_abs_xx_0 = blocks.abs_ff(1)
        self.analog_sig_source_x_0_0 = analog.sig_source_f(samp_rate, analog.GR_SIN_WAVE, 876, test_gain/6, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_f(samp_rate, analog.GR_SQR_WAVE, 1/2, 1, 0, 0)
        self.analog_rail_ff_0_0_0 = analog.rail_ff(0, 15)
        self.analog_rail_ff_0_0 = analog.rail_ff(0, 15)
        self.analog_rail_ff_0 = analog.rail_ff(0, 15)
        self.analog_fm_preemph_1 = analog.fm_preemph(fs=ctrl_rate, tau=30e-3, fh=-1.0)
        self.analog_fm_deemph_0_1_0 = analog.fm_deemph(fs=ctrl_rate, tau=200e-3)
        self.analog_fm_deemph_0_1 = analog.fm_deemph(fs=ctrl_rate, tau=30e-3)
        self.analog_fm_deemph_0_0_0 = analog.fm_deemph(fs=ctrl_rate, tau=2.5e-3)
        self.analog_fm_deemph_0_0 = analog.fm_deemph(fs=ctrl_rate, tau=250e-6)
        self.analog_const_source_x_2_1 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 1-test_tone_enable)
        self.analog_const_source_x_2 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, test_tone_enable)
        self.analog_const_source_x_1 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 1)
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, knee_point)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.analog_const_source_x_1, 0), (self.blocks_multiply_xx_1_1_0_0_0, 1))
        self.connect((self.analog_const_source_x_2, 0), (self.blocks_multiply_xx_5, 1))
        self.connect((self.analog_const_source_x_2_1, 0), (self.blocks_multiply_xx_5_0, 1))
        self.connect((self.analog_const_source_x_2_1, 0), (self.blocks_multiply_xx_5_0_0, 1))
        self.connect((self.analog_fm_deemph_0_0, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.analog_fm_deemph_0_0, 0), (self.blocks_sub_xx_1_1, 0))
        self.connect((self.analog_fm_deemph_0_0_0, 0), (self.blocks_multiply_xx_1_0, 1))
        self.connect((self.analog_fm_deemph_0_0_0, 0), (self.blocks_sub_xx_1_1, 1))
        self.connect((self.analog_fm_deemph_0_1, 0), (self.blocks_multiply_xx_1_1_0, 0))
        self.connect((self.analog_fm_deemph_0_1, 0), (self.blocks_sample_and_hold_xx_0_0, 0))
        self.connect((self.analog_fm_deemph_0_1, 0), (self.blocks_sub_xx_1_0, 0))
        self.connect((self.analog_fm_deemph_0_1_0, 0), (self.blocks_multiply_xx_1_1_0_1, 0))
        self.connect((self.analog_fm_deemph_0_1_0, 0), (self.blocks_sample_and_hold_xx_0_0_0, 0))
        self.connect((self.analog_fm_deemph_0_1_0, 0), (self.blocks_sub_xx_1_0, 1))
        self.connect((self.analog_fm_preemph_1, 0), (self.blocks_multiply_xx_1_1_0_0_0, 0))
        self.connect((self.analog_rail_ff_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.analog_rail_ff_0, 0), (self.blocks_threshold_ff_0, 0))
        self.connect((self.analog_rail_ff_0_0, 0), (self.analog_fm_deemph_0_1, 0))
        self.connect((self.analog_rail_ff_0_0, 0), (self.analog_fm_deemph_0_1_0, 0))
        self.connect((self.analog_rail_ff_0_0, 0), (self.analog_fm_preemph_1, 0))
        self.connect((self.analog_rail_ff_0_0_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_2, 1))
        self.connect((self.analog_sig_source_x_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_multiply_xx_2, 0))
        self.connect((self.blocks_abs_xx_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_abs_xx_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.blocks_abs_xx_1, 0), (self.blocks_multiply_const_vxx_9_1, 0))
        self.connect((self.blocks_abs_xx_1_1, 0), (self.blocks_multiply_const_vxx_9_1_0, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_multiply_xx_1_0, 0))
        self.connect((self.blocks_add_const_vxx_0_0, 0), (self.blocks_add_xx_4_0, 1))
        self.connect((self.blocks_add_const_vxx_0_0, 0), (self.blocks_float_to_uchar_0_0_0, 0))
        self.connect((self.blocks_add_const_vxx_0_0, 0), (self.blocks_multiply_xx_1_1_0_1, 1))
        self.connect((self.blocks_add_const_vxx_0_0_1, 0), (self.blocks_threshold_ff_1_0_2, 0))
        self.connect((self.blocks_add_const_vxx_0_0_1_0, 0), (self.blocks_float_to_uchar_0_0_0_0, 0))
        self.connect((self.blocks_add_const_vxx_0_0_1_0_0, 0), (self.blocks_multiply_xx_4_1_0, 0))
        self.connect((self.blocks_add_const_vxx_0_0_1_0_1, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.blocks_add_const_vxx_0_1, 0), (self.blocks_multiply_xx_4_2_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.analog_fm_deemph_0_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.analog_fm_deemph_0_0_0, 0))
        self.connect((self.blocks_add_xx_1, 0), (self.low_pass_filter_0, 0))
        self.connect((self.blocks_add_xx_2, 0), (self.analog_rail_ff_0_0, 0))
        self.connect((self.blocks_add_xx_2_0, 0), (self.blocks_add_xx_5, 1))
        self.connect((self.blocks_add_xx_3, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.blocks_add_xx_3, 0), (self.blocks_multiply_const_vxx_3, 0))
        self.connect((self.blocks_add_xx_4, 0), (self.blocks_multiply_xx_1_1_0_0, 0))
        self.connect((self.blocks_add_xx_4_0, 0), (self.blocks_multiply_const_vxx_2_0_1, 0))
        self.connect((self.blocks_add_xx_5, 0), (self.blocks_add_xx_5_0, 1))
        self.connect((self.blocks_add_xx_5_0, 0), (self.low_pass_filter_1, 0))
        self.connect((self.blocks_add_xx_6, 0), (self.blocks_delay_0_0_0, 0))
        self.connect((self.blocks_add_xx_6, 0), (self.blocks_multiply_const_vxx_3_0, 0))
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_multiply_xx_5_0, 0))
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_multiply_xx_5_0_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_null_sink_1_0, 1))
        self.connect((self.blocks_delay_0, 0), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.blocks_delay_0_0, 0), (self.blocks_multiply_const_vxx_7, 0))
        self.connect((self.blocks_delay_0_0_0, 0), (self.blocks_multiply_const_vxx_6, 0))
        self.connect((self.blocks_float_to_uchar_0_0, 0), (self.blocks_sample_and_hold_xx_0_0, 1))
        self.connect((self.blocks_float_to_uchar_0_0_0, 0), (self.blocks_sample_and_hold_xx_0_0_0, 1))
        self.connect((self.blocks_float_to_uchar_0_0_0_0, 0), (self.blocks_sample_and_hold_xx_0_0_0_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_multiply_xx_4_2, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_sub_xx_1_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_multiply_xx_4_2_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_sub_xx_1_0_0, 1))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.envelope_probe, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.qtgui_number_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_multiply_const_vxx_2, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_2_0, 0), (self.blocks_add_const_vxx_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_2_0_1, 0), (self.blocks_add_const_vxx_0_0_1, 0))
        self.connect((self.blocks_multiply_const_vxx_2_0_1_0, 0), (self.blocks_add_const_vxx_0_0_1_0, 0))
        self.connect((self.blocks_multiply_const_vxx_2_0_1_0_0, 0), (self.blocks_add_const_vxx_0_0_1_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_2_0_1_0_1, 0), (self.blocks_add_const_vxx_0_0_1_0_1, 0))
        self.connect((self.blocks_multiply_const_vxx_2_1, 0), (self.blocks_add_const_vxx_0_1, 0))
        self.connect((self.blocks_multiply_const_vxx_3, 0), (self.high_pass_filter_0, 0))
        self.connect((self.blocks_multiply_const_vxx_3_0, 0), (self.high_pass_filter_0_1, 0))
        self.connect((self.blocks_multiply_const_vxx_4, 0), (self.analog_rail_ff_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_5, 0), (self.blocks_add_xx_5_0, 0))
        self.connect((self.blocks_multiply_const_vxx_6, 0), (self.blocks_multiply_const_vxx_8, 0))
        self.connect((self.blocks_multiply_const_vxx_7, 0), (self.blocks_multiply_const_vxx_8_0, 0))
        self.connect((self.blocks_multiply_const_vxx_8, 0), (self.blocks_multiply_const_vxx_9_0, 0))
        self.connect((self.blocks_multiply_const_vxx_8_0, 0), (self.blocks_multiply_const_vxx_9, 0))
        self.connect((self.blocks_multiply_const_vxx_9, 0), (self.blocks_abs_xx_1, 0))
        self.connect((self.blocks_multiply_const_vxx_9, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_9_0, 0), (self.blocks_abs_xx_1_1, 0))
        self.connect((self.blocks_multiply_const_vxx_9_0, 0), (self.blocks_wavfile_sink_0, 1))
        self.connect((self.blocks_multiply_const_vxx_9_1, 0), (self.qtgui_number_sink_1, 0))
        self.connect((self.blocks_multiply_const_vxx_9_1_0, 0), (self.qtgui_number_sink_1, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_xx_1, 0), (self.blocks_add_xx_2, 0))
        self.connect((self.blocks_multiply_xx_1_0, 0), (self.blocks_add_xx_2, 1))
        self.connect((self.blocks_multiply_xx_1_1_0, 0), (self.blocks_add_xx_2_0, 0))
        self.connect((self.blocks_multiply_xx_1_1_0_0, 0), (self.blocks_add_xx_5, 0))
        self.connect((self.blocks_multiply_xx_1_1_0_0_0, 0), (self.blocks_multiply_const_vxx_5, 0))
        self.connect((self.blocks_multiply_xx_1_1_0_1, 0), (self.blocks_add_xx_2_0, 1))
        self.connect((self.blocks_multiply_xx_2, 0), (self.blocks_multiply_xx_5, 0))
        self.connect((self.blocks_multiply_xx_2, 0), (self.rational_resampler_xxx_2, 0))
        self.connect((self.blocks_multiply_xx_3, 0), (self.blocks_multiply_const_vxx_2_0_1_0_0, 0))
        self.connect((self.blocks_multiply_xx_3, 0), (self.blocks_multiply_xx_4_1, 0))
        self.connect((self.blocks_multiply_xx_4, 0), (self.blocks_add_xx_4, 0))
        self.connect((self.blocks_multiply_xx_4_0, 0), (self.blocks_add_xx_4, 1))
        self.connect((self.blocks_multiply_xx_4_1, 0), (self.blocks_multiply_xx_4, 1))
        self.connect((self.blocks_multiply_xx_4_1_0, 0), (self.blocks_multiply_xx_4_0, 1))
        self.connect((self.blocks_multiply_xx_4_2, 0), (self.blocks_add_xx_1, 0))
        self.connect((self.blocks_multiply_xx_4_2_0, 0), (self.blocks_add_xx_1, 1))
        self.connect((self.blocks_multiply_xx_5, 0), (self.blocks_add_xx_3, 1))
        self.connect((self.blocks_multiply_xx_5, 0), (self.blocks_add_xx_6, 1))
        self.connect((self.blocks_multiply_xx_5_0, 0), (self.blocks_add_xx_3, 0))
        self.connect((self.blocks_multiply_xx_5_0_0, 0), (self.blocks_add_xx_6, 0))
        self.connect((self.blocks_sample_and_hold_xx_0_0, 0), (self.blocks_multiply_xx_4, 0))
        self.connect((self.blocks_sample_and_hold_xx_0_0_0, 0), (self.blocks_multiply_xx_4_0, 0))
        self.connect((self.blocks_sample_and_hold_xx_0_0_0_0, 0), (self.blocks_multiply_xx_3, 0))
        self.connect((self.blocks_sub_xx_1_0, 0), (self.blocks_threshold_ff_1_0, 0))
        self.connect((self.blocks_sub_xx_1_0, 0), (self.blocks_threshold_ff_1_0_1, 0))
        self.connect((self.blocks_sub_xx_1_0_0, 0), (self.blocks_threshold_ff_1_1_0, 0))
        self.connect((self.blocks_sub_xx_1_1, 0), (self.blocks_threshold_ff_1_1, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.blocks_multiply_const_vxx_2_0_1_0_1, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_threshold_ff_1_0, 0), (self.blocks_add_xx_4_0, 0))
        self.connect((self.blocks_threshold_ff_1_0, 0), (self.blocks_float_to_uchar_0_0, 0))
        self.connect((self.blocks_threshold_ff_1_0, 0), (self.blocks_multiply_xx_1_1_0, 1))
        self.connect((self.blocks_threshold_ff_1_0, 0), (self.blocks_sample_and_hold_xx_0_0_0_0, 0))
        self.connect((self.blocks_threshold_ff_1_0_1, 0), (self.blocks_multiply_const_vxx_2_0, 0))
        self.connect((self.blocks_threshold_ff_1_0_2, 0), (self.blocks_multiply_const_vxx_2_0_1_0, 0))
        self.connect((self.blocks_threshold_ff_1_0_2, 0), (self.blocks_multiply_xx_1_1_0_0, 1))
        self.connect((self.blocks_threshold_ff_1_0_2, 0), (self.blocks_multiply_xx_3, 1))
        self.connect((self.blocks_threshold_ff_1_0_2, 0), (self.blocks_multiply_xx_4_1, 1))
        self.connect((self.blocks_threshold_ff_1_0_2, 0), (self.blocks_multiply_xx_4_1_0, 1))
        self.connect((self.blocks_threshold_ff_1_1, 0), (self.blocks_multiply_const_vxx_2, 0))
        self.connect((self.blocks_threshold_ff_1_1, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_threshold_ff_1_1_0, 0), (self.blocks_multiply_const_vxx_2_1, 0))
        self.connect((self.blocks_threshold_ff_1_1_0, 0), (self.blocks_multiply_xx_4_2, 1))
        self.connect((self.high_pass_filter_0, 0), (self.blocks_abs_xx_0, 0))
        self.connect((self.high_pass_filter_0_1, 0), (self.blocks_abs_xx_0_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_rail_ff_0, 0))
        self.connect((self.low_pass_filter_1, 0), (self.blocks_multiply_const_vxx_4, 0))
        self.connect((self.low_pass_filter_1, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.blocks_null_sink_1_0, 0))
        self.connect((self.rational_resampler_xxx_2, 0), (self.blocks_delay_0, 0))
        self.connect((self.zeromq_req_source_0, 0), (self.blocks_complex_to_float_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "CX_NR")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_ctrl_rate(round(self.samp_rate/self.decimation))
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.high_pass_filter_0.set_taps(firdes.high_pass(1, self.samp_rate, 500, 250, firdes.WIN_KAISER, 6.76))
        self.high_pass_filter_0_1.set_taps(firdes.high_pass(1, self.samp_rate, 500, 250, firdes.WIN_KAISER, 6.76))

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.set_ctrl_rate(round(self.samp_rate/self.decimation))

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.blocks_multiply_const_vxx_8.set_k(self.volume)
        self.blocks_multiply_const_vxx_8_0.set_k(self.volume)

    def get_tp1_gain(self):
        return self.tp1_gain

    def set_tp1_gain(self, tp1_gain):
        self.tp1_gain = tp1_gain
        self.blocks_multiply_const_vxx_4.set_k(self.tp1_gain)

    def get_test_tone_enable(self):
        return self.test_tone_enable

    def set_test_tone_enable(self, test_tone_enable):
        self.test_tone_enable = test_tone_enable
        self._test_tone_enable_callback(self.test_tone_enable)
        self.analog_const_source_x_2.set_offset(self.test_tone_enable)
        self.analog_const_source_x_2_1.set_offset(1-self.test_tone_enable)

    def get_test_gain(self):
        return self.test_gain

    def set_test_gain(self, test_gain):
        self.test_gain = test_gain
        self.analog_sig_source_x_0_0.set_amplitude(self.test_gain/6)
        self.blocks_multiply_const_vxx_3.set_k(self.test_gain)
        self.blocks_multiply_const_vxx_3_0.set_k(self.test_gain)

    def get_min_average(self):
        return self.min_average

    def set_min_average(self, min_average):
        self.min_average = min_average

    def get_knee_point(self):
        return self.knee_point

    def set_knee_point(self, knee_point):
        self.knee_point = knee_point
        self.analog_const_source_x_0.set_offset(self.knee_point)

    def get_dry(self):
        return self.dry

    def set_dry(self, dry):
        self.dry = dry
        self.blocks_multiply_const_vxx_6.set_k(self.ctrl_envelope+self.dry)
        self.blocks_multiply_const_vxx_7.set_k(self.ctrl_envelope+self.dry)

    def get_diode_drop(self):
        return self.diode_drop

    def set_diode_drop(self, diode_drop):
        self.diode_drop = diode_drop
        self.blocks_threshold_ff_0.set_hi(self.diode_drop)
        self.blocks_threshold_ff_0.set_lo(self.diode_drop)
        self.blocks_threshold_ff_1_0.set_hi(self.diode_drop)
        self.blocks_threshold_ff_1_0_1.set_lo(-self.diode_drop)
        self.blocks_threshold_ff_1_0_2.set_hi(self.diode_drop)
        self.blocks_threshold_ff_1_0_2.set_lo(self.diode_drop)

    def get_ctrl_rate(self):
        return self.ctrl_rate

    def set_ctrl_rate(self, ctrl_rate):
        self.ctrl_rate = ctrl_rate
        self.low_pass_filter_0.set_taps(firdes.low_pass(9.3, self.ctrl_rate, 300, 150, firdes.WIN_KAISER, 6.76))
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.ctrl_rate, 10, 10, firdes.WIN_HAMMING, 6.76))
        self.qtgui_time_sink_x_0.set_samp_rate(self.ctrl_rate)

    def get_ctrl_gain(self):
        return self.ctrl_gain

    def set_ctrl_gain(self, ctrl_gain):
        self.ctrl_gain = ctrl_gain
        self.blocks_multiply_const_vxx_1.set_k(self.ctrl_gain)

    def get_ctrl_envelope(self):
        return self.ctrl_envelope

    def set_ctrl_envelope(self, ctrl_envelope):
        self.ctrl_envelope = ctrl_envelope
        self.blocks_multiply_const_vxx_6.set_k(self.ctrl_envelope+self.dry)
        self.blocks_multiply_const_vxx_7.set_k(self.ctrl_envelope+self.dry)

    def get_ctrl_delay(self):
        return self.ctrl_delay

    def set_ctrl_delay(self, ctrl_delay):
        self.ctrl_delay = ctrl_delay
        self.blocks_delay_0.set_dly(self.ctrl_delay)
        self.blocks_delay_0_0.set_dly(self.ctrl_delay)
        self.blocks_delay_0_0_0.set_dly(self.ctrl_delay)





def main(top_block_cls=CX_NR, options=None):

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
