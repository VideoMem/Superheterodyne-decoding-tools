from time import time, gmtime, strftime

class Benchmark:

    def __init__(self, funct, steps):
        self.testant = funct
        self.loops = steps
        self.results = 0

    def run(self, args):
        t0 = time()
        for i in range(0, int(self.loops)):
            self.testant(args)
        t1 = time()
        elapsed = t1 - t0
        self.results = self.loops / elapsed
        print('Test results: %f Iterations / sec' % self.results)

    def units(self, unit, name):
        conv = self.results * unit
        print('%f %s' % (conv, name))

