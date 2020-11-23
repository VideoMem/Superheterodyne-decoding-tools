import stdin
from benchmark import Benchmark
from idempotency import Idempotency
from readfile import ReadFile

def idem(f0, f1, args):
    print('Testing %s vs %s' % (f0, f1))
    t = Idempotency(f0, f1)
    return t.run(args)

def bench(funct, args, iters, units, name):
    print('Testing %s' % funct)
    b = Benchmark(funct, iters)
    b.run(args)
    b.units(units, name)

def asMb(bytes):
    return bytes / (1024 * 1024)

def run_benchmarks(size, iters):
    #benchmarks
    bench(stdin.read_block16, size, iters, asMb(size), 'MBytes/s')
    bench(stdin.osread, size, iters, asMb(size), 'MBytes/s')
    bench(stdin.osread_block16, size, iters, asMb(size), 'MBytes/s')
    bench(stdin.struct_short, size, iters, asMb(size), 'MBytes/s')
    bench(stdin.array_short, size, iters, asMb(size), 'MBytes/s')
    readf = ReadFile('/dev/zero', size)
    bench(readf.read, size, iters, asMb(size), 'MBytes/s')


def run_idempotency_tests(size):
    to_compare = { stdin.read_block16, stdin.osread_block16, stdin.struct_short, stdin.array_short }
    for test in to_compare:
        if idem(stdin.read_block16, test, size):
            print('checks Ok')


if __name__ == "__main__":
    size = 256
    iters = int(10 * 1024*1024 / size)  # it reads 10Mb in (size) chunks

    run_idempotency_tests(size)
    run_benchmarks(size, iters)
