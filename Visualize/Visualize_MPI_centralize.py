import tkinter as tk
import threading
import time
import queue
import random

class CentralizedBarrierVisualization:
    def __init__(self, num_threads=8, num_barriers=5):
        self.NUM_THREADS = num_threads
        self.NUM_BARRIERS = num_barriers
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Centralized Barrier Synchronization")
        self.root.geometry("800x600")
        
        # Synchronization primitives
        self.barriers = [threading.Barrier(num_threads) for _ in range(num_barriers)]
        
        # Thread tracking
        self.threads_complete = 0
        self.update_queue = queue.Queue()
        
        # Synchronization for queue updates
        self.queue_lock = threading.Lock()
        
        # Metrics
        self.total_execution_time = 0
        self.average_time_per_thread = 0
        self.max_time_per_thread = 0
        self.min_time_per_thread = 0
        
        # Create UI
        self.create_ui()
    
    def create_ui(self):
        # Barrier round label
        self.barrier_label = tk.Label(
            self.root, 
            text="Barrier Synchronization", 
            font=("Arial", 16, "bold")
        )
        self.barrier_label.pack(pady=10)
        
        # Threads frame
        threads_frame = tk.Frame(self.root)
        threads_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Create thread visualization
        self.thread_frames = []
        self.thread_progress_bars = []
        self.thread_status_labels = []
        self.thread_speed_labels = []
        
        for i in range(self.NUM_THREADS):
            # Individual thread frame
            thread_frame = tk.Frame(threads_frame, relief=tk.RAISED, borderwidth=1)
            thread_frame.pack(fill=tk.X, pady=5)
            
            # Thread ID
            tk.Label(thread_frame, text=f"Thread {i}", width=10).pack(side=tk.LEFT, padx=5)
            
            # Speed Label
            speed_label = tk.Label(thread_frame, text="", width=10)
            speed_label.pack(side=tk.LEFT, padx=5)
            self.thread_speed_labels.append(speed_label)
            
            # Status Label
            status_label = tk.Label(thread_frame, text="Initialized", width=20)
            status_label.pack(side=tk.LEFT, padx=5)
            self.thread_status_labels.append(status_label)
            
            # Progress Bar
            progress_bar = tk.Scale(
                thread_frame, 
                from_=0, to=100, 
                orient=tk.HORIZONTAL, 
                length=300, 
                showvalue=0
            )
            progress_bar.pack(side=tk.LEFT, padx=5)
            self.thread_progress_bars.append(progress_bar)
            
            self.thread_frames.append(thread_frame)
        
        # New label to display the additional metrics
        self.result_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.result_label.pack(pady=20)
    
    def update_ui(self):
        """Process updates from threads"""
        try:
            while True:
                thread_id, status, progress, speed = self.update_queue.get_nowait()
                
                # Update speed label
                self.thread_speed_labels[thread_id].config(text=f"Speed: {speed:.2f}")
                
                # Update status label
                self.thread_status_labels[thread_id].config(text=status)
                
                # Update progress bar
                self.thread_progress_bars[thread_id].set(progress)
                
                # Update barrier label
                self.barrier_label.config(
                    text=f"Barrier Synchronization: {status}"
                )
        except queue.Empty:
            pass
        
        # Check if all threads have completed
        if self.threads_complete == self.NUM_THREADS:
            self.barrier_label.config(text="Simulation Complete!")
            
            # Populate the result label with the additional metrics
            result_text = f"""
Total Threads: {self.NUM_THREADS}
Number of Barrier Rounds: {self.NUM_BARRIERS}
Total Execution Time: {self.total_execution_time:.2f} seconds
Average Time per Thread: {self.average_time_per_thread:.2f} seconds
Max Time per Thread: {self.max_time_per_thread:.2f} seconds
Min Time per Thread: {self.min_time_per_thread:.2f} seconds
"""
            self.result_label.config(text=result_text)
            return
        
        # Schedule next update
        self.root.after(100, self.update_ui)
    
    def worker(self, thread_id):
        """Worker thread function"""
        # Create random work and wait speeds
        work_speed = random.uniform(0.01, 0.05)
        barrier_wait_speed = random.uniform(0.1, 0.5)
        
        try:
            self.total_execution_time = 0
            self.max_time_per_thread = 0
            self.min_time_per_thread = float('inf')
            
            for barrier_num in range(self.NUM_BARRIERS):
                # Simulate work with varied speed
                for progress in range(101):
                    with self.queue_lock:
                        self.update_queue.put((
                            thread_id, 
                            f"Working Round {barrier_num+1}", 
                            progress,
                            work_speed
                        ))
                    time.sleep(work_speed)
                
                # Reach barrier
                with self.queue_lock:
                    self.update_queue.put((
                        thread_id, 
                        f"Waiting at Barrier {barrier_num+1}", 
                        100,
                        barrier_wait_speed
                    ))
                
                # Wait a random time before reaching the barrier
                time.sleep(barrier_wait_speed)
                
                # Synchronize at barrier
                try:
                    start_wait = time.time()
                    self.barriers[barrier_num].wait()
                    wait_time = time.time() - start_wait
                    
                    with self.queue_lock:
                        self.update_queue.put((
                            thread_id, 
                            f"Synchronized Round {barrier_num+1} (Wait: {wait_time:.2f}s)", 
                            100,
                            wait_time
                        ))
                    
                    # Update total execution time and min/max time per thread
                    self.total_execution_time += wait_time
                    self.max_time_per_thread = max(self.max_time_per_thread, wait_time)
                    self.min_time_per_thread = min(self.min_time_per_thread, wait_time)
                
                except threading.BrokenBarrierError:
                    with self.queue_lock:
                        self.update_queue.put((
                            thread_id, 
                            f"Barrier {barrier_num+1} Broken", 
                            100,
                            0
                        ))
                    return
        
        except Exception as e:
            with self.queue_lock:
                self.update_queue.put((
                    thread_id, 
                    f"Error: {str(e)}", 
                    100,
                    0
                ))
        
        # Tăng số lượng luồng hoàn thành
        with threading.Lock():
            self.threads_complete += 1
        
        # Mark thread as complete
        with self.queue_lock:
            self.update_queue.put((
                thread_id, 
                "Completed", 
                100,
                0
            ))
        
        # Calculate average time per thread
        self.average_time_per_thread = self.total_execution_time / self.NUM_THREADS
    
    def start_simulation(self):
        """Start barrier synchronization"""
        # Start UI update thread
        self.update_ui()
        
        # Create and start worker threads
        threads = []
        for i in range(self.NUM_THREADS):
            thread = threading.Thread(target=self.worker, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
    
    def run(self):
        """Run the visualization"""
        # Start simulation in a separate thread
        sim_thread = threading.Thread(target=self.start_simulation)
        sim_thread.daemon = True
        sim_thread.start()
        
        # Start Tkinter main loop
        self.root.mainloop()

def main():
    visualization = CentralizedBarrierVisualization()
    visualization.run()

if __name__ == "__main__":
    main()
