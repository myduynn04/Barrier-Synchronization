import multiprocessing as mp
from multiprocessing import Process, Value, RawArray, Lock
import time
import math
from array import array
import ctypes
from threading import Barrier, Thread
import queue
from contextlib import contextmanager

# Configuration
NUM_BARRIERS = 100
P = 2  # number of threads/processes
SLEEP_TIME = 0.0001
MAX_BACKOFF = 0.001
BASE_BACKOFF = 0.000001  # Start with smaller initial backoff

class OptimizedFlags:
    def __init__(self, size):
        # Use ctypes arrays for direct memory access
        self.myflags = [RawArray(ctypes.c_int, size) for _ in range(2)]
        self.partnerflags = [[RawArray(ctypes.c_int, 1) for _ in range(size)] for _ in range(2)]
        self._size = size
        
    @contextmanager
    def flag_operation(self):
        """Context manager for safe flag operations"""
        try:
            yield
        finally:
            pass
    
    def set_flag(self, parity, index, value):
        with self.flag_operation():
            self.myflags[parity][index] = value
        
    def get_flag(self, parity, index):
        with self.flag_operation():
            return self.myflags[parity][index]

class OptimizedBarrier:
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.count = Value(ctypes.c_int, 0, lock=True)  # Use lock=True for atomic operations
        self.generation = Value(ctypes.c_int, 0, lock=True)
        self.lock = Lock()
        
    def wait(self):
        gen = self.generation.value
        
        with self.count.get_lock():
            self.count.value += 1
            if self.count.value == self.num_threads:
                self.count.value = 0
                self.generation.value += 1
                return
            
        # Exponential backoff while waiting
        backoff = BASE_BACKOFF
        while gen == self.generation.value:
            time.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)

def optimized_dissemination_barrier(local_flags, sense, parity, proc, lock):
    """Optimized dissemination barrier with improved synchronization"""
    p = parity.value
    
    # Pre-calculate partner indices and use round-robin distribution
    partner_indices = [(proc + ((1 << i) + proc - 1)) % proc for i in range(int(math.log2(proc)) + 1)]
    
    for i, partner in enumerate(partner_indices):
        # Signal partner with atomic operation
        local_flags.set_flag(p, i, sense.value)
        
        # Efficient waiting with adaptive backoff
        backoff = BASE_BACKOFF
        while local_flags.get_flag(p, i) != sense.value:
            time.sleep(backoff)
            backoff = min(backoff * 1.5, MAX_BACKOFF)  # Gentler backoff increase
            
            # Add a yield point for better CPU utilization
            if backoff >= MAX_BACKOFF / 2:
                time.sleep(0)
    
    # Atomic sense and parity updates
    with lock:
        if p == 1:
            sense.value = not sense.value
        parity.value = 1 - p

class BarrierManager:
    """Manager class for coordinating barrier operations"""
    def __init__(self, num_participants):
        self.num_participants = num_participants
        self.shared_barrier = OptimizedBarrier(num_participants)
        self.shared_time = Value('d', 0.0, lock=True)
        
    def get_barrier(self):
        return self.shared_barrier
    
    def get_shared_time(self):
        return self.shared_time

def worker_thread(thread_id, barrier, results_queue):
    """Optimized worker thread with local timing"""
    local_time = 0
    times = []  # Store individual timings for analysis
    
    for _ in range(NUM_BARRIERS):
        start = time.perf_counter_ns()  # Use nanosecond precision
        barrier.wait()
        elapsed = (time.perf_counter_ns() - start) / 1e9  # Convert to seconds
        local_time += elapsed
        times.append(elapsed)
    
    results_queue.put((local_time, times))

def worker_process(process_id, num_processes, barrier_manager):
    """Optimized worker process with improved synchronization"""
    proc = math.ceil(math.log2(num_processes))
    local_flags = OptimizedFlags(proc)
    sense = Value(ctypes.c_bool, True, lock=True)
    parity = Value(ctypes.c_bool, False, lock=True)
    lock = Lock()
    
    # Initialize flags
    for p in range(2):
        for i in range(proc):
            local_flags.set_flag(p, i, False)
    
    local_time = 0
    times = []
    
    for _ in range(NUM_BARRIERS):
        start = time.perf_counter_ns()
        optimized_dissemination_barrier(local_flags, sense, parity, proc, lock)
        elapsed = (time.perf_counter_ns() - start) / 1e9
        local_time += elapsed
        times.append(elapsed)
        
    with barrier_manager.get_shared_time().get_lock():
        barrier_manager.get_shared_time().value += local_time

def main():
    # Thread-based execution
    print("Running thread-based barrier test...")
    barrier = Barrier(P)
    results_queue = queue.Queue()
    threads = []
    
    start_time = time.perf_counter()
    
    for i in range(P):
        t = Thread(target=worker_thread, args=(i, barrier, results_queue))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
        
    thread_results = [results_queue.get() for _ in range(P)]
    thread_time = sum(r[0] for r in thread_results) / P
    
    print(f"Average thread barrier time: {thread_time/NUM_BARRIERS:.9f} seconds")
    
    # Process-based execution
    print("\nRunning process-based barrier test...")
    barrier_manager = BarrierManager(P)
    processes = []
    
    start_time = time.perf_counter()
    
    for i in range(P):
        p = Process(target=worker_process, args=(i, P, barrier_manager))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
        
    total_time = time.perf_counter() - start_time
    avg_barrier_time = barrier_manager.get_shared_time().value / (P * NUM_BARRIERS)
    
    print(f"Average process barrier time: {avg_barrier_time:.9f} seconds")
    print(f"Total execution time: {total_time:.6f} seconds")

if __name__ == "__main__":
    mp.set_start_method('spawn')  # Use spawn for better process isolation
    main()
