import tkinter as tk
import threading
import math
import time
import random

class TournamentBarrierVisualizer:
    def __init__(self, num_threads=8, num_barriers=5):
        # Configuration first
        self.NUM_THREADS = num_threads
        self.NUM_BARRIERS = num_barriers
        self.rounds = math.ceil(math.log(self.NUM_THREADS, 2))
        
        # Create Tkinter root
        self.root = tk.Tk()
        self.root.title("Tournament Barrier Visualization")
        
        # Synchronization data
        self.thread_states = [tk.StringVar(value="Waiting") for _ in range(self.NUM_THREADS)]
        self.thread_colors = [self.generate_pastel_color() for _ in range(self.NUM_THREADS)]
        
        # Barrier simulation data
        self.array = [[{'role': '', 'state': tk.StringVar(value="")} 
                       for _ in range(self.rounds + 1)] 
                      for _ in range(self.NUM_THREADS)]
        
        # Setup UI
        self.setup_ui()
        
        # Initialize thread roles
        self.initialize_thread_roles()
        
    def generate_pastel_color(self):
        """Generate a random pastel color."""
        return f'#{random.randint(150, 220):02x}{random.randint(150, 220):02x}{random.randint(150, 220):02x}'
    
    def setup_ui(self):
        """Create the main UI layout."""
        # Thread status frame
        thread_frame = tk.Frame(self.root)
        thread_frame.pack(pady=10, padx=10)
        
        self.thread_labels = []
        for i in range(self.NUM_THREADS):
            label = tk.Label(thread_frame, 
                             textvariable=self.thread_states[i], 
                             relief=tk.RAISED, 
                             width=15,
                             bg=self.thread_colors[i])
            label.pack(side=tk.LEFT, padx=5)
            self.thread_labels.append(label)
        
        # Rounds visualization
        self.round_frames = []
        for round_num in range(self.rounds + 1):
            round_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=2)
            round_frame.pack(pady=5)
            
            round_label = tk.Label(round_frame, text=f"Round {round_num}")
            round_label.pack()
            
            thread_roles = []
            for thread_num in range(self.NUM_THREADS):
                role_label = tk.Label(round_frame, 
                                      textvariable=self.array[thread_num][round_num]['state'], 
                                      width=10,
                                      bg=self.thread_colors[thread_num])
                role_label.pack(side=tk.LEFT, padx=2)
                thread_roles.append(role_label)
            
            self.round_frames.append((round_frame, thread_roles))
        
        # Start button
        start_button = tk.Button(self.root, text="Start Barrier Simulation", command=self.start_simulation)
        start_button.pack(pady=10)
    
    def initialize_thread_roles(self):
        """Initialize thread roles for each round."""
        for l in range(self.NUM_THREADS):
            for k in range(self.rounds + 1):
                comp = math.ceil(2 ** k)
                comp_second = math.ceil(2 ** (k - 1))
                
                role = ""
                if k > 0 and l % comp == 0 and (l + comp_second) < self.NUM_THREADS and comp < self.NUM_THREADS:
                    role = "winner"
                elif k > 0 and l % comp == 0 and (l + comp_second) >= self.NUM_THREADS:
                    role = "bye"
                elif k > 0 and (l % comp == comp_second):
                    role = "loser"
                elif k > 0 and l == 0 and comp >= self.NUM_THREADS:
                    role = "champion"
                elif k == 0:
                    role = "dropout"
                
                self.array[l][k]['role'] = role
                self.array[l][k]['state'].set(role)
    
    def thread_barrier_simulation(self, thread_id):
        """Simulate thread barrier process with slower execution."""
        for barrier_iteration in range(self.NUM_BARRIERS):
            # Update thread state
            self.thread_states[thread_id].set("Entering Barrier")
            
            # Simulate barrier entry with longer wait
            time.sleep(random.uniform(1.0, 2.0))  # Increased from 0.1-0.5 to 1.0-2.0
            
            # Update thread state
            self.thread_states[thread_id].set("In Barrier")
            
            # Simulate synchronization with longer wait
            time.sleep(random.uniform(1.5, 3.0))  # Increased from 0.3-0.7 to 1.5-3.0
            
            # Update thread state
            self.thread_states[thread_id].set("Exiting Barrier")
            
            # Longer pause between barrier iterations
            time.sleep(1.0)  # Increased from 0.2 to 1.0
        
        # Final state
        self.thread_states[thread_id].set("Completed")
    
    def start_simulation(self):
        """Start the tournament barrier simulation."""
        # Create and start threads
        threads = []
        for i in range(self.NUM_THREADS):
            thread = threading.Thread(target=self.thread_barrier_simulation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for threads to complete
        def wait_for_threads():
            for thread in threads:
                thread.join()
            self.thread_states[0].set("All Threads Completed")
        
        # Start waiting thread
        threading.Thread(target=wait_for_threads).start()
    
    def run(self):
        """Run the Tkinter event loop."""
        self.root.mainloop()

# Create and run the visualization
if __name__ == "__main__":
    visualizer = TournamentBarrierVisualizer()
    visualizer.run()
