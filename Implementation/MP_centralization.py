import threading
import time

NUM_THREADS = 8
NUM_BARRIERS = 5

class CentralizedBarrier:
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.count = num_threads
        self.sense = False
        self.local_sense = threading.local()
        self.lock = threading.Lock()
        self.barrier_condition = threading.Condition(self.lock)

    def wait(self):
        with self.lock:
            # Toggle local sense for this thread
            current_sense = not self.sense
            self.local_sense.value = current_sense

            # Decrement the count of threads waiting
            self.count -= 1

            # If this is the last thread
            if self.count == 0:
                # Reset the count
                self.count = self.num_threads
                # Flip the global sense
                self.sense = current_sense
                # Wake up all waiting threads
                self.barrier_condition.notify_all()
            else:
                # Wait until the sense changes
                while self.sense != current_sense:
                    self.barrier_condition.wait()

def worker(thread_num, num_threads, barrier):
    for j in range(NUM_BARRIERS):
        time.sleep(0.0001)
        print(f"Hello World from thread {thread_num} of {num_threads}")
        
        start_time = time.time()
        # Barrier synchronization
        barrier.wait()
        end_time = time.time()
        
        # Post barrier
        time.sleep(0.0001)
        print(f"Hello World from thread {thread_num} of {num_threads} after barrier")
        
        print(f"Time spent in barrier by thread {thread_num} is {end_time - start_time}")

def main():
    # Create a centralized barrier
    barrier = CentralizedBarrier(NUM_THREADS)
    
    # Create and start threads
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=worker, args=(i, NUM_THREADS, barrier))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
