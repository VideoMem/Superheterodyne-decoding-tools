import struct

def as_float(twobyte):
    return struct.unpack('f', twobyte)[0]


class ReadFile:

    def __init__(self, fname):
        self.hs = open(fname, 'rb')

    def __del__(self):
        self.hs.close()

    def get(self):
        eof = False
        read = 0
        while True:
            try:
                read = as_float(self.hs.read(4))
                break
            except (struct.error, IOError) as e:
                eof = True
                break

        return read, eof
