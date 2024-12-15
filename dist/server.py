logo = """
  _______ ______ _  _______   ____   _____ _____ _____ ____  _      ______      _    _          
 |__   __|  ____| |/ /  __ \ / __ \ / ____/ ____|_   _|  _ \| |    |  ____|    | |  | |   /\    
    | |  | |__  | ' /| |__) | |  | | (___| (___   | | | |_) | |    | |__       | |__| |  /  \   
    | |  |  __| |  < |  ___/| |  | |\___ \\\\___ \  | | |  _ <| |    |  __|      |  __  | / /\ \  
    | |  | |____| . \| |    | |__| |____) |___) |_| |_| |_) | |____| |____     | |  | |/ ____ \ 
    |_|  |______|_|\_\_|     \____/|_____/_____/|_____|____/|______|______|    |_|  |_/_/    \_\\


    Fun to write Clustering Program Developed by TekPossible Systems (Griffin Kiesecker)    
    This is mainly just to do something kinda fun and refresh my python skills
"""

import os
from alpha.alpha import AlphaServer
from bravo.bravo import BravoServer

__hostname = os.popen("hostname").read().rstrip()
__server_alpha = "AlphaServer"
__server_bravo = "BravoServer"

# ALPHA PORTS
alpha_internal_status = 10001
alpha_internal_queue = 10002
alpha_external_queue_send = 8000
alpha_external_queue_recv  = 8001

# BRAVO PORTS
bravo_internal_status = 10003
bravo_internal_queue = 10004
bravo_external_queue_send = 8002
bravo_external_queue_recv  = 8003

print(logo)

if __server_alpha in __hostname: 
    server_a = AlphaServer(__hostname, alpha_internal_status, alpha_internal_queue, alpha_external_queue_send, alpha_external_queue_recv, bravo_external_queue_send, bravo_external_queue_recv );
    server_a.run()

if __server_bravo in __hostname: 
    server_b = BravoServer(__hostname, bravo_internal_status, bravo_internal_queue, bravo_external_queue_send, bravo_external_queue_recv, alpha_external_queue_send, alpha_external_queue_recv );
    server_b.run()
