#!/usr/bin/env python
# -*- coding:utf-8 -*-
#

import socket
import threading
# import SocketServer
import json

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    try:
        print ("Send: {}".format(message))
        sock.sendall(message.encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        jresp = json.loads(response)

        print ("Recv: {}".format(response)) #json文件
        print ("Recv: {}".format(jresp))

    finally:
        sock.close()

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "114.212.171.172", 50001
    msg1 = [{'src':"zj", 'dst':"zjdst"}]
    msg2 = [{'src':"ln", 'dst':"lndst"}]
    msg3 = [{'src':"xj", 'dst':"xjdst"}]

    jmsg1 = json.dumps(msg1)
    jmsg2 = json.dumps(msg2)
    jmsg3 = json.dumps(msg3)

    client(HOST, PORT, jmsg1)
    client(HOST, PORT, jmsg2)
    client(HOST, PORT, jmsg3)
