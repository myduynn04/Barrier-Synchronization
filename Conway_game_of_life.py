from mpi4py import MPI
import numpy as np
import time
import threading
import sys

# Constants
ALIVE = 1
DEAD = 0

# Shared flag to indicate whether the game should stop
stop_game = False


def stop_game_listener():
    """Thread to listen for user input to stop the game."""
    global stop_game
    input("Press Enter to stop the game...\n")
    stop_game = True


def tree_barrier(rank, numprocs, comm):
    """
    Implements a tree-based barrier synchronization.
    """
    # Phase 1: Gather (Bottom-up)
    mask = 1
    while mask < numprocs:
        target = rank ^ mask  # XOR to find communication partner
        if target < numprocs:
            if rank > target:
                comm.send(True, dest=target, tag=mask)
            else:
                comm.recv(source=target, tag=mask)
        mask <<= 1

    # Phase 2: Release (Top-down)
    mask = numprocs >> 1
    while mask > 0:
        target = rank ^ mask
        if target < numprocs:
            if rank < target:
                comm.send(True, dest=target, tag=mask)
            else:
                comm.recv(source=target, tag=mask)
        mask >>= 1


def initialize_grid(rows, cols):
    """
    Initialize the grid with a few live cells.
    """
    grid = np.zeros((rows, cols), dtype=int)
    live_positions = [(rows // 2, cols // 2), (rows // 2 - 1, cols // 2),
                      (rows // 2 + 1, cols // 2), (rows // 2, cols // 2 - 1),
                      (rows // 2, cols // 2 + 1)]
    for x, y in live_positions:
        grid[x, y] = ALIVE
    return grid


def count_neighbors(grid, x, y, rows, cols):
    """
    Count the number of alive neighbors for a cell.
    """
    neighbors = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),         (0, 1),
        (1, -1), (1, 0), (1, 1)
    ]
    count = 0
    for dx, dy in neighbors:
        nx, ny = (x + dx) % rows, (y + dy) % cols
        count += grid[nx, ny]
    return count


def update_grid(local_grid, rows, cols):
    """
    Compute the next state of the grid.
    """
    new_grid = local_grid.copy()
    for i in range(1, rows - 1):  # Exclude halo rows
        for j in range(cols):
            neighbors = count_neighbors(local_grid, i, j, rows, cols)
            if local_grid[i, j] == ALIVE and (neighbors < 2 or neighbors > 3):
                new_grid[i, j] = DEAD
            elif local_grid[i, j] == DEAD and neighbors == 3:
                new_grid[i, j] = ALIVE
    return new_grid


def print_grid(grid):
    """
    Print the grid.
    """
    for row in grid:
        print("".join("O" if cell == ALIVE else "." for cell in row))
    print()


def main():
    global stop_game

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    numprocs = comm.Get_size()

    # Grid dimensions
    global_rows, global_cols = 20, 20

    # Get the time step from user input (on rank 0 only)
    if rank == 0:
        try:
            time_step = float(input("Enter the time step (in seconds) between updates: "))
        except ValueError:
            print("Invalid input. Defaulting to 0.5 seconds.")
            time_step = 0.5
    else:
        time_step = None

    # Broadcast the time step to all processes
    time_step = comm.bcast(time_step, root=0)

    # Number of rows per process (including halo rows)
    local_rows = (global_rows // numprocs) + 2
    cols = global_cols

    # Initialize grid
    if rank == 0:
        grid = initialize_grid(global_rows, global_cols)
    else:
        grid = None

    # Scatter grid among processes
    local_grid = np.zeros((local_rows, cols), dtype=int)
    comm.Scatterv(
        [grid, (global_rows // numprocs) * cols, None, MPI.INT],
        local_grid[1:-1, :],
        root=0
    )

    # Start the listener thread to stop the game (AFTER initialization)
    if rank == 0:
        threading.Thread(target=stop_game_listener, daemon=True).start()

    while not stop_game:
        # Send and receive halo rows
        if rank > 0:
            comm.Sendrecv(local_grid[1, :], dest=rank - 1, recvbuf=local_grid[0, :], source=rank - 1)
        if rank < numprocs - 1:
            comm.Sendrecv(local_grid[-2, :], dest=rank + 1, recvbuf=local_grid[-1, :], source=rank + 1)

        # Synchronize processes using tree barrier before updating the grid
        tree_barrier(rank, numprocs, comm)

        # Update grid
        new_local_grid = update_grid(local_grid, local_rows, cols)
        local_grid[:] = new_local_grid

        # Synchronize processes using tree barrier before gathering the updated grid
        tree_barrier(rank, numprocs, comm)

        # Gather the grid on rank 0
        if rank == 0:
            grid = np.zeros((global_rows, global_cols), dtype=int)
        comm.Gatherv(local_grid[1:-1, :], [grid, (global_rows // numprocs) * cols, None, MPI.INT], root=0)

        # Synchronize processes using tree barrier before printing the grid
        tree_barrier(rank, numprocs, comm)

        # Print the grid (on rank 0)
        if rank == 0:
            print("\nCurrent Grid State:")
            print_grid(grid)
            time.sleep(time_step)

    # Ensure all processes exit cleanly
    tree_barrier(rank, numprocs, comm)
    if rank == 0:
        print("\nGame stopped by user.")


if __name__ == "__main__":
    main()
