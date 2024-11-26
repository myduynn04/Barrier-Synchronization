# Barrier Synchronization 

This project is developed as part of the **Operating Systems** course. The primary goal is to explore and implement various barrier synchronization techniques in both multi-threaded and distributed environments. The project demonstrates the use of centralized, tournament-style, and tree-based barriers, as well as their performance analysis through visualization.

---

## Project Structure

### 1. Implementation
- `MP_centralization.py`: Implements a centralized barrier using threading
- `MP_tournament.py`: Implements a tournament-style barrier for hierarchical synchronization
- `MPI_centralization.py`: Implements a tree-based barrier using MPI for distributed systems
- `MP-MPI.py`: A hybrid approach combining threads and processes to evaluate barrier synchronization efficiency

### 2. Visualization
- `Visualize_MPI_centralization.py`: Visualizes results for the centralized MPI barrier
- `Visualize_MP_MPI_for_process.py`: Visualizes the behavior of MPI processes
- `Visualize_MP_centralize.py`: Displays results from the centralized barrier implementation
- `Visualize_MP_tournament.py`: Visualizes the synchronization process in a tournament-style barrier


### 3. Practical Demonstration: Conway's Game of Life
As a practical example of barrier synchronization, we've included a Conway_game_of_life.py implementation that showcases:

- Distributed grid computation
- Tree-based barrier synchronization
- Parallel state updates
- Process coordination techniques
---

## Prerequisites

### 1. System Requirements
- Python 3.x
- Required Python libraries:
  - `threading`
  - `multiprocessing`
  - `mpi4py`
  - `numpy`

### 2. Installation
```bash
# Recommended: Create a virtual environment
python3 -m venv barrier_sync_env
source barrier_sync_env/bin/activate

# Install required dependencies
pip install numpy mpi4py
```

## Running the Implementations

### Centralized Barrier
```bash
python MP_centralization.py
```

### Tournament Barrier
```bash
python MP_tournament.py <num_threads> <num_barriers>
```

### MPI Tree Barrier
```bash
mpiexec -n <num_processes> python MPI_centralization.py
```

### Hybrid Implementation
```bash
python MP-MPI.py
```

## Visualizing Results
```bash
# Run visualization scripts
python Visualize_MP_centralize.py
python Visualize_MP_tournament.py
python Visualize_MPI_centralization.py
python Visualize_MP_MPI_for_process.py
```

## Project Goals
- Understand different types of barrier synchronization techniques
- Compare their performance in multi-threaded and distributed environments
- Explore real-world applications of synchronization in parallel computing

## Performance Metrics
- Synchronization overhead
- Scalability across different thread/process counts
- Efficiency in various computational scenarios

## Troubleshooting
- Ensure all dependencies are correctly installed
- Check Python and MPI versions for compatibility
- Verify network and process communication settings for distributed implementations

## Contributors
- Nguyen My Duyen   20225967
- Nguyen Lan Nhi    20225991
- Ha Viet Khanh     20225979
- Ho Bao Thu        20226003



## Contact
For questions, issues, or collaboration:
- Email: duyen.nm225967@sis.hust.edu.vn
- GitHub: [[Barrier Synchronization](https://github.com/myduynn04/Barrier-Synchronization.git)]

---

---

**Academic Significance**: 
Barrier synchronization is a critical concept in parallel computing, enabling efficient coordination and communication between multiple threads or processes. This project provides a comprehensive exploration of different barrier synchronization techniques, offering insights into their design, implementation, and performance characteristics in real-world computational scenarios.
