import threading
import random
import time

# Constants
LOWER_NUM = 1
UPPER_NUM = 10000
BUFFER_SIZE = 100
MAX_COUNT = 10000

buffer_array = []
producer_done = False
buffer_condition = threading.Condition()

# File locks
all_file_lock = threading.Lock()
even_file_lock = threading.Lock()
odd_file_lock = threading.Lock()


def producer():
    """
        Produces MAX_COUNT random numbers between LOWER_NUM and UPPER_NUM, writes them to 'all.txt',
        and appends each number to a shared buffer. It signals other threads using a condition variable
        when the buffer has space for more numbers and sets the global flag 'producer_done' when finished.
    """
    global producer_done
    print(f"{threading.current_thread().name} started.")
    with all_file_lock:
        with open('all.txt', 'w') as f_all:
            for _ in range(MAX_COUNT):
                num = random.randint(LOWER_NUM, UPPER_NUM)
                f_all.write(f"{num}\n")
                with buffer_condition:
                    while len(buffer_array) >= BUFFER_SIZE:
                        buffer_condition.wait()
                    buffer_array.append(num)
                    buffer_condition.notify_all()
    with buffer_condition:
        producer_done = True
        buffer_condition.notify_all()


def customer_even():
    """
        Consumes even numbers from the shared buffer, writing them to 'even.txt'. It uses a condition variable
        to wait for numbers to become available or for the producer to finish, and a file lock to ensure thread-safe
        file writing. The function removes processed numbers from the buffer to make space for new numbers.
    """
    print(f"{threading.current_thread().name} started.")
    with even_file_lock:
        with open('even.txt', 'w') as f_even:
            while True:
                with buffer_condition:
                    while not buffer_array and not producer_done:
                        buffer_condition.wait()
                    if producer_done and not buffer_array:
                        break
                    else:
                        for num in list(buffer_array):  # Iterate over a copy to safely modify the original list
                            if num % 2 == 0:
                                f_even.write(f"{num}\n")
                                buffer_array.remove(num)
                    buffer_condition.notify_all()


def customer_odd():
    """
        Consumes odd numbers from the shared buffer, writing them to 'odd.txt'. Similar to customer_even,
        it waits on a condition variable for numbers to become available or for the production to end,
        using a file lock for thread-safe file access. Odd numbers are processed and removed from the buffer.
    """
    print(f"{threading.current_thread().name} started.")
    with odd_file_lock:
        with open('odd.txt', 'w') as f_odd:
            while True:
                with buffer_condition:
                    while not buffer_array and not producer_done:
                        buffer_condition.wait()
                    if producer_done and not buffer_array:
                        break
                    else:
                        for num in list(buffer_array):
                            if num % 2 != 0:
                                f_odd.write(f"{num}\n")
                                buffer_array.remove(num)
                    buffer_condition.notify_all()


if __name__ == '__main__':
    start_time = time.time()

    producer_thread = threading.Thread(target=producer, name="ProducerThread")
    customer_even_thread = threading.Thread(target=customer_even, name="EvenCustomerThread")
    customer_odd_thread = threading.Thread(target=customer_odd, name="OddCustomerThread")

    producer_thread.start()
    customer_even_thread.start()
    customer_odd_thread.start()

    producer_thread.join()
    customer_even_thread.join()
    customer_odd_thread.join()

    end_time = time.time()
    print(f"Execution completed in {end_time - start_time:.2f} seconds.")
