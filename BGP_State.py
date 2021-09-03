#-*- coding: utf-8 -*-
""" Retrieve down  BGP peers from Mikrotik Routers,
    print "1" if everything is ok,
    else print message about problematic BGP peers """

#instal python 3.8 or ++
# pip3 install telebot
# pip3 install librouteros
# */10    *       *       *       *    python3 /Mikrotik_BGP_State/BGP_State.py
import sys
import os
from librouteros import  connect
from telebot import TeleBot
#sql
import sqlite3
con = sqlite3.connect('db.db')
cur = con.cursor()

from datetime import datetime
t = datetime.now().strftime("%m/%d/%Y, %H:%M")
#Mikrotik
USERNAME = 'admin'
PASSWORD = 'admin'
PORT = '8291'
#Bot
app = TeleBot(__name__)
if __name__ == '__main__':
    #bot_token
    app.config['api_key'] = 'Your_Token'
    #chat_id
    chat_id = 'Your_Chat_id'
    #app.poll(debug=True)


DEBUG = False

def log(log_msg):
    """Print a message if DEBUG is True"""
    if DEBUG:
        print(log_msg)

def main():

    Dict1 = []
    Count = 0
    
    #router loopback IP to be checked from a file
    #file should have only router loopback IP perline nothing else


    try:
        RouterID = [ row for row in cur.execute('SELECT id, router_id FROM routers')]
    except Exception:
        e = sys.exc_info()[0]
        log(e)
        sys.exit(1)


    ## Defining the API Connection
    for x in RouterID:
        try:
            api = connect(username=USERNAME, password=PASSWORD, host=x[1], port=PORT)
            
            ## Command run on each router
            bgp_peers = api(cmd='/routing/bgp/peer/print')
            for i in bgp_peers:
                if str(i['disabled']) == 'False':
                    Dict1.append({'id':x[0], 'neighbor': i['remote-address'],'name': i['name'], 'router_id': x[1], 'state': i['state']} )   
            api.close()


        except Exception:
            e = sys.exc_info()[0]
            log(e)

    
    # Finding Number of Down Peers && Update Database.
    for state in Dict1:
        if state['state'] != "established":
            cur.execute('''INSERT OR IGNORE INTO bgp_sessions (session_id, name, neighbor, up, down) 
            VALUES (?, ?, ?, ?, ?)''', (state['id'],state['name'],state['neighbor'], 0, 1))
            con.commit()
         
   

    # Send Message If And Update Database
    for status  in cur.execute('''SELECT r.router_id, b.up, b.down, b.telegram_status, b.name, b.neighbor, b.session_id
    FROM routers r LEFT JOIN bgp_sessions b on b.session_id = r.id'''):
        if status[2] and not status[3]:
            Count += 1
            app.send_message(chat_id, f"{Count} peer_down:\n neighbor {status[4]} {status[5]} of router {status[0]} is down!\n time: {t}\n")
            cur.execute("UPDATE bgp_sessions SET telegram_status=? WHERE session_id=?",(1, status[6]))
            con.commit()
           
            
    
    # Dict1 = [] # Debag
    if not Dict1:

       for message in cur.execute('''SELECT b.name, b.neighbor, r.router_id 
       FROM routers r 
       LEFT JOIN bgp_sessions b on b.session_id = r.id '''):
           m =  f"{Count} peer_down:\n neighbor {message[0]} {message[1]} of router {message[2]} is up!\n time: {t}\n"
           app.send_message(chat_id, m)
         
       cur.execute("UPDATE bgp_sessions SET up=?, down=?, telegram_status=? WHERE down=?",(1,0,0,1))
       con.commit()

main()

