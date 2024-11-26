import multiprocessing
import time

NUM_THREADS = 8
NUM_BARRIERS = 10

def centralized_barrier(count, sense, local_sense):
    time.sleep(0.001)  
    local_sense.value = not local_sense.value
    
    with count.get_lock():
        count.value -= 1
    
    if count.value == 0:
        count.value = NUM_THREADS
        sense.value = local_sense.value
    else:
        while sense.value != local_sense.value:
            pass

def worker(thread_num, num_threads, count, sense, local_sense):
    for j in range(NUM_BARRIERS):
     
        time.sleep(0.0001)
        print(f"Hello World from thread {thread_num} of {num_threads}")
        
        start_time = time.time()
        # Barrier
        centralized_barrier(count, sense, local_sense)
        end_time = time.time()
        
        # Sau barrier
        time.sleep(0.0001)
        print(f"Hello World from thread {thread_num} of {num_threads} after barrier")
        
        print(f"Time spent in barrier by thread {thread_num} is {end_time - start_time}")

if __name__ == "__main__":
   
    count = multiprocessing.Value('i', NUM_THREADS)
    sense = multiprocessing.Value('b', True)
    

    processes = []
    for i in range(NUM_THREADS):
        local_sense = multiprocessing.Value('b', True)
        p = multiprocessing.Process(target=worker, args=(i, NUM_THREADS, count, sense, local_sense))
        processes.append(p)
        p.start()
    

    for p in processes:
        p.join()
