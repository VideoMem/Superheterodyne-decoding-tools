#  It does parallel filtering of the input data in threads,
#  then collects the results and applies some measures to them
#
#  The pipeline pseudocode:
#
#   Input producer: (Thread 0)
#   |   file/stdin ->
#   |     reading producer -> to_resample_blocks [one per resampling thread]
#   |       to_resample_blocks is a queue of tuples (block_id, block_data)
#   v
#   Parallel resampler: (One thread per block, N blocks, N threads)
#   |   for each [block_id, input_block] in to_resample_blocks:
#   |       [block_id, input_block] -> resampler -> [block_id, resampled_block]
#   |
#   v
#   Block Merger distributor: (Re-assembles the block sequence in a stream)
#   |   and distributes it among the filters
#   |   for each input_block in to_resample_blocks:
#   |       [block_id, input_block] -> resampler -> [block_id, resampled_block]
#   |
#   v
#   Middle consumer: (One thread per filter)
#   |   for each input_queue in filter_input_queues:
#   |       [input_queue] -> IIR filter -> [middle_output_queue]
#   |
#   v
#   Output measure consumer (Thread N):
#       for each filtered_signal in middle_output_queues:
#           [filtered_signal] -> RMS value -> [measure_queue]
#

import filterbank as fb
import numpy as np
import nearest
from threading import Thread
from queue import Queue
from time import sleep, time
from scipy import signal
from resample import Arbitrary
from scipy.io.wavfile import write


# A producer with an attached queue as output
# the input comes from somewhere else
class QueueableProducer:
    def __init__(self, queues, max_queue_depth):
        self.max_depth = max_queue_depth
        self.out_queue = queues
        self.busy_wait = 50e-3

    def check_multi_queue_depth(self):
        while True:
            level = 0
            for q in self.out_queue:
                if level < q.qsize():
                    level = q.qsize()
            if level < self.max_depth:
                break
            else:
                fb.LOG(2, '-> Waiting workers to finish')
                sleep(self.busy_wait)

    def check_queue_depth(self):
        while True:
            if self.out_queue.qsize() < self.max_depth:
                break
            else:
                fb.LOG(2, '-> Waiting worker to finish')
                sleep(self.busy_wait)


# it reads the data from file/stdin
# and it queues it with block id to resample
class DiscReader(QueueableProducer):

    def __init__(self, queues, max_queue_depth):
        super().__init__(queues, max_queue_depth)
        self.specs = fb.SSpecs()
        self.resampler = Arbitrary(self.specs.samp_rate())
        self.block_id = 0
        self.fp = open(0, 'rb')


    def read_block(self):
        if self.fp:
            data = np.fromstring(self.fp.read(read_size()), dtype=np.int16)
        else:
            fb.LOG(0, 'Cannot read stdin!')
            exit(0)
        return data

    def loop(self):
        for q in self.out_queue:
            data = self.read_block()
            q.put((self.block_id, data))
            self.block_id += 1

        self.check_multi_queue_depth()


# A producer which is also a consumer.
# It acts like a producer, but it have an input queue and an output queue
class QueueableProdCon(QueueableProducer):
    def __init__(self, o_queue, i_queue, max_queue_depth):
        super().__init__(o_queue, max_queue_depth)
        self.in_queue = i_queue


# A producer/consumer which resamples indexed data blocks
class QueueableResampler(QueueableProdCon):
    def __init__(self, o_queue, i_queue, max_queue_depth):
        super().__init__(o_queue, i_queue, max_queue_depth)
        self.specs = fb.SSpecs()
        self.resampler = Arbitrary(self.specs.samp_rate())

    def loop(self):
        block_id, data = self.in_queue.get()
        output = self.resampler.linear(data, self.specs.fs())
        self.out_queue.put((block_id, output))
        self.check_queue_depth()


# it takes the resampled indexed blocks and
# distributes it to the filter threads
class QueueableBlockMergerDC(QueueableProdCon):
    def __init__(self, o_queue, i_queue, max_queue_depth):
        super().__init__(o_queue, i_queue, max_queue_depth)
        self.block_id = 0
        self.receiver = list()
        self.DCf = fb.DC_blocking()
        self.iir_b, self.iir_a = self.DCf['handler']['iir_b'], self.DCf['handler']['iir_a']
        self.z = signal.lfilter_zi(self.iir_b, self.iir_a)

    def get_block(self, id):
        index = 0
        for block_id, data in self.receiver:
            if block_id == self.block_id:
                del self.receiver[index]
                self.block_id += 1
                return True, data
            index += 1

        return False, None

    def DC_remove(self, data):
        output, self.z = signal.lfilter(self.iir_b, self.iir_a, data, zi=self.z)
        return output

    def loop(self):
        got_it, data = self.get_block(self.block_id)
        if got_it is False:
            for q in self.in_queue:
                self.receiver.append(q.get())

        if got_it:
            # it distributes a copy of the input buffer between the input queues
            # each queue corresponds to a filter
            for q in self.out_queue:
                q.put(self.DC_remove(data))

            self.check_multi_queue_depth()


# the actual filter thread thing
class QueueableFilter(QueueableProdCon):
    def __init__(self, fltr, o_queue, i_queue, max_queue_depth):
        super().__init__(o_queue, i_queue, max_queue_depth)
        self.filter = fltr
        self.iir_b, self.iir_a = self.filter['handler']['iir_b'], self.filter['handler']['iir_a']
        self.z = signal.lfilter_zi(self.iir_b, self.iir_a)

    def loop(self):
        data = self.in_queue.get()
        output, self.z = signal.lfilter(self.iir_b, self.iir_a, data, zi=self.z)
        self.out_queue.put(output)
        self.check_queue_depth()


def loop_until_quit(callback):
    while True:
        callback()


def read_size():
    specs = fb.SSpecs()
    size = int(nearest.power(2, specs.samp_rate() / specs.ratio()))
    return size


def asMb(bytes):
    return bytes / (1024 * 1024)


def dump_signal(data, id, fid):
    audio_rate = 192000
    filename = '%d %s, %s.wav' % (id, fid['filter']['type'], fid['identifier'])
    #write(filename, audio_rate, data.astype(np.int16))


def merge(qout, filters):
    block_count = 0
    t0 = time()
    while True:
        filter_id = 0
        for q in qout:
            data = q.get()
            dump_signal(data, filter_id, filters[filter_id])
            filter_id += 1

        block_count += 1
        t1 = time()
        if block_count % 10 == 0:
            elapsed = t1 - t0
            speed = block_count * asMb(read_size()) / elapsed
            fb.LOG(0, '-> Block %d, read %.2f Mb/s' % (block_count, speed))


if __name__ == '__main__':
    fb.LOG(2, 'Reading stdin')

    max_queue_depth = 2
    resample_workers = 4

    filters = fb.filterbank()

    # setups the resampler threads
    resample_threads = list()
    resample_inq = list()
    resample_outq = list()
    for i in range(0, resample_workers):
        inq, outq = Queue(), Queue()
        resample_inq.append(inq)
        resample_outq.append(outq)
        resampler = QueueableResampler(outq, inq, max_queue_depth)
        resample_threads.append(Thread(target=loop_until_quit, args=(resampler.loop, )))

    # setups the disc reader
    input_reader = DiscReader(resample_inq, max_queue_depth)
    input_reader_t = Thread(target=loop_until_quit, args=(input_reader.loop, ))

    # setups the filters
    filter_threads = list()
    filters_inq = list()
    filters_outq = list()
    for filter in filters:
        qin, qout = Queue(), Queue()
        qfilter = QueueableFilter(filter, qout, qin, max_queue_depth)
        filter_threads.append(Thread(target=loop_until_quit, args=(qfilter.loop, )))
        filters_inq.append(qin)
        filters_outq.append(qout)


    # setups the merger + DC remover
    block_merger = QueueableBlockMergerDC(filters_inq, resample_outq, max_queue_depth)
    block_merger_t = Thread(target=loop_until_quit, args=(block_merger.loop, ))


    #starts all threads
    input_reader_t.start()

    for thread in resample_threads:
        thread.start()

    block_merger_t.start()

    for thread in filter_threads:
        thread.start()

    measure_thread = Thread(target=merge, args=(filters_outq, filters, ))
    measure_thread.start()

