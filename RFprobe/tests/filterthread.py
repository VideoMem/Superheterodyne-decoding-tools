#  It does parallel filtering of the input data in threads,
#  then collects the results and applies some measures to them
#
#  The pipeline:
#
#   Input producer: (Thread 0)
#   |   file/stdin ->
#   |     reading producer / resampler / DC remover -> filter_input_queues [one per filter]
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


# A producer with an attached queue of queues as output
# each queue corresponds to a filter and a thread
class QueueableProducer:
    def __init__(self, queues, max_queue_depth):
        self.max_depth = max_queue_depth
        self.out_queue = queues
        self.idle_wait = 50e-3

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
                sleep(self.idle_wait)

    def check_queue_depth(self):
        while True:
            if self.out_queue.qsize() < self.max_depth:
                break
            else:
                fb.LOG(2, '-> Queue full, waiting worker to finish')
                sleep(self.idle_wait)


# it reads the data from file/stdin
class DiscReader(QueueableProducer):

    def __init__(self, queues, max_queue_depth):
        super().__init__(queues, max_queue_depth)
        self.specs = fb.SSpecs()
        self.resampler = Arbitrary(self.specs.samp_rate())

    def loop(self):
        data = read_block()

        # it distributes a copy of the input buffer between the input queues
        # each queue corresponds to a filter
        for q in self.out_queue:
            data_resampled = self.resampler.linear(data, self.specs.fs())
            fb.LOG(2, 'Read size %d -> data resampled size %d' % (len(data), len(data_resampled)))
            q.put(data_resampled)

        self.check_multi_queue_depth()


# A producer which is also a consumer.
# It acts like a producer, but it have an input queue and an output queue
class QueueableProdCon(QueueableProducer):
    def __init__(self, o_queue, i_queue, max_queue_depth):
        super().__init__(o_queue, max_queue_depth)
        self.in_queue = i_queue


# A producer/consumer which resamples indexed blocks
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



# the actual filter thread thing
class QueueableFilter(QueueableProdCon):
    def __init__(self, fltr, o_queue, i_queue, max_queue_depth):
        super().__init__(o_queue, i_queue, max_queue_depth)
        self.filter = fltr
        self.iir_b, self.iir_a = self.filter['handler']['iir_b'], self.filter['handler']['iir_a']
        self.z = signal.lfilter_zi(self.iir_b, self.iir_a)

    def loop(self):
        self.z = signal.lfilter_zi(self.iir_b, self.iir_a)
        data = self.in_queue.get()
        output, z = signal.lfilter(self.iir_b, self.iir_a, data, zi=self.z)
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


def read_block():
    fp = open('/dev/stdin', 'rb')
    with fp as binfile:
        data = np.fromstring(binfile.read(read_size()), dtype=np.int16)
    fp.close()
    return data


def dump_signal(data, id):
    with open('%d.raw' % id, 'wb') as f:
        np.save(f, data)
        del data


def merge(qout):
    block_count = 0
    t0 = time()
    while True:
        filter_id = 0
        for q in qout:
            data = q.get()
            #dump_signal(data, filter_id)
            filter_id += 1

        block_count += 1
        t1 = time()
        if block_count % 10 == 0:
            elapsed = t1 - t0
            speed = block_count * asMb(read_size()) / elapsed
            fb.LOG(0, '-> Block %d, read %.2f Mb/s' % (block_count, speed))


if __name__ == '__main__':
    max_queue_depth = 2
    filters = fb.filterbank()
    worker_list = list()
    input_queues = list()
    output_queues = list()

    fb.LOG(2, 'Reading stdin')
    for filter in filters:
        qin = Queue()
        qout = Queue()
        qfilter = QueueableFilter(filter, qout, qin, max_queue_depth)
        worker_list.append(Thread(target=loop_until_quit, args=(qfilter.loop, )))
        input_queues.append(qin)
        output_queues.append(qout)

    input_reader = DiscReader(input_queues, max_queue_depth)
    producer_thread = Thread(target=loop_until_quit, args=(input_reader.loop, ))

    producer_thread.start()

    for thread in worker_list:
        thread.start()

    measure_thread = Thread(target=merge, args=(output_queues,))
    measure_thread.start()

    # while True:
    #    produce(input_queues)
