import multiprocessing as mp
from multiprocessing import Process, Value, Lock
import time
import os
import sys
from tabulate import tabulate
import ctypes
import random

NUM_BARRIERS = 10  # Reduced number of iterations
P = 8
BASE_WORK_TIME = 1.5   # Base work time
BASE_BARRIER_TIME = 0.7  # Base barrier time

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_progress_bar(progress, width=30):
    filled = int(width * progress)
    bar = '█' * filled + '▒' * (width - filled)
    percentage = progress * 100
    return f'[{bar}] {percentage:.1f}%'

def worker_process(process_id, shared_times, status_queue):
    local_times = []
    
    for barrier_num in range(NUM_BARRIERS):
        # Add random deviation
        work_time = BASE_WORK_TIME * (1 + random.uniform(-0.3, 0.3))
        barrier_time = BASE_BARRIER_TIME * (1 + random.uniform(-0.2, 0.2))
        
        start = time.perf_counter()
        
        # Simulate work with progress and random deviations
        for i in range(11):
            status_queue.put({
                'process_id': process_id,
                'barrier': barrier_num,
                'progress': i / 10,
                'state': 'working'
            })
            time.sleep(work_time / 10)
        
        # Barrier synchronization with random deviations
        status_queue.put({
            'process_id': process_id,
            'barrier': barrier_num,
            'progress': 1,
            'state': 'synchronizing'
        })
        time.sleep(barrier_time)
        
        elapsed = time.perf_counter() - start
        local_times.append(elapsed)
        
        with shared_times.get_lock():
            shared_times.value += elapsed
    
    status_queue.put({
        'process_id': process_id,
        'barrier': NUM_BARRIERS,
        'progress': 1,
        'state': 'completed'
    })

def print_status_table(thread_statuses):
    clear_terminal()
    headers = ['Process', 'Barrier', 'State', 'Progress']
    table_data = []
    
    state_color = {
        'working': '\033[1;32m⚙ Working\033[0m',
        'synchronizing': '\033[1;35m🔄 Synchronizing\033[0m',
        'completed': '\033[1;34m✓ Completed\033[0m'
    }
    
    for pid, status in thread_statuses.items():
        table_data.append([
            f"Process {pid}", 
            status['barrier'], 
            state_color.get(status['state'], status['state']),
            create_progress_bar(status['progress'])
        ])
    
    print("\n\033[1;35m=== Barrier Synchronization ===\033[0m")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    sys.stdout.flush()

def print_results_summary(shared_times, total_time):
    print("\n\033[1;35m=== Simulation Results ===\033[0m")
    
    avg_barrier_time = shared_times.value / (P * NUM_BARRIERS)
    
    summary_data = [
        ["Number of Threads", P],
        ["Number of Barrier Iterations", NUM_BARRIERS],
        ["Total Execution Time", f"{total_time:.2f} seconds"],
        ["Average Time/Barrier", f"{avg_barrier_time:.6f} seconds"],
        ["Total Barrier Time", f"{shared_times.value:.6f} seconds"]
    ]
    
    print(tabulate(summary_data, headers=["Metric", "Value"], tablefmt="grid"))

def main():
    manager = mp.Manager()
    status_queue = manager.Queue()
    shared_times = Value('d', 0.0, lock=True)
    
    processes = []
    start_total_time = time.perf_counter()
    
    for i in range(P):
        p = Process(target=worker_process, args=(i, shared_times, status_queue))
        processes.append(p)
        p.start()
    
    thread_statuses = {}
    completed_count = 0
    
    while completed_count < P:
        if not status_queue.empty():
            status = status_queue.get()
            thread_statuses[status['process_id']] = status
            print_status_table(thread_statuses)
            
            if status['state'] == 'completed':
                completed_count += 1
    
    for p in processes:
        p.join()
    
    total_time = time.perf_counter() - start_total_time
    
    print_results_summary(shared_times, total_time)

if __name__ == "__main__":
    mp.set_start_method('spawn')
    main()
