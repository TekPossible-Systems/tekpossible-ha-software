logo = """
  _______ ______ _  _______   ____   _____ _____ _____ ____  _      ______      _    _          
 |__   __|  ____| |/ /  __ \ / __ \ / ____/ ____|_   _|  _ \| |    |  ____|    | |  | |   /\    
    | |  | |__  | ' /| |__) | |  | | (___| (___   | | | |_) | |    | |__       | |__| |  /  \   
    | |  |  __| |  < |  ___/| |  | |\___ \\\\___ \  | | |  _ <| |    |  __|      |  __  | / /\ \  
    | |  | |____| . \| |    | |__| |____) |___) |_| |_| |_) | |____| |____     | |  | |/ ____ \ 
    |_|  |______|_|\_\_|     \____/|_____/_____/|_____|____/|______|______|    |_|  |_/_/    \_\\


    Port Opening Program Developed by TekPossible Systems (Griffin Kiesecker)    
    This is mainly a program that is here until I write something cooler    
"""

import socket
import os
import threading

__ports = os.popen("firewall-cmd --list-ports").read().replace("/tcp", "").strip().split(" ")
sockets = []
threads = []
print(logo)

def handle_socket(s: socket.socket):
    print("Started new thread!")
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            try:
                data = conn.recv(1024)
                print(data.decode('utf-8'))
                if not data:
                    break
                conn.sendall(bytes("RECV: " + data.decode('utf-8'), 'utf-8'))
            except:
                s.close()



for i in range(len(__ports)):
    if (int(__ports[i]) < 1000):
        continue
    else:
        print(int(__ports[i]))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', int(__ports[i])))
        s.listen(50)
        sockets.append(s)
        print(f"LISTENING ON PORT {__ports[i]}!")


for s in sockets:
    thr = threading.Thread(target=handle_socket, args=(s,), daemon=False)
    thr.start()
    threads.append(thr)

while True:
    try:
        continue
    except:
        for thread in threads:
            thread.join()