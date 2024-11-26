from mpi4py import MPI
import numpy as np
import time
import threading

print_lock = threading.Lock()

def safe_print(message):
    with print_lock:
        print(message, end='', flush=True)

def tree_barrier(rank, numprocs, comm):
    mask = 1
    while mask < numprocs:
        target = rank ^ mask
        if target < numprocs:
            if rank > target:
                comm.send(True, dest=target, tag=mask)
            else:
                comm.recv(source=target, tag=mask)
        mask <<= 1

    mask = numprocs >> 1
    while mask > 0:
        target = rank ^ mask
        if target < numprocs:
            if rank < target:
                comm.send(True, dest=target, tag=mask)
            else:
                comm.recv(source=target, tag=mask)
        mask >>= 1

def work_simulation(rank):
    processing_time = np.random.uniform(0.1, 1.0) * (rank + 1)
    time.sleep(processing_time)
    return processing_time

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    numprocs = comm.Get_size()
    
    np.random.seed(rank * 100)
    
    NUM_EXPERIMENTS = 5
    
    standard_barrier_times = np.zeros(NUM_EXPERIMENTS)
    tree_barrier_times = np.zeros(NUM_EXPERIMENTS)
    
    if rank == 0:
        print(f"Running experiments with {numprocs} processes")
    
    for exp in range(NUM_EXPERIMENTS):
        work_time = work_simulation(rank)
        
        standard_barrier_start = MPI.Wtime()
        comm.Barrier()
        standard_barrier_time = MPI.Wtime() - standard_barrier_start
        standard_barrier_times[exp] = standard_barrier_time
        
        safe_print(f"Proc {rank}: Std Barrier {exp+1} = {standard_barrier_time:.6f}s | ")
        
        time.sleep(np.random.uniform(0.05, 0.2))
        
        tree_barrier_start = MPI.Wtime()
        tree_barrier(rank, numprocs, comm)
        tree_barrier_time = MPI.Wtime() - tree_barrier_start
        tree_barrier_times[exp] = tree_barrier_time
        
        safe_print(f"Tree Barrier {exp+1} = {tree_barrier_time:.6f}s\n")
        
        comm.Barrier()
    
    if rank == 0:
        print("\nBarrier Performance Summary:")
        print(f"Standard Barrier - Mean: {np.mean(standard_barrier_times):.6f}s, Min: {np.min(standard_barrier_times):.6f}s, Max: {np.max(standard_barrier_times):.6f}s")
        print(f"Tree Barrier     - Mean: {np.mean(tree_barrier_times):.6f}s, Min: {np.min(tree_barrier_times):.6f}s, Max: {np.max(tree_barrier_times):.6f}s")

if __name__ == "__main__":
    main()
