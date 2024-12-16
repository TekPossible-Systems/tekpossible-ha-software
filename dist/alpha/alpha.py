import os
import socket
import threading
import json
import time
import uuid

class AlphaServer:
    def __init__(self, hostname, internal_status_port, internal_queue_port, external_queue_port_send, external_queue_port_recv, bravo_queue_port_send, bravo_queue_port_recv  ):
        self.hostname = hostname
        self.internal_status_port = internal_status_port
        self.internal_queue_port = internal_queue_port
        self.external_queue_port_send = external_queue_port_send
        self.external_queue_port_recv = external_queue_port_recv
        self.bravo_queue_port_send = bravo_queue_port_send
        self.bravo_queue_port_recv = bravo_queue_port_recv
        self.alpha_servers = []
        self.alpha_secret = "ABCDEFG"
        self.bravo_remote_loadbalancer = ""
        self.lock = None    
        self.msg_queue = []
        self.queue_updated = None

    def generate_status_message(self):
        status_message = {
            "hostname": self.hostname,
            "ip_address": self.get_ip_address(),
            "server_type": "ALPHA",
            "server_secret": self.alpha_secret,
            "isReady": self.isReady()

        }
        return(json.dumps(status_message))
    
    # def generate_queue_message(self, queue_data):

    def start_queue_recv(self):
        queue_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        queue_listener.bind(('0.0.0.0', self.internal_queue_port))
        queue_listener.listen(100)
        while True:
            (client_socket, address) = queue_listener.accept()
            print("Connection <<INT-QUEUE>> Started: " + str(address))
            thread = threading.Thread(self.queue_handler_recv(client_socket, address))

    def queue_handler_recv(self, client_socket: socket.socket, address):
        while True:
            self.lock.acquire()
            queue_msg = client_socket.recv(4096)
            self.msg_queue.append(json.loads(str(queue_msg.decode())))
            queue_msg.send("ACK")
            self.lock.release()

    def start_queue_send(self):
        while True:
            if self.queue_updated != None:
                self.lock.acquire()
                self.msg_queue.append(self.queue_updated)
                for alpha_server in self.alpha_servers:
                    if alpha_server['isReady']:
                        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        send_socket.connect(( alpha_server['ip_address'], self.internal_queue_port))
                        response = send_socket.recv(4096)
                        if "ACK" in str(response.decode()):
                            send_socket.close()
                        else:
                            print("Error in sending queue update to server " + alpha_server['ip_address'] + "!")
                            send_socket.close()
                self.queue_updated = None
                self.lock.release()
            time.sleep(5) # At the moment, wait 5 seconds 

    # def get_alpha_secret(): TODO: We will need to write a AWS secret manager call here once we are cloud ready
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
        time.sleep(0.2)
        print("Connection <<STATUS>> Ended: " + str(address))
        client_socket.close()

    def find_servers(self):
        ip_range = os.popen("hostname -i | rev | cut -d ' ' -f1 | cut -d '.' -f3- | rev").read().rstrip()
        print("Starting to search for other alpha servers. Maybe we'll start a book club or something")
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
                            client_socket.close()
                            try: # Make sure the data is valid json
                                client_status = json.loads(str(client_data.decode()))
                                is_duplicate =  False
                                self.lock.acquire()
                                for i in range(len(self.alpha_servers)):
                                    if self.alpha_servers[i]["hostname"] == client_status["hostname"]:
                                        is_duplicate = True
                                        if self.alpha_servers[i]["isReady"] != client_status["isReady"]:
                                            self.alpha_servers[i]["isReady"] = client_status["isReady"]
                                self.lock.release()
                                if (client_status["server_secret"] == self.alpha_secret) and (client_status["isReady"] == True) and (client_status["server_type"] == "ALPHA") and (is_duplicate == False):
                                    self.lock.acquire()
                                    self.alpha_servers.append({"hostname": client_status["hostname"], "ip_address": current_ip, "isReady": client_status["isReady"]})
                                    self.lock.release()
                                elif (client_status["isReady"] == False) and (is_duplicate == False):
                                    print("client at ip " + current_ip + " is not healthy and will not be added until it is")
                            except:
                                print(current_ip + " is not an alpha server or is not functioning")
                        except:
                            continue



    def run(self):
        print("Server of ALPHA type found. Starting to initialize cluster setup...")
        self.lock = threading.Lock()
        cluster_listener = threading.Thread(target=self.start_cluster_listener)
        cluster_listener.start()
        cluster_search = threading.Thread(target=self.find_servers)
        cluster_search.start()
        queue_recv = threading.Thread(target=self.start_queue_recv)
        queue_recv.start()
        queue_send = threading.Thread(target=self.start_queue_send)
        queue_send.start()
        self.alpha_servers.append({"hostname": self.hostname, "ip_address": self.get_ip_address(), "isReady": self.isReady()})
        while True:
            print("Currently running with following alpha_servers: " + str(self.alpha_servers))
            time.sleep(10)
