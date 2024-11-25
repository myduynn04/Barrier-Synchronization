import threading
import math
import time

NUM_THREADS = 0
NUM_BARRIERS = 0
array = [[None for _ in range(100)] for _ in range(1000)]

class Round:
    def __init__(self):
        self.role = -1
        self.opponent = None
        self.flag = False


def barrier(vpid, sense, rounds):
    round = 0

    while True:
        if array[vpid][round].role == "loser":
            array[vpid][round].opponent.flag = sense[0]
            while array[vpid][round].flag != sense[0]:
                pass
            break

        if array[vpid][round].role == "winner":
            while array[vpid][round].flag != sense[0]:
                pass

        if array[vpid][round].role == "champion":
            while array[vpid][round].flag != sense[0]:
                pass
            array[vpid][round].opponent.flag = sense[0]
            break

        if round < rounds:
            round += 1

    # Wake up
    while round > 0:
        round -= 1
        if array[vpid][round].role == "winner":
            array[vpid][round].opponent.flag = sense[0]
        if array[vpid][round].role == "dropout":
            break

    sense[0] = not sense[0]


def thread_function(vpid, rounds, sense):
    for i in range(NUM_BARRIERS):
        for _ in range(50):
            pass

        print(f"Hello World from thread {vpid}.")
        start_time = time.time()
        barrier(vpid, sense, rounds)
        end_time = time.time()
        print(f"Hello from thread {vpid} after barrier")
        print(f"Time spent in barrier by thread {vpid} is {end_time - start_time}")


def main():
    import sys
    global NUM_THREADS, NUM_BARRIERS

    if len(sys.argv) == 3:
        NUM_THREADS = int(sys.argv[1])
        NUM_BARRIERS = int(sys.argv[2])
    else:
        print("Syntax: python tournament.py num_threads num_barriers")
        sys.exit(-1)

    rounds = math.ceil(math.log(NUM_THREADS, 2))

    # Khởi tạo array
    for j in range(NUM_THREADS):
        for k in range(rounds + 1):
            array[j][k] = Round()

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

    threads = []
    for vpid in range(NUM_THREADS):
        sense = [True]
        thread = threading.Thread(target=thread_function, args=(vpid, rounds, sense))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()