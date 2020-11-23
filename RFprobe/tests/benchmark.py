from tests import Tests
from time import time

class Benchmark(Tests):

    def __init__(self, funct, steps):
        super(Benchmark, self).__init__(funct)
        self.loops = steps

    def run(self, args):
        t0 = time()
        for i in range(0, int(self.loops)):
            self.test(args)
        t1 = time()
        elapsed = t1 - t0
        self.results = self.loops / elapsed
        print('Test results: %f Iterations / sec' % self.results)

    def units(self, unit, name):
        conv = self.results * unit
        print('%f %s' % (conv, name))

