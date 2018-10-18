'''
Created on Oct 17, 2018

@author: carlos

this is an exmple of how to use sevral threads through crunch through data set in parallel way,...

in this example we will be multiplying a bunch of values by 2

'''
from queue import Queue, Empty  # in python 2.7 import from Queue
from threading import Thread
import multiprocessing

# define data (1000 random numbers)
DATA = [index for index in range(1000)]


# put DATA to be processed in  a thread safe iterator (Queue)
DATA_QUE = Queue()
for index, val in enumerate(DATA):
    tpl_data = index, val
    DATA_QUE.put(tpl_data)

# define number of threads
NUMBER_THREADS = multiprocessing.cpu_count()

# allocate list to store outputs into
OUTPUT = [None] * DATA_QUE.qsize()

# define method for data manipulation


def _worker_method():
    while True:
        # pull a value to process form the queue if the que is empty exit thread
        try:
            index, val = DATA_QUE.get_nowait()
        except Empty:
            # Protect against a race condition where another thread dequeues the last item before this thread gets it
            break

        # if we get a value then let's multiply it and store the results in output array
        OUTPUT[index] = val * 2
        # mark task as finished
        DATA_QUE.task_done()


# make sure number of threads is not larger than data set size
if NUMBER_THREADS > len(DATA):
    NUMBER_THREADS = len(DATA)

# start some threads
THREADS = []
for _ in range(NUMBER_THREADS):
    thread = Thread(target=_worker_method)
    THREADS.append(thread)
    thread.start()

# wait for all threads to finish
DATA_QUE.join()
# print values for visual check
print(DATA)
print(OUTPUT)
