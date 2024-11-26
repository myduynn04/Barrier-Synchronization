import threading
import math
import time
import os
import sys
from tabulate import tabulate
import random

# Cấu hình cố định
NUM_THREADS = 8
NUM_BARRIERS = 5
DISPLAY_REFRESH = 0.1
BARRIER_TIME = 0.3

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_progress_bar(progress, width=30):
    filled = int(width * progress)
    bar = '█' * filled + '▒' * (width - filled)
    percentage = progress * 100
    if percentage == 100:
        return f'[{bar}] \033[1;32m{percentage:.1f}%\033[0m'  # Màu xanh khi hoàn thành
    else:
        return f'[{bar}] {percentage:.1f}%'

class Round:
    def __init__(self):
        self.role = -1
        self.opponent = None
        self.flag = False

def print_status_table(thread_status, current_barrier, thread_status_lock):
    with thread_status_lock:
        headers = ['Thread', 'State', 'Progress', 'Time (s)', 'Role']
        table_data = []
        
        for thread_id in sorted(thread_status.keys()):
            status = thread_status[thread_id]
            progress = create_progress_bar(status['progress'])
            state = status['state']
            
            # Hiệu ứng nhấp nháy cho trạng thái chờ
            if state == 'waiting':
                if int(time.time() * 2) % 2:
                    state = '\033[1;33m⌛ Waiting for barrier\033[0m'
                else:
                    state = '\033[1;33m⏳ Waiting for barrier\033[0m'
            elif state == 'working':
                state = '\033[1;32m⚙ Working\033[0m'
            elif state == 'completed':
                state = '\033[1;34m✓ Completed\033[0m'
            
            time_spent = f"{status['time']:.2f}" if status['time'] is not None else "---"
            table_data.append([
                f"\033[1;36mThread {thread_id}\033[0m", 
                state, 
                progress, 
                time_spent,
                f"\033[1;35m{status['role']}\033[0m"
            ])
        
        clear_terminal()
        print(f"\n\033[1;35m=== Tournament Barrier Synchronization Simulation ===\033[0m")
        print(f"\033[1;33mRound: {current_barrier + 1}/{NUM_BARRIERS}\033[0m")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        sys.stdout.flush()

def update_thread_status(thread_status, thread_id, thread_status_lock, **kwargs):
    with thread_status_lock:
        current_status = thread_status[thread_id].copy()
        current_status.update(kwargs)
        thread_status[thread_id] = current_status

def simulate_work(progress, thread_status, thread_id, thread_status_lock, barrier_num, role):
    start = time.time()
    update_thread_status(thread_status, thread_id, thread_status_lock,
                        progress=progress,
                        time=time.time() - start,
                        role=role)
    print_status_table(thread_status, barrier_num, thread_status_lock)
    time.sleep(0.1 + random.uniform(0, 0.05))  # Thêm một chút độ trễ ngẫu nhiên

def barrier(vpid, sense, rounds, thread_status, thread_status_lock, barrier_num):
    round = 0
    start_time = time.time()
    local_role = array[vpid][round].role

    update_thread_status(thread_status, vpid, thread_status_lock, 
                        state='waiting', 
                        time=time.time() - start_time,
                        role=local_role)
    print_status_table(thread_status, barrier_num, thread_status_lock)
    
    while True:
        if local_role == "loser":
            array[vpid][round].opponent.flag = sense[0]
            while array[vpid][round].flag != sense[0]:
                time.sleep(DISPLAY_REFRESH)
                update_thread_status(thread_status, vpid, thread_status_lock,
                                     time=time.time() - start_time)
                print_status_table(thread_status, barrier_num, thread_status_lock)
            break
        
        if local_role == "winner":
            while array[vpid][round].flag != sense[0]:
                time.sleep(DISPLAY_REFRESH)
                update_thread_status(thread_status, vpid, thread_status_lock,
                                     time=time.time() - start_time)
                print_status_table(thread_status, barrier_num, thread_status_lock)
        
        if local_role == "champion":
            while array[vpid][round].flag != sense[0]:
                time.sleep(DISPLAY_REFRESH)
                update_thread_status(thread_status, vpid, thread_status_lock,
                                     time=time.time() - start_time)
                print_status_table(thread_status, barrier_num, thread_status_lock)
            array[vpid][round].opponent.flag = sense[0]
            break
        
        if round < rounds:
            round += 1
    
    # Trở lại
    while round > 0:
        round -= 1
        if local_role == "winner":
            array[vpid][round].opponent.flag = sense[0]
        if local_role == "dropout":
            break
    
    sense[0] = not sense[0]
    
    update_thread_status(thread_status, vpid, thread_status_lock,
                        state='completed',
                        time=time.time() - start_time)
    print_status_table(thread_status, barrier_num, thread_status_lock)

def thread_function(vpid, rounds, sense, thread_status, thread_status_lock):
    for barrier_num in range(NUM_BARRIERS):
        # Khởi tạo công việc mới
        update_thread_status(thread_status, vpid, thread_status_lock,
                             state='working',
                             progress=0,
                             time=0,
                             role=array[vpid][0].role)
        print_status_table(thread_status, barrier_num, thread_status_lock)
        
        # Mô phỏng công việc trong 10 bước
        for progress in range(10):
            simulate_work((progress + 1) / 10, thread_status, vpid, thread_status_lock, barrier_num, array[vpid][0].role)
        
        # Barrier đồng bộ hóa
        barrier(vpid, sense, rounds, thread_status, thread_status_lock, barrier_num)
        time.sleep(1)  # Tạm dừng để quan sát trạng thái hoàn thành

def print_results_summary(thread_status, total_time):
    clear_terminal()
    print("\n\033[1;35m=== Kết Quả Mô Phỏng Tournament Barrier ===\033[0m")
    
    thread_times = [status['time'] for status in thread_status.values() if status['time'] is not None]
    
    avg_thread_time = sum(thread_times) / len(thread_times) if thread_times else 0
    max_thread_time = max(thread_times) if thread_times else 0
    min_thread_time = min(thread_times) if thread_times else 0
    
    summary_data = [
        ["Tổng Số Threads", NUM_THREADS],
        ["Số Vòng Barrier", NUM_BARRIERS],
        ["Tổng Thời Gian Thực Thi", f"{total_time:.2f} giây"],
        ["Thời Gian Trung Bình Mỗi Thread", f"{avg_thread_time:.2f} giây"],
        ["Thời Gian Tối Đa Mỗi Thread", f"{max_thread_time:.2f} giây"],
        ["Thời Gian Tối Thiểu Mỗi Thread", f"{min_thread_time:.2f} giây"]
    ]
    
    print(tabulate(summary_data, headers=["Chỉ Số", "Giá Trị"], tablefmt="grid"))
    
    print("\n\033[1;33m=== Biểu Đồ Hiệu Năng Thread ===\033[0m")
    max_bar_width = 30
    for thread_id, status in sorted(thread_status.items()):
        if status['time'] is not None:
            bar_length = int((status['time'] / max_thread_time) * max_bar_width)
            bar = '█' * bar_length + '▒' * (max_bar_width - bar_length)
            print(f"Thread {thread_id} ({status['role']}): [{bar}] {status['time']:.2f}s")

def main():
    global array
    
    rounds = math.ceil(math.log(NUM_THREADS, 2))
    
    # Khởi tạo array
    array = [[Round() for _ in range(rounds + 1)] for _ in range(NUM_THREADS)]
    
    # Khởi tạo vai trò cho từng thread
    for l in range(NUM_THREADS):
        for k in range(rounds + 1):
            comp = math.ceil(2 ** k)
            comp_second = math.ceil(2 ** (k - 1))
            
            if k > 0 and l % comp == 0 and (l + comp_second) < NUM_THREADS and comp < NUM_THREADS:
                array[l][k].role = "winner"
            if k > 0 and l % comp == 0 and (l + comp_second) >= NUM_THREADS:
                array[l][k].role = "bye"
            if k > 0 and (l % comp == comp_second):
                array[l][k].role = "loser"
            if k > 0 and l == 0 and comp >= NUM_THREADS:
                array[l][k].role = "champion"
            if k == 0:
                array[l][k].role = "dropout"
            
            if array[l][k].role == "loser":
                array[l][k].opponent = array[l - comp_second][k]
            if array[l][k].role in ["winner", "champion"]:
                array[l][k].opponent = array[l + comp_second][k]
    
    # Khởi tạo trạng thái thread
    thread_status_lock = threading.Lock()
    thread_status = {i: {
        'state': 'working',
        'progress': 0,
        'time': None,
        'role': array[i][0].role
    } for i in range(NUM_THREADS)}
    
    clear_terminal()
    print("\033[1;35m=== Bắt Đầu Mô Phỏng Tournament Barrier ===\033[0m")
    start_total_time = time.time()
    time.sleep(1)
    
    # Tạo threads
    threads = []
    for vpid in range(NUM_THREADS):
        sense = [True]
        thread = threading.Thread(
            target=thread_function,
            args=(vpid, rounds, sense, thread_status, thread_status_lock)
        )
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # Khởi động tuần tự các thread
    
    # Đợi tất cả các threads kết thúc
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_total_time
    
    print("\n\033[1;35m=== Hoàn Thành Mô Phỏng ===\033[0m")
    print(f"\nTổng thời gian thực thi: {total_time:.2f} giây")
    
    # In kết quả tóm tắt
    print_results_summary(thread_status, total_time)

if __name__ == "__main__":
    main()