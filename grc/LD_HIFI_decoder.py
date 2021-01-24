#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: LaserDisc HIFI decoder
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
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
import nearest  # embedded python module
import pipe

from gnuradio import qtgui

class LD_HIFI_decoder(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "LaserDisc HIFI decoder")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("LaserDisc HIFI decoder")
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

        self.settings = Qt.QSettings("GNU Radio", "LD_HIFI_decoder")

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
        self.Fh = Fh = Fv*lines_per_frame/2
        self.samp_rate = samp_rate = 40e6
        self.center_freq = center_freq = -1987
        self.carrierR_fine = carrierR_fine = -112
        self.carrierL_fine = carrierL_fine = 0
        self.VCO_deviation = VCO_deviation = 300e3
        self.R_carrier_ref = R_carrier_ref = 178.75 * Fh
        self.L_carrier_ref = L_carrier_ref = 146.25* Fh
        self.volume = volume = 0.65
        self.sharpness = sharpness = int(VCO_deviation/2)
        self.op_VCO_deviation = op_VCO_deviation = VCO_deviation/3
        self.if_rate = if_rate = nearest.power(samp_rate/4,2)
        self.half_VCO_deviation = half_VCO_deviation = VCO_deviation/2
        self.audio_rate = audio_rate = 192e3
        self.R_carrier = R_carrier = R_carrier_ref + carrierR_fine + center_freq
        self.L_carrier = L_carrier = L_carrier_ref + carrierL_fine + center_freq
        self.FM_HPF = FM_HPF = 120

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
        self._sharpness_range = Range(int(op_VCO_deviation/4), int(VCO_deviation*2), 1, int(VCO_deviation/2), 300)
        self._sharpness_win = RangeWidget(self._sharpness_range, self.set_sharpness, 'Transition', "counter_slider", int)
        self.tabs_layout_1.addWidget(self._sharpness_win)
        self._volume_range = Range(0, 2, 0.01, 0.65, 200)
        self._volume_win = RangeWidget(self._volume_range, self.set_volume, 'Volume', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._volume_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(1, 2):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=Fraction(if_rate/samp_rate).limit_denominator(1000).numerator,
                decimation=Fraction(if_rate/samp_rate).limit_denominator(1000).denominator,
                taps=None,
                fractional_bw=None)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            8192, #size
            if_rate, #samp_rate
            "", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_AUTO, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(True)
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
        self.qtgui_number_sink_0_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1
        )
        self.qtgui_number_sink_0_0.set_update_time(0.10)
        self.qtgui_number_sink_0_0.set_title("")

        labels = ['NTSC R', '', '', '', '',
            '', '', '', '', '']
        units = ['VRMS', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0_0.set_min(i, 0)
            self.qtgui_number_sink_0_0.set_max(i, 1)
            self.qtgui_number_sink_0_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_0.set_label(i, labels[i])
            self.qtgui_number_sink_0_0.set_unit(i, units[i])
            self.qtgui_number_sink_0_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0_0.enable_autoscale(True)
        self._qtgui_number_sink_0_0_win = sip.wrapinstance(self.qtgui_number_sink_0_0.pyqwidget(), Qt.QWidget)
        self.tabs_layout_0.addWidget(self._qtgui_number_sink_0_0_win)
        self.qtgui_number_sink_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1
        )
        self.qtgui_number_sink_0.set_update_time(0.10)
        self.qtgui_number_sink_0.set_title("")

        labels = ['NTSC L', '', '', '', '',
            '', '', '', '', '']
        units = ['VRMS', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0.set_min(i, -1)
            self.qtgui_number_sink_0.set_max(i, 1)
            self.qtgui_number_sink_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0.set_label(i, labels[i])
            self.qtgui_number_sink_0.set_unit(i, units[i])
            self.qtgui_number_sink_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0.enable_autoscale(True)
        self._qtgui_number_sink_0_win = sip.wrapinstance(self.qtgui_number_sink_0.pyqwidget(), Qt.QWidget)
        self.tabs_layout_0.addWidget(self._qtgui_number_sink_0_win)
        self.pipe_source_1 = pipe.source(gr.sizeof_short*1, 'ld-ldf-reader ~/vault/Karaoke_1_CLV_NTSC.ldf')
        self._center_freq_range = Range(-10e3, 10e3, 0.1, -1987, 300)
        self._center_freq_win = RangeWidget(self._center_freq_range, self.set_center_freq, 'Center Fine', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._center_freq_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self._carrierR_fine_range = Range(-5e3, 5e3, 1, -112, 200)
        self._carrierR_fine_win = RangeWidget(self._carrierR_fine_range, self.set_carrierR_fine, 'R Fine Tune', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._carrierR_fine_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(1, 2):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self._carrierL_fine_range = Range(-5e3, 5e3, 1, 0, 200)
        self._carrierL_fine_win = RangeWidget(self._carrierL_fine_range, self.set_carrierL_fine, 'L Fine Tune', "counter_slider", float)
        self.tabs_grid_layout_0.addWidget(self._carrierL_fine_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.tabs_grid_layout_0.setRowStretch(r, 1)
        for c in range(0, 1):
            self.tabs_grid_layout_0.setColumnStretch(c, 1)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_short_to_float_0_0 = blocks.short_to_float(1, 1)
        self.blocks_rms_xx_0_0 = blocks.rms_ff(0.0001)
        self.blocks_rms_xx_0 = blocks.rms_ff(0.0001)
        self.blocks_multiply_const_vxx_5 = blocks.multiply_const_ff(1)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(round(if_rate /  FM_HPF), 1/round(if_rate / FM_HPF), 4000, 1)
        self.blocks_delay_1 = blocks.delay(gr.sizeof_float*1, round(if_rate /  FM_HPF))
        self.band_pass_filter_0_0 = filter.fir_filter_fff(
            1,
            firdes.band_pass(
                1/0xFF,
                if_rate,
                R_carrier - VCO_deviation / 2 ,
                R_carrier + VCO_deviation / 2,
                sharpness,
                firdes.WIN_KAISER,
                14))
        self.band_pass_filter_0 = filter.fir_filter_fff(
            1,
            firdes.band_pass(
                1/0xFF,
                if_rate,
                L_carrier - VCO_deviation /2,
                L_carrier + VCO_deviation /2,
                sharpness,
                firdes.WIN_KAISER,
                14))



        ##################################################
        # Connections
        ##################################################
        self.connect((self.band_pass_filter_0, 0), (self.blocks_rms_xx_0, 0))
        self.connect((self.band_pass_filter_0_0, 0), (self.blocks_rms_xx_0_0, 0))
        self.connect((self.blocks_delay_1, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_5, 0), (self.band_pass_filter_0, 0))
        self.connect((self.blocks_multiply_const_vxx_5, 0), (self.band_pass_filter_0_0, 0))
        self.connect((self.blocks_rms_xx_0, 0), (self.qtgui_number_sink_0, 0))
        self.connect((self.blocks_rms_xx_0_0, 0), (self.qtgui_number_sink_0_0, 0))
        self.connect((self.blocks_short_to_float_0_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.blocks_multiply_const_vxx_5, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.pipe_source_1, 0), (self.blocks_short_to_float_0_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_delay_1, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_moving_average_xx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "LD_HIFI_decoder")
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

    def get_Fh(self):
        return self.Fh

    def set_Fh(self, Fh):
        self.Fh = Fh
        self.set_L_carrier_ref(146.25* self.Fh)
        self.set_R_carrier_ref(178.75 * self.Fh)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_if_rate(nearest.power(self.samp_rate/4,2))

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

    def get_VCO_deviation(self):
        return self.VCO_deviation

    def set_VCO_deviation(self, VCO_deviation):
        self.VCO_deviation = VCO_deviation
        self.set_half_VCO_deviation(self.VCO_deviation/2)
        self.set_op_VCO_deviation(self.VCO_deviation/3)
        self.set_sharpness(int(self.VCO_deviation/2))
        self.band_pass_filter_0.set_taps(firdes.band_pass(1/0xFF, self.if_rate, self.L_carrier - self.VCO_deviation /2, self.L_carrier + self.VCO_deviation /2, self.sharpness, firdes.WIN_KAISER, 14))
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1/0xFF, self.if_rate, self.R_carrier - self.VCO_deviation / 2 , self.R_carrier + self.VCO_deviation / 2, self.sharpness, firdes.WIN_KAISER, 14))

    def get_R_carrier_ref(self):
        return self.R_carrier_ref

    def set_R_carrier_ref(self, R_carrier_ref):
        self.R_carrier_ref = R_carrier_ref
        self.set_R_carrier(self.R_carrier_ref + self.carrierR_fine + self.center_freq)

    def get_L_carrier_ref(self):
        return self.L_carrier_ref

    def set_L_carrier_ref(self, L_carrier_ref):
        self.L_carrier_ref = L_carrier_ref
        self.set_L_carrier(self.L_carrier_ref + self.carrierL_fine + self.center_freq)

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume

    def get_sharpness(self):
        return self.sharpness

    def set_sharpness(self, sharpness):
        self.sharpness = sharpness
        self.band_pass_filter_0.set_taps(firdes.band_pass(1/0xFF, self.if_rate, self.L_carrier - self.VCO_deviation /2, self.L_carrier + self.VCO_deviation /2, self.sharpness, firdes.WIN_KAISER, 14))
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1/0xFF, self.if_rate, self.R_carrier - self.VCO_deviation / 2 , self.R_carrier + self.VCO_deviation / 2, self.sharpness, firdes.WIN_KAISER, 14))

    def get_op_VCO_deviation(self):
        return self.op_VCO_deviation

    def set_op_VCO_deviation(self, op_VCO_deviation):
        self.op_VCO_deviation = op_VCO_deviation

    def get_if_rate(self):
        return self.if_rate

    def set_if_rate(self, if_rate):
        self.if_rate = if_rate
        self.band_pass_filter_0.set_taps(firdes.band_pass(1/0xFF, self.if_rate, self.L_carrier - self.VCO_deviation /2, self.L_carrier + self.VCO_deviation /2, self.sharpness, firdes.WIN_KAISER, 14))
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1/0xFF, self.if_rate, self.R_carrier - self.VCO_deviation / 2 , self.R_carrier + self.VCO_deviation / 2, self.sharpness, firdes.WIN_KAISER, 14))
        self.blocks_delay_1.set_dly(round(self.if_rate /  self.FM_HPF))
        self.blocks_moving_average_xx_0.set_length_and_scale(round(self.if_rate /  self.FM_HPF), 1/round(self.if_rate / self.FM_HPF))
        self.qtgui_time_sink_x_0.set_samp_rate(self.if_rate)

    def get_half_VCO_deviation(self):
        return self.half_VCO_deviation

    def set_half_VCO_deviation(self, half_VCO_deviation):
        self.half_VCO_deviation = half_VCO_deviation

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate

    def get_R_carrier(self):
        return self.R_carrier

    def set_R_carrier(self, R_carrier):
        self.R_carrier = R_carrier
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1/0xFF, self.if_rate, self.R_carrier - self.VCO_deviation / 2 , self.R_carrier + self.VCO_deviation / 2, self.sharpness, firdes.WIN_KAISER, 14))

    def get_L_carrier(self):
        return self.L_carrier

    def set_L_carrier(self, L_carrier):
        self.L_carrier = L_carrier
        self.band_pass_filter_0.set_taps(firdes.band_pass(1/0xFF, self.if_rate, self.L_carrier - self.VCO_deviation /2, self.L_carrier + self.VCO_deviation /2, self.sharpness, firdes.WIN_KAISER, 14))

    def get_FM_HPF(self):
        return self.FM_HPF

    def set_FM_HPF(self, FM_HPF):
        self.FM_HPF = FM_HPF
        self.blocks_delay_1.set_dly(round(self.if_rate /  self.FM_HPF))
        self.blocks_moving_average_xx_0.set_length_and_scale(round(self.if_rate /  self.FM_HPF), 1/round(self.if_rate / self.FM_HPF))





def main(top_block_cls=LD_HIFI_decoder, options=None):

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
