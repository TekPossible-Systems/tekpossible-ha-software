import os
import socket
import threading
import json
import time
class BravoServer:
    def __init__(self, hostname, internal_status_port, internal_queue_port, external_queue_port_send, external_queue_port_recv, alpha_queue_port_send, alpha_queue_port_recv  ):
        self.hostname = hostname
        self.internal_status_port = internal_status_port
        self.internal_queue_port = internal_queue_port
        self.external_queue_port_send = external_queue_port_send
        self.external_queue_port_recv = external_queue_port_recv
        self.alpha_queue_port_send = alpha_queue_port_send
        self.alpha_queue_port_recv = alpha_queue_port_recv
        self.bravo_servers = []
        self.bravo_secret = "ABCDEFG"
        self.alpha_remote_loadbalancer = ""
        self.lock = None    
    def generate_status_message(self):
        status_message = {
            "hostname": self.hostname,
            "ip_address": self.get_ip_address(),
            "server_type": "BRAVO",
            "server_secret": self.bravo_secret,
            "isReady": self.isReady()

        }
        return(json.dumps(status_message))

    # def get_bravo_secret(): TODO: We will need to write a AWS secret manager call here once we are cloud ready
    def get_ip_address(self):
        return(os.popen("ip -o route get 1.1.1.1 | cut -d \" \" -f 7").read().rstrip())
        
    def isReady(self):
        return True # I will write this one later
    
    def start_cluster_listener(self):
        cluster_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cluster_listener.bind(('0.0.0.0', self.internal_status_port))
        cluster_listener.listen(100)
        while True:
            (client_socket, address) = cluster_listener.accept()
            print("Connection <<STATUS>> Started: " + str(address))
            thread = threading.Thread(self.recv_client_status(client_socket, address))

    def recv_client_status(self, client_socket: socket.socket, address):
        client_socket.send(bytes(self.generate_status_message(), 'utf-8'))
        client_data = client_socket.recv(4096) # RECEIVE UP TO 4096 BYTES

        try: # Make sure the data is valid json
            client_status: str = json.loads(str(client_data.decode()))
        except:
            x = 0 # Error parsing the JSON object that was sent to us
        print("Connection <<STATUS>> Ended: " + str(address))
        client_socket.close()

    def find_servers(self):
        ip_range = os.popen("hostname -i | rev | cut -d ' ' -f1 | cut -d '.' -f3- | rev").read().rstrip()
        print("Starting to search for other bravo servers. Maybe we'll start a book club or something")
        while True:
            for i in range(4):
                for j in range(1,255):
                    current_ip = ip_range + "."  + str(i) + "." + str(j)
                    if current_ip == self.get_ip_address():
                        continue  
                    else: 
                        try:
                            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            client_socket.settimeout(0.01)  
                            client_socket.connect((current_ip, self.internal_status_port))
                            client_data = client_socket.recv(4096) # RECEIVE UP TO 4096 BYTES
                            try: # Make sure the data is valid json
                                client_status = json.loads(str(client_data.decode()))
                                self.lock.acquire()
                                is_duplicate =  False
                                for i in range(len(self.bravo_servers)):
                                    if self.bravo_servers[i]["hostname"] == client_status["hostname"]:
                                        is_duplicate = True
                                        if self.bravo_servers[i]["isReady"] != client_status["isReady"]:
                                            self.bravo_servers[i]["isReady"] = client_status["isReady"]
                                self.lock.release()
                                if (client_status["server_secret"] == self.bravo_secret) and (client_status["isReady"] == True) and (client_status["server_type"] == "BRAVO") and (is_duplicate == False):
                                    self.lock.acquire()
                                    self.bravo_servers.append({"hostname": client_status["hostname"], "ip_address": current_ip, "isReady": client_status["isReady"]})
                                    self.lock.release()
                                elif (client_status["isReady"] == False) and (is_duplicate == False):
                                    print("client at ip " + current_ip + " is not healthy and will not be added until it is")
                            except:
                                print(current_ip + " is not an bravo server or is not functioning")
                        except:
                            continue



    def run(self):
        print("Server of BRAVO type found. Starting to initialize cluster setup...")
        self.lock = threading.Lock()
        cluster_listener = threading.Thread(target=self.start_cluster_listener)
        cluster_listener.start()
        cluster_search = threading.Thread(target=self.find_servers)
        cluster_search.start()
        self.bravo_servers.append({"hostname": self.hostname, "ip_address": self.get_ip_address(), "isReady": self.isReady()})
        while True:
            self.lock.acquire()
            print("Currently running with following bravo_servers: " + str(self.bravo_servers))
            self.lock.release()
            time.sleep(10)
