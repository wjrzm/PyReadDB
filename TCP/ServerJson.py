#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

import socket
import threading
import socketserver
import json, types,string
import os, time
  
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        message = self.request.recv(20480)
        dataJson = message.decode('utf-8')
        # dataPy = json.loads(dataJson)
        # print ("Receive data '%r'"% (dataJson))
        # print ("Receive jdata from '%r'"% (jdata))
        # deviceID = dataPy[0]['DeviceID']
        # pcCurTimeMS = dataPy[0]['PCCurTimeMS']
        # quat = dataPy[0]['Quat']
        # eul = dataPy[0]['Eul']
        # acc = dataPy[0]['Acc']
        # gyr = dataPy[0]['Gyr']

        # print("DeviceID",deviceID)
        # print("PCCurTimeMS",pcCurTimeMS)
        # print("Quat",quat)
        # print("Eul",eul)
        # print("Acc",acc)
        # print("Gyr",gyr)

        # cur_thread = threading.current_thread()
        # # response = [{"thread":cur_thread.name,"src":rec_src,"dst":rec_dst}]
        # response = [{"thread":cur_thread.name}]

        # jresp = json.dumps(response).encode('utf-8')
        # # print(len(jresp))
        # self.request.sendall(jresp)
        # rec_cmd = "proccess "+rec_src+" -o "+rec_dst
        # print ("CMD '%r'" % (rec_cmd))
        # os.system(rec_cmd)
        return dataJson
           
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    # HOST, PORT = "114.212.171.172", 50001
    HOST, PORT = "172.28.131.113", 50001

    
    socketserver.TCPServer.allow_reuse_address = True
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)

    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print ("Server loop running in thread:", server_thread.name)
    print (" .... waiting for connection")

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()