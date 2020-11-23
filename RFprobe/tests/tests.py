from time import time


class Tests:

    def __init__(self, funct):
        self.test = funct
        self.output = 0
        self.results = 0

    def run(self, args):
        t0 = time()
        self.output = self.test(args)
        t1 = time()
        elapsed = t1 - t0
        self.results = 1 / elapsed
        print('Test results: %f Iterations / sec' % self.results)

    def get_output(self):
        return self.output