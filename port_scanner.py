#!/usr/bin/python3

import socket
import threading
import sys
from queue import Queue
from datetime import datetime

# Threaded port scanner
# scan known ports 1 - 1023
# scan static ports 1024 - 49151
# scan dynamic ports 49152 - 65535

THREADS = 1024 * 8
OPEN_PORTS = []

q = Queue()
print_lock = threading.Lock()
port_list_lock = threading.Lock()


def port_scan(ip, port, timeout=5):
    with print_lock:
        print(f"Scanning {ip}:{port}")
        
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((ip, port))
        connected = True
        
    except:
        connected = False
        
    finally:
        with port_list_lock:
            if connected:
                OPEN_PORTS.append(port)
        return connected

def threader():
    while True:
        item = q.get()
        if item is None:
            break
        ip, port = item
        port_scan(ip, port)
        q.task_done()

def main(target_ip='localhost', max_port=65535):
    # create all threads
    for _ in range(THREADS):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()

    # enqueue tasks to threads   
    for port in range(1, max_port+1):
        q.put((target_ip, port))
        
    # block until all tasks are done    
    q.join()


if __name__ == '__main__':
    target_ip = 'localhost'
    max_port = 65535
    
    # get system arguments
    if len(sys.argv) == 2:
        target_ip = sys.argv[1]
    elif len(sys.argv) == 3:
        target_ip = sys.argv[1]
        max_port = int(sys.argv[2])
     
    t1 = datetime.now()
    main(target_ip, max_port)
    t2 = datetime.now()
    
    print("\nOpened ports:", OPEN_PORTS)
    print(f"\nFinished scanning ports 1 to {max_port} in {t2-t1} seconds.")
    