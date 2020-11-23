from tests import Tests


class Idempotency:

    def __init__(self, A, B):
        self.A = Tests(A)
        self.B = Tests(B)

    def run(self, args):
        self.A.test(args)
        self.B.test(args)
        if self.A.get_output() != self.B.get_output():
            print('%s output does not match %s output' % (self.A.test, self.B.test))
            return False
        else:
            return True
