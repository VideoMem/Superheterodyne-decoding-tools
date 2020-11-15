

class LDCarriers:
    def __init__(self, fh):
        self.fh = fh

    def audioNTSC(self):
        return {
            'L': 146.25 * self.fh,
            'R': 178.75 * self.fh,
            'AC3': 182.86 * self.fh
        }

    def efm(self):
        return {
            'L': 196e3,
            'H': 720e3
        }
