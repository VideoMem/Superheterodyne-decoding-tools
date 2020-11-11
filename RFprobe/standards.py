
class LDCarriers:
    def __init__(self, Fv, lines_per_frame):
        self.fh = Fv*lines_per_frame/2
        self.fv = Fv

    def audio(self):
        values = list()
        values.append(('L', 146.25 * self.fh))
        values.append(('R', 178.75 * self.fh))

        return values
