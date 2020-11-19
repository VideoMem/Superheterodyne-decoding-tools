from sys import stdin
import os
import struct
import array

def read_block16(samples):
    xf = list()
    mid = 0xFFFF / 2
    while len(xf) < samples:
        x = int.from_bytes(stdin.buffer.read(2), byteorder='little', signed=False)
        xf.append((x - mid/2) / mid)
    return xf

def osread(samples):
    return os.read(0, samples * 2)

def osread_block16(samples):
    buffer = osread(samples)
    xf = list()
    mid = 0xFFFF / 2
    offset = 0
    while len(xf) < samples:
        x = int.from_bytes(buffer[offset:2], byteorder='little', signed=False)
        xf.append((x - mid/2) / mid)
        offset += 2
    return xf


def struct_short(samples):
    buffer = osread(samples)
    mid = 0xFFFF / 2
    format = '<{}H'.format(len(buffer) / 2)
    short_array = struct.unpack(format, buffer)
    result = [(sample - mid / 2) / mid for sample in short_array]
    assert len(result) == samples
    return result


def array_short(samples):
    buffer = osread(samples)
    mid = 0xFFFF / 2
    format = 'H'
    short_array = array.array(format, buffer)
    result = [(sample - mid / 2) / mid for sample in short_array]
    assert len(result) == samples
    return result
