import multiprocessing
import time
import os
from datetime import datetime
from tabulate import tabulate
import sys
import random
from typing import Dict  # Keep this import

NUM_PROCESSES = 8
NUM_BARRIERS = 5  # Reduced the number of rounds for easier observation
WORK_TIME = 0.5   # Work processing time (seconds)
BARRIER_TIME = 0.2  # Waiting time at the barrier (seconds)
DISPLAY_REFRESH = 0.1  # Screen refresh rate

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_progress_bar(progress, width=30):  # Increase progress bar length
    filled = int(width * progress)
    bar = '█' * filled + '▒' * (width - filled)
    percentage = progress * 100
    if percentage == 100:
        return f'[{bar}] \033[1;32m{percentage:.1f}%\033[0m'  # Green when completed
    else:
        return f'[{bar}] {percentage:.1f}%'

def print_status_table(PROCESS_status, current_barrier, status_lock):
    with status_lock:
        headers = ['PROCESS', 'State', 'Progress']
        table_data = []
        
        for PROCESS_id in sorted(PROCESS_status.keys()):
            status = PROCESS_status[PROCESS_id]
            progress = create_progress_bar(status['progress'])
            state = status['state']
            
            # Add blinking effect for waiting state
            if state == 'waiting':
                if int(time.time() * 2) % 2:  # Blinks every 0.5 seconds
                    state = '\033[1;33m⌛ Waiting for barrier\033[0m'
                else:
                    state = '\033[1;33m⏳ Waiting for barrier\033[0m'
            elif state == 'working':
                state = '\033[1;32m⚙ Working\033[0m'
            elif state == 'completed':
                state = '\033[1;34m✓ Completed\033[0m'
            
            time_spent = f"{status['time']:.2f}" if status['time'] is not None else "---"
            table_data.append([
                f"\033[1;36mPROCESS {PROCESS_id}\033[0m", 
                state, 
                progress
                
            ])
        
        clear_terminal()
        print(f"\n\033[1;35m=== Barrier Synchronization Simulation ===\033[0m")
        print(f"\033[1;33mRound: {current_barrier + 1}/{NUM_BARRIERS}\033[0m")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
       
       
        sys.stdout.flush()

def update_PROCESS_status(PROCESS_status, PROCESS_id, status_lock, **kwargs):
    with status_lock:
        current_status = PROCESS_status[PROCESS_id].copy()
        current_status.update(kwargs)
        PROCESS_status[PROCESS_id] = current_status

def simulate_work(progress, PROCESS_status, PROCESS_id, status_lock, barrier_num):
    start = time.time()
    update_PROCESS_status(PROCESS_status, PROCESS_id, status_lock,
                        progress=progress,
                        time=time.time() - start)
    print_status_table(PROCESS_status, barrier_num, status_lock)
    time.sleep(WORK_TIME + random.uniform(0, 0.1))  # Add a bit of random delay


def centralized_barrier(PROCESS_id, barrier_num, count, sense, local_sense, PROCESS_status, status_lock):
    start_time = time.time()
    local_sense.value = not local_sense.value
    
    update_PROCESS_status(PROCESS_status, PROCESS_id, status_lock, 
                        state='waiting', 
                        time=time.time() - start_time)
    print_status_table(PROCESS_status, barrier_num, status_lock)
    
    with count.get_lock():
        count.value -= 1
        if count.value == 0:
            time.sleep(BARRIER_TIME)  # Pause when all PROCESSES reach the barrier
            count.value = NUM_PROCESSES
            sense.value = local_sense.value
        else:
            while sense.value != local_sense.value:
                time.sleep(DISPLAY_REFRESH)
                update_PROCESS_status(PROCESS_status, PROCESS_id, status_lock,
                                   time=time.time() - start_time)
                print_status_table(PROCESS_status, barrier_num, status_lock)

def worker(PROCESS_id, count, sense, local_sense, PROCESS_status, status_lock):
    for barrier_num in range(NUM_BARRIERS):
        # Initialize new work
        update_PROCESS_status(PROCESS_status, PROCESS_id, status_lock,
                           state='working',
                           progress=0,
                           time=0)
        print_status_table(PROCESS_status, barrier_num, status_lock)
        
        # Simulate work in 10 steps
        for progress in range(10):
            simulate_work((progress + 1) / 10, PROCESS_status, PROCESS_id, status_lock, barrier_num)
        
        # Barrier synchronization
        centralized_barrier(PROCESS_id, barrier_num, count, sense, local_sense, PROCESS_status, status_lock)
        
        # Mark as completed
        update_PROCESS_status(PROCESS_status, PROCESS_id, status_lock,
                           state='completed')
        print_status_table(PROCESS_status, barrier_num, status_lock)
        time.sleep(1)  # Pause to observe completed state

def print_results_summary(PROCESS_status: Dict, total_time: float):
    """Print a summary of the barrier synchronization simulation results."""
    print("\n\033[1;35m=== Simulation Results ===\033[0m")
    
    # Collect PROCESS-wise statistics
    PROCESS_times = [status['time'] for status in PROCESS_status.values() if status['time'] is not None]
    
    # Calculate summary statistics
    avg_PROCESS_time = sum(PROCESS_times) / len(PROCESS_times) if PROCESS_times else 0
    max_PROCESS_time = max(PROCESS_times) if PROCESS_times else 0
    min_PROCESS_time = min(PROCESS_times) if PROCESS_times else 0
    
    # Prepare summary table
    summary_data = [
        ["Total PROCESSES", NUM_PROCESSES],
        ["Number of Barrier Rounds", NUM_BARRIERS],
        ["Total Execution Time", f"{total_time:.2f} seconds"],
        ["Average Time per PROCESS", f"{avg_PROCESS_time:.2f} seconds"],
        ["Max Time per PROCESS", f"{max_PROCESS_time:.2f} seconds"],
        ["Min Time per PROCESS", f"{min_PROCESS_time:.2f} seconds"]
    ]
    
    # Print summary table
    print(tabulate(summary_data, headers=["Metric", "Value"], tablefmt="grid"))
    
    # Visual representation of PROCESS performance
    

def main():
    # Initialize shared variables
    start_total_time = time.time()
    manager = multiprocessing.Manager()
    PROCESS_status = manager.dict()
    status_lock = multiprocessing.Lock()
    
    for i in range(NUM_PROCESSES):
        PROCESS_status[i] = {
            'state': 'working',
            'progress': 0,
            'time': None
        }
    
    count = multiprocessing.Value('i', NUM_PROCESSES)
    sense = multiprocessing.Value('b', True)
    
    clear_terminal()
    print("\033[1;35m=== Starting Barrier Synchronization Simulation ===\033[0m")
    start_total_time = time.time()
    time.sleep(1)
    
    # Create processes
    processes = []
    for i in range(NUM_PROCESSES):
        local_sense = multiprocessing.Value('b', True)
        p = multiprocessing.Process(
            target=worker,
            args=(i, count, sense, local_sense, PROCESS_status, status_lock)
        )
        processes.append(p)
        p.start()
        time.sleep(0.1)  # Sequential PROCESS start
    
    # Wait for all processes to finish
    for p in processes:
        p.join()
    
    total_time = time.time() - start_total_time
    
    print("\n\033[1;35m=== Simulation Complete ===\033[0m")
    
     
    total_time = time.time() - start_total_time
    
    print(f"\nTotal execution time: {total_time:.2f} seconds")
    
    # Print results summary
    print_results_summary(PROCESS_status, total_time)

if __name__ == "__main__":
    main()
