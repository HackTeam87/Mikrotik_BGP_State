#-*- coding: utf-8 -*-
""" Retrieve down  BGP peers from Mikrotik Routers,
    print "1" if everything is ok,
    else print message about problematic BGP peers """

#instal python 3.8 or ++
# pip3 install telebot
# pip3 install librouteros
# file CheckMessage = 0
# echo 0 > CheckSend.txt
# */10    *       *       *       *    python3 /Mikrotik_BGP_State/BGP_State.py
import sys
import os
from librouteros import  connect
from telebot import TeleBot

#import time
from datetime import datetime
t = datetime.now().strftime("%m/%d/%Y, %H:%M")
#from datetime import timedelta
#Mikrotik
USERNAME = ''
PASSWORD = ''
PORT = ''
#Bot
app = TeleBot(__name__)
if __name__ == '__main__':
    #bot_token
    app.config['api_key'] = ''
    #chat_id
    chat_id = ''
    #app.poll(debug=True)





DEBUG = False

def log(log_msg):
    """Print a message if DEBUG is True"""
    if DEBUG:
        print(log_msg)

def main():

    Dict1 = {}
    Dict2 = {}
    Flag = 1
    Count = 0
    Result = ''
    
    

    #router loopback IP to be checked from a file
    #file should have only router loopback IP perline nothing else

    try:
        RouterID = [line.rstrip('\n') \
        for line in open('RouterID.txt')]
    except Exception:
        e = sys.exc_info()[0]
        log(e)
        sys.exit(1)

    ## Defining the API Connection
    for x in RouterID: 
        try:
            api = connect(username=USERNAME, password=PASSWORD, host=x, port=PORT)
            ## Command run on each router
            bgp_peers = api(cmd='/routing/bgp/peer/print')
            for i in bgp_peers:
                if str(i['disabled']) == 'False':
                    Dict1.update({i['remote-address']: {'router_id': x, 'state': i['state']}} )
            api.close()

        except Exception:
            e = sys.exc_info()[0]
            log(e)

    #Current State Message
    def current_state():
        try:
            CheckMessage = [r_line.rstrip('\n') \
            for r_line in open('CheckSend.txt')]
            return int(CheckMessage[0])
        except Exception:
            e = sys.exc_info()[0]
            log(e)
            sys.exit(1)        
    
    
    #Finding Number of Down Peers.
    for Key, Value  in Dict1.items():
       if Dict1[Key]['state'] != "established":
          Dict2.update({Key: Value})
          Flag = 0
          Count += 1
    if Flag == 0 and current_state() == 0:
        for Key, Value in Dict2.items():
            Result = f"{Count} peer_down:\n neighbor {Key} of router {Value['router_id']} is down!\n time: {t}\n"
            app.send_message(chat_id, Result)
        cmd = r'echo 1 > CheckSend.txt'
        os.system(cmd)
    else:
        cmd = r'echo 0 > CheckSend.txt'
        os.system(cmd)

main()

