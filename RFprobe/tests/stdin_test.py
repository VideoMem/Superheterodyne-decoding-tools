import stdin
from benchmark import Benchmark
from readfile import ReadFile

def test(funct, args, iters, units, name):
    print('Testing %s' % funct)
    b = Benchmark(stdin.read_block16, iters)
    b.run(args)
    b.units(units, name)

def asMb(bytes):
    return bytes / (1024 * 1024)

if __name__ == "__main__":
    size = 256
    iters = int(10 * 1024*1024 / size)  # it reads 10Mb

    test(stdin.read_block16, size, iters, asMb(size), 'MBytes/s')
    test(stdin.osread, size, iters, asMb(size), 'MBytes/s')
    test(stdin.osread_block16, size, iters, asMb(size), 'MBytes/s')
    test(stdin.struct_short, size, iters, asMb(size), 'MBytes/s')
    test(stdin.array_short, size, iters, asMb(size), 'MBytes/s')
    readf = ReadFile('/dev/zero', size)
    test(readf.read, size, iters, asMb(size), 'MBytes/s')
