from mpi4py import MPI
import numpy as np
import time

NUM_BARRIERS = 1

def tree_barrier(rank, numprocs, comm):
    """
    Implements a tree-based barrier synchronization.
    This is more efficient than the centralized barrier as it has O(log n) communication steps.
    """
    # Phase 1: Gather (Bottom-up)
    mask = 1
    while mask < numprocs:
        target = rank ^ mask  # XOR to find communication partner
        if target < numprocs:
            if rank > target:
                # Send to parent in tree
                comm.send(True, dest=target, tag=mask)
            else:
                # Receive from child in tree
                comm.recv(source=target, tag=mask)
        mask <<= 1  # Shift left = multiply by 2
    
    # Phase 2: Release (Top-down)
    mask = numprocs >> 1  # Start from highest power of 2 less than numprocs
    while mask > 0:
        target = rank ^ mask
        if target < numprocs:
            if rank < target:
                # Send release signal
                comm.send(True, dest=target, tag=mask)
            else:
                # Wait for release
                comm.recv(source=target, tag=mask)
        mask >>= 1  # Shift right = divide by 2

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    numprocs = comm.Get_size()
    
    # Initialize timing array using numpy for better performance
    times = np.zeros(NUM_BARRIERS, dtype=np.float64)
    
    for i in range(NUM_BARRIERS):
        # Synchronize before starting timing
        comm.Barrier()
        
        time1 = MPI.Wtime()
        tree_barrier(rank, numprocs, comm)
        time2 = MPI.Wtime()
        
        times[i] = time2 - time1
        
        if rank == 0:
            print(f"Barrier {i} completed")
    
    # Calculate statistics
    avg_time = np.mean(times)
    max_time = comm.reduce(avg_time, op=MPI.MAX, root=0)
    min_time = comm.reduce(avg_time, op=MPI.MIN, root=0)
    
    # Only root process prints the timing statistics
    if rank == 0:
        print(f"\nBarrier Statistics:")
        print(f"Average time: {avg_time:.6f} seconds")
        print(f"Min time across processes: {min_time:.6f} seconds")
        print(f"Max time across processes: {max_time:.6f} seconds")
        print(f"Number of processes: {numprocs}")

if __name__ == "__main__":
    main()
