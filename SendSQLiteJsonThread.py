import sqlite3
import struct
import socket
import json
import time
import threading

CSTIME = 62135596800000
TODAYTIME = 1659283200000
STEP = 100

#OverallTime: 3456
#SendTime: 3112

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
        # print(len(message.encode('utf-8')))
        sock.sendall(message.encode('utf-8'))
        # response = sock.recv(512).decode('utf-8')
        # jresp = json.loads(response)

        # print (f"Recv: {response}") #json文件
        # print ("Recv: {}".format(jresp))

    finally:
        sock.close()

def imuQuery(row):
    # print("----------------------------------read Table:IMUData(北京超核电子)----------------------------------")
    imuData = [{'DeviceID':row[0],
        'PCCurTimeMS':row[1],
        'Quat':getFloatFromByteArray(row[2],4),
        'Eul':getFloatFromByteArray(row[3],3),
        'Acc':getFloatFromByteArray(row[4],3),
        'Gyr':getFloatFromByteArray(row[5],3)
        }]

    imuJson = json.dumps(imuData)
    return imuJson

def kinectQuery(row):
    kinectData = [{
            'DeviceTimeMS':row[0],
            'PCCurTimeMS':row[1],
            'Pos3dRawData':getFloatFromByteArray(row[2],3),
            'Pos2dRawData':getFloatFromByteArray(row[3],2),
            'RotationRawData':getFloatFromByteArray(row[4],4)
        }]

    kinectJson = json.dumps(kinectData)
    return kinectJson

def noitomQuery(row):
    noitomData = [{
            'PCCurTimeMS':row[0],
            'JointTag':row[1],
            'JointLocalPosition':getFloatFromByteArray(row[2],3),
            'JointLocalRotation':getFloatFromByteArray(row[3],4),
            'JointLocalRotationByEuler':getFloatFromByteArray(row[4],3),
            'SensorModuleId':row[5],
            'SensorModulePosture':getFloatFromByteArray(row[6],4),
            'SensorModuleAngularVelocity':getFloatFromByteArray(row[7],3),
            'SensorModuleAcceleratedVelocity':getFloatFromByteArray(row[8],3),
            'BodyPartPosture':getFloatFromByteArray(row[9],4),
            'ParentJointTag':row[10],
            # 'ChildrenJointsID':''.join([chr(x) for x in getIntArrayFromByteArray(row[11])]),
        }]

    noitomJson = json.dumps(noitomData)
    return noitomJson

def pbQuery(row):
    pbData = [{
            'DeviceTimeStamp':row[0],
            'PCCurTimeMS':row[1],
            'BoardIP':row[2],
            'Data':str(row[3])
        }]

    pbJson = json.dumps(pbData)
    return pbJson

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
        sql = cur.execute('SELECT * FROM Kinect order by PCCurTimeMS').fetchall()
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
    HOST, PORT = "114.212.171.172", 50001

    con = sqlite3.connect('20220809_103505_424.db')
    cur = con.cursor()
    curTime = int(round(time.time() * 1000))

    imuThread = imuThread('imuThread',HOST, PORT)
    kinectThread = kinectThread('kinectThread',HOST, PORT)
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