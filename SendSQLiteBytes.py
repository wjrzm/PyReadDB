import sqlite3
import struct
import socket
import time
import struct

# 不加线程 30+ms
# 加多线程

CSTIME = 62135596800000
TODAYTIME = 1659283200000
STEP = 10

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
        # response = sock.recv(64).decode('utf-8')
        # print (f"Recv: {response}") #json文件

    finally:
        sock.close()

if __name__ == "__main__":
    # HOST, PORT = "114.212.171.172", 50001
    HOST, PORT = "127.0.0.1", 50001

    con = sqlite3.connect('20220809_103505_424.db',check_same_thread=False)
    cur = con.cursor()
    curTime = int(round(time.time() * 1000))
    
    for i in range(1):

        print("----------------------------------read Table:IMUData(北京超核电子)----------------------------------")
        imuSet = cur.execute('SELECT * FROM IMUData order by PCCurTimeMS limit 1')
        imuData = imuSet.fetchall()[i]
        relaTime = imuData[1] -  CSTIME - TODAYTIME
        imuMsg = struct.pack("H", imuData[0]) + struct.pack("I", relaTime) + imuData[2] + imuData[3] + imuData[4] + imuData[5]
        

        print("\n----------------------------------read Table:Kinect(Kinect Azure)----------------------------------")
        kinectSet = cur.execute('SELECT * FROM Kinect order by PCCurTimeMS limit 1')
        kinectData = kinectSet.fetchall()[i]
        # relaTime = kinectData[1] -  CSTIME - TODAYTIME
        kinectMsg = struct.pack("I", kinectData[0]) + struct.pack("I", relaTime) + kinectData[2] + kinectData[3] + kinectData[4]


        print("\n----------------------------------read Table:NTData(诺依腾)----------------------------------")
        noitomSet = cur.execute('SELECT * FROM NTData order by PCCurTimeMS limit 1')
        noitomData = noitomSet.fetchall()[i]
        noitomMsg = struct.pack("I", relaTime) + struct.pack("I", noitomData[1]) + noitomData[2] + noitomData[3] + noitomData[4] + struct.pack("I", noitomData[5]) + noitomData[6] + noitomData[7] + noitomData[8] + noitomData[9] + struct.pack("i", noitomData[10]) #+ noitomData[11]#这里有数据是空的
        



        print("\n----------------------------------read Table:PreasureBoard(压力板)----------------------------------")
        pbSet = cur.execute('SELECT * FROM PreasureBoard order by PCCurTimeMS limit 1')
        pbData = pbSet.fetchall()[i]
        pbMsg = struct.pack("I", pbData[0]) + struct.pack("I", relaTime) + pbData[2].encode('utf-8') + pbData[3]
        
        message = imuMsg + kinectMsg + noitomMsg + pbMsg
        client(HOST, PORT, message)
        print(len(message))

        print(i)

    finalTime = int(round(time.time() * 1000))
    print(finalTime-curTime)

    con.close()