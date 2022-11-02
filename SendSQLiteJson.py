import sqlite3
import struct
import socket
import json
import time
import struct

CSTIME = 62135596800000
TODAYTIME = 1659283200000

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
        print(len(message.encode('utf-8')))
        sock.sendall(message.encode('utf-8'))
        # response = sock.recv(512).decode('utf-8')
        # jresp = json.loads(response)

        # print (f"Recv: {response}") #json文件
        # print ("Recv: {}".format(jresp))

    finally:
        sock.close()

if __name__ == "__main__":
    HOST, PORT = "114.212.171.172", 50001

    con = sqlite3.connect('20220809_103505_424.db')
    cur = con.cursor()
    curTime = int(round(time.time() * 1000))


    print("----------------------------------read Table:IMUData(北京超核电子)----------------------------------")
    for row in cur.execute('SELECT * FROM IMUData order by PCCurTimeMS limit 1'):
        # print("DeviceID(long integer):", row[0])
        # print("PCCurTimeMS(long integer):", row[1])
        # print("Quat(float 四元数wxyz):", getFloatFromByteArray(row[2],4))#只有这里的w在最前面，他们的程序默认就这样
        # print("Eul(float 欧拉角,可能是yaw,roll,pitch):", getFloatFromByteArray(row[3],3))
        # print("Acc(float 加速度xyz):", getFloatFromByteArray(row[4],3))
        # print("Gyr(float 角速度xyz):", getFloatFromByteArray(row[5],3))
        # print("\n")
        imuData = [{'DeviceID':row[0],
        'PCCurTimeMS':row[1],
        'Quat':getFloatFromByteArray(row[2],4),
        'Eul':getFloatFromByteArray(row[3],3),
        'Acc':getFloatFromByteArray(row[4],3),
        'Gyr':getFloatFromByteArray(row[5],3)
        }]

        imuJson = json.dumps(imuData)
        client(HOST, PORT, imuJson)

    print("\n\n\n----------------------------------read Table:Kinect(Kinect Azure)----------------------------------")
    for row in cur.execute('SELECT * FROM Kinect order by PCCurTimeMS limit 1'):
    #     print("DeviceTimeMS(long integer):", row[0])
    #     print("PCCurTimeMS(long integer):", row[1])
    #     print("Pos3dRawData(float 3d位置xyz):", getFloatFromByteArray(row[2],3))
    #     print("Pos2dRawData(float 2d位置xy):", getFloatFromByteArray(row[3],2))
    #     print("RotationRawData(float 旋转四元数xyzw):", getFloatFromByteArray(row[4],4))#这里的w在最后面
    #     print("\n")
        kinectData = [{
            'DeviceTimeMS':row[0],
            'PCCurTimeMS':row[1],
            'Pos3dRawData':getFloatFromByteArray(row[2],3),
            'Pos2dRawData':getFloatFromByteArray(row[3],2),
            'RotationRawData':getFloatFromByteArray(row[4],4)
        }]

        kinectJson = json.dumps(kinectData)
        client(HOST, PORT, kinectJson)



    print("\n\n\n----------------------------------read Table:NTData(诺依腾)----------------------------------")
    for row in cur.execute('SELECT * FROM NTData order by PCCurTimeMS limit 1'):
    #     print("PCCurTimeMS(long integer):", row[0])
    #     print("JointTag(integer):", row[1]) #关于节点的数值，参见本文件最后
    #     print("JointLocalPosition(float  本地位置xyz):", getFloatFromByteArray(row[2],3))
    #     print("JointLocalRotation(float  本地旋转四元数xyzw):", getFloatFromByteArray(row[3],4))
    #     print("JointLocalRotationByEuler(float  本地旋转欧拉角):", getFloatFromByteArray(row[4],3))#可能是yaw,roll,pitch
    #     print("SensorModuleId(long integer 传感器模块的id):", row[5])#目前都是0，不知道为啥
    #     print("SensorModulePosture(float  传感器模块的姿态四元数xyzw):", getFloatFromByteArray(row[6],4))#目前都是0，不知道为啥
    #     print("SensorModuleAngularVelocity(float 传感器模块的角速度xyz):", getFloatFromByteArray(row[7],3))#目前都是0，不知道为啥
    #     print("SensorModuleAcceleratedVelocity(float 传感器模块的加速度xyz):", getFloatFromByteArray(row[8],3))#目前都是0，不知道为啥
    #     print("BodyPartPosture(float '身体部位'的姿态四元素xyzw):", getFloatFromByteArray(row[9],4))#目前都是0，不知道为啥
    #     print("ParentJointTag(integer 父亲节点的id):", row[10])#根节点没有父亲，数值为-1
    #     print("ChildrenJointsID(integer数组， 所有孩子节点的id):", ''.join([chr(x) for x in getIntArrayFromByteArray(row[11])]))
    #     print("\n")
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
        client(HOST, PORT, noitomJson)


    print("\n\n\n----------------------------------read Table:PreasureBoard(压力板)----------------------------------")
    for row in cur.execute('SELECT * FROM PreasureBoard order by PCCurTimeMS limit 1'):
    #     print("DeviceTimeStamp(long integer):", row[0])
    #     print("PCCurTimeMS(integer):", row[1])
    #     print("BoardIP(string  板子的Ip地址):", row[2])#一共三块小的板子拼接成一块大的，每块都有自己的ip
    #     for h in range(60):
    #         s = ""
    #         for w in range(60):
    #             s += str(row[3][h*60+w])
    #             if(  w+1<60):
    #                 s += ", "
    #         print(s)

    #     print("\n")
        pbData = [{
            'DeviceTimeStamp':row[0],
            'PCCurTimeMS':row[1],
            'BoardIP':row[2],
            'Data':str(row[3])
        }]
        pbJson = json.dumps(pbData)
        client(HOST, PORT, pbJson)

    con.close()
    finalTime = int(round(time.time() * 1000))
    print(finalTime-curTime)