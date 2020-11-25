from sys import argv, stdout
from struct import pack
from numpy import array

def gen_uint16_t(length):
    block = list()
    step = 0xFFFF / length
    for x in range(0, length):
        y = step * x
        block.append(round(y))

    block[length - 1] = 0xFFFF
    assert len(block) == length

    return block

def short_char(shorts):
    chars = list()

    for short in shorts:
        msb = int(short / 0x100)
        lsb = short & 0x00FF
        chars.append(msb)
        chars.append(lsb)

    assert len(chars) == 2 * len(shorts)
    return chars

if __name__ == "__main__":
    print('size:', argv[1])
    block = short_char(gen_uint16_t(int(argv[1])))
    while True:
        stdout.write(block.decode('utf-8'))
        #print('%s' % block)