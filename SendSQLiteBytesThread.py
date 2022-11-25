import sqlite3
import struct
import socket
import time
import threading

# 不加线程 30+ms
# 加多线程

CSTIME = 62135596800000
TODAYTIME = 1659283200000
STEP = 100

lock = threading.Lock()

def getFloatFromByteArray(b, count):
    rt = []
    for i in range(count):
        rt.append(struct.unpack('f', b[(i*4):((i+1)*4)])[0])

    return rt

def getIntArrayFromByteArray(b):
    rt = []
    for i in range( (int)(len(b)/4) ):
        rt.append(struct.unpack('i', b[(i*4):((i+1)*4)])[0])

    return rt

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    try:
        # print ("Send: {}".format(message))
        # print(len(message))
        sock.sendall(message)
        #response = sock.recv(64).decode('utf-8')
        #print (f"Recv: {response}") #json文件

    finally:
        sock.close()

def imuQuery(imuData):
    relaTime = imuData[1] -  CSTIME - TODAYTIME
    imuMsg = struct.pack("H", imuData[0]) + struct.pack("I", relaTime) + imuData[2] + imuData[3] + imuData[4] + imuData[5]
    return imuMsg

def kinectQuery(kinectData):
    relaTime = kinectData[1] -  CSTIME - TODAYTIME
    kinectMsg = struct.pack("I", kinectData[0]) + struct.pack("I", relaTime) + kinectData[2] + kinectData[3] + kinectData[4]
    return kinectMsg

def noitomQuery(noitomData):
    relaTime = noitomData[0] -  CSTIME - TODAYTIME
    noitomMsg = struct.pack("I", relaTime) + struct.pack("I", noitomData[1]) + noitomData[2] + noitomData[3] + noitomData[4] + struct.pack("I", noitomData[5]) + noitomData[6] + noitomData[7] + noitomData[8] + noitomData[9] + struct.pack("i", noitomData[10]) #+ noitomData[11]#这里有数据是空的
    return noitomMsg

def pbQuery(pbData):
    relaTime = pbData[1] -  CSTIME - TODAYTIME
    pbMsg = struct.pack("I", pbData[0]) + struct.pack("I", relaTime) + pbData[2].encode('utf-8') + pbData[3]
    return pbMsg

class imuThread(threading.Thread):
    def __init__(self,n,ip,port):
        self.n = n
        self.ip = ip
        self.port = port

    def readDB(self):
        sql = cur.execute('SELECT * FROM IMUData order by PCCurTimeMS').fetchall()
        return sql
        
    def run(self, i, sql):
        print('task',self.n)
        try:
            lock.acquire(True)
            client(self.ip, self.port, imuQuery(sql[i]))
        finally:
            lock.release()

class kinectThread(threading.Thread):
    def __init__(self,n,ip,port):
        self.n = n
        self.ip = ip
        self.port = port
        
    def readDB(self):
        sql = cur.execute('SELECT * FROM kinect order by PCCurTimeMS').fetchall()
        return sql
        
    def run(self, i, sql):
        print('task',self.n)
        try:
            lock.acquire(True)
            client(self.ip, self.port, kinectQuery(sql[i]))
        finally:
            lock.release()
            
class noitomThread(threading.Thread):
    def __init__(self,n,ip,port):
        self.n = n
        self.ip = ip
        self.port = port
        
    def readDB(self):
        sql = cur.execute('SELECT * FROM NTData order by PCCurTimeMS').fetchall()
        return sql
        
    def run(self, i, sql):
        print('task',self.n)
        try:
            lock.acquire(True)
            client(self.ip, self.port, noitomQuery(sql[i]))
        finally:
            lock.release()

class pbThread(threading.Thread):
    def __init__(self,n,ip,port):
        self.n = n
        self.ip = ip
        self.port = port
        
    def readDB(self):
        sql = cur.execute('SELECT * FROM PreasureBoard order by PCCurTimeMS').fetchall()
        return sql
        
    def run(self, i, sql):
        print('task',self.n)
        try:
            lock.acquire(True)
            client(self.ip, self.port, pbQuery(sql[i]))
        finally:
            lock.release()

if __name__ == "__main__":
    # HOST, PORT = "114.212.171.172", 50001
    HOST, PORT = "172.28.131.113", 50001

    con = sqlite3.connect('20220809_103505_424.db',check_same_thread=False)
    cur = con.cursor()
    curTime = int(round(time.time() * 1000))

    imuThread = imuThread('imuThread', HOST, PORT)
    kinectThread = kinectThread('kinectThread', HOST, PORT)
    noitomThread = noitomThread('noitomThread',HOST, PORT)
    pbThread = pbThread('pbThread',HOST, PORT)

    imuSql = imuThread.readDB()
    kinectSql = kinectThread.readDB()
    noitomSql = noitomThread.readDB()
    pbSql = pbThread.readDB()

    beforeSendTime = int(round(time.time() * 1000))
    for i in range(STEP):
        imuThread.run(i,imuSql)
        kinectThread.run(i,kinectSql)
        noitomThread.run(i,noitomSql)
        pbThread.run(i,pbSql)
    afterSendTime = int(round(time.time() * 1000))

    con.close()
    finalTime = int(round(time.time() * 1000))
    print("OverallTime:",finalTime-curTime)
    print("SendTime:",afterSendTime-beforeSendTime)