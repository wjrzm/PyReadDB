import sqlite3
import struct
import numpy as np
import quaternion
import time
import matplotlib.pyplot as plt
from dtaidistance import dtw

CSTIME = 62135596800000
TODAYTIME = 1659283200000

# 传入数据之前要进行数据处理操作，确保数据都是等间隔进入

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

def slerp(startImu,endImu,kinect):
    cosTheta = startImu[2]*endImu[2] + startImu[3]*endImu[3] + startImu[4]*endImu[4] + startImu[5]*endImu[5]

    if cosTheta < 0.0:
        endImu[2] = -endImu[2]
        endImu[3] = -endImu[3]
        endImu[4] = -endImu[4]
        endImu[5] = -endImu[5]
        cosTheta = -cosTheta
    
    if cosTheta > 0.9999:
        frontScale = (endImu[0] - kinect[0]) / (endImu[0] - startImu[0])
        backScale = (kinect[0] - startImu[0]) / (endImu[0] - startImu[0])
    else:
        sinTheta = np.sqrt(1-cosTheta*cosTheta)
        theta = np.arctan2(sinTheta,cosTheta)
        frontScale = np.sin((endImu[0] - kinect[0]) / (endImu[0] - startImu[0])*theta/sinTheta)
        backScale = np.sin((kinect[0] - startImu[0]) / (endImu[0] - startImu[0]) * theta) / sinTheta
    
    wSyn = startImu[2] * frontScale + endImu[2] * backScale
    xSyn = startImu[3] * frontScale + endImu[3] * backScale
    ySyn = startImu[4] * frontScale + endImu[4] * backScale
    zSyn = startImu[5] * frontScale + endImu[5] * backScale
    return wSyn, xSyn, ySyn, zSyn

def lerp(startImu,endImu,kinect):
    frontScale = (endImu[0] - kinect[0]) / (endImu[0] - startImu[0])
    backScale = (kinect[0] - startImu[0]) / (endImu[0] - startImu[0])
    wSyn = startImu[2] * frontScale + endImu[2] * backScale
    xSyn = startImu[3] * frontScale + endImu[3] * backScale
    ySyn = startImu[4] * frontScale + endImu[4] * backScale
    zSyn = startImu[5] * frontScale + endImu[5] * backScale
    return wSyn, xSyn, ySyn, zSyn


def timeSynImu(npImu,npKinect):
    i = 0
    j = 0
    k = 1
    synImu = [] # time,id,w,x,y,z
    synKinect = []
    
    
    while k < npImu.shape[0] and i < npKinect.shape[0]:
        if npImu[j][0] <= npKinect[i][0] and npImu[k][0] >= npKinect[i][0]:
            if npImu[k][0] - npImu[j][0] != 0:

                # frontScale = (npImu[k][0] - npKinect[i][0]) / (npImu[k][0] - npImu[j][0])
                # backScale = (npKinect[i][0] - npImu[j][0]) / (npImu[k][0] - npImu[j][0])# need to fix
                # wSyn = npImu[j][2] * frontScale + npImu[k][2] * backScale
                # xSyn = npImu[j][3] * frontScale + npImu[k][3] * backScale
                # ySyn = npImu[j][4] * frontScale + npImu[k][4] * backScale
                # zSyn = npImu[j][5] * frontScale + npImu[k][5] * backScale
                
                # wSyn,xSyn,ySyn,zSyn = slerp(npImu[j],npImu[k],npKinect[i])
                wSyn,xSyn,ySyn,zSyn = lerp(npImu[j],npImu[k],npKinect[i])
                
                synImu.append([npKinect[i][0],npImu[j][1],wSyn,xSyn,ySyn,zSyn])
                synKinect.append(npKinect[i])
                i += 1
                j += 1
                k = j + 1
            else:
                j += 1
                k = j + 1
        elif npImu[j][0] > npKinect[i][0]:
            i += 1
        elif npImu[k][0] < npKinect[i][0]:
            j += 1
            k = j + 1
    
    npSynImu = np.asarray(synImu)
    npSynKinect = np.asarray(synKinect)
    return npSynImu, npSynKinect

con = sqlite3.connect('20220809_103505_424.db')
cur = con.cursor()

npImu = []
npKinect = []


print("----------------------------------read Table:IMUData(北京超核电子)----------------------------------")
for row in cur.execute('SELECT * FROM IMUData where DeviceID = 1 order by PCCurTimeMS '):
    # print("DeviceID(long integer):", row[0])
    # print("PCCurTimeMS(long integer):", row[1])
    # print("Quat(float 四元数wxyz):", getFloatFromByteArray(row[2],4))#只有这里的w在最前面，他们的程序默认就这样
    # print("Eul(float 欧拉角,可能是yaw,roll,pitch):", getFloatFromByteArray(row[3],3))
    # print("Acc(float 加速度xyz):", getFloatFromByteArray(row[4],3))
    # print("Gyr(float 角速度xyz):", getFloatFromByteArray(row[5],3))
    # print("\n")

    relaTime = row[1] -  CSTIME - TODAYTIME

    w = getFloatFromByteArray(row[2],4)[0]
    x = getFloatFromByteArray(row[2],4)[1]
    y = getFloatFromByteArray(row[2],4)[2]
    z = getFloatFromByteArray(row[2],4)[3]
    # quatImu = np.quaternion(w, x, y, z)
    
    npImu.append([relaTime,row[0],w,x,y,z])# faster
    # npImu = np.append(npImu,np.array([[relaTime,row[0],w,x,y,z]]),axis = 0)

npImu = np.asarray(npImu) 
print(npImu)


print("\n\n\n----------------------------------read Table:Kinect(Kinect Azure)----------------------------------")
for row in cur.execute('SELECT * FROM Kinect order by PCCurTimeMS '):
    # print("DeviceTimeMS(long integer):", row[0])
    # print("PCCurTimeMS(long integer):", row[1])
    # print("Pos3dRawData(float 3d位置xyz):", getFloatFromByteArray(row[2],3))
    # print("Pos2dRawData(float 2d位置xy):", getFloatFromByteArray(row[3],2))
    # print("RotationRawData(float 旋转四元数xyzw):", getFloatFromByteArray(row[4],4))#这里的w在最后面
    # print("\n")
    
    relaTime = row[1] -  CSTIME - TODAYTIME
    npKinect.append([relaTime,row[0]])
    # npKinect = np.append(npKinect,np.array([[relaTime,row[0]]]),axis = 0)
npKinect = np.asarray(npKinect) 
print(npKinect.shape)
time0 = time.time()
timeSynedImu,timeSynedKinect = timeSynImu(npImu,npKinect)
time1 = time.time()
print(time1 - time0)
print(timeSynedImu.shape)
print(timeSynedKinect.shape)

distImu = dtw.distance_fast(timeSynedImu[:,2], npImu[:,2])

print(distImu)

plt.plot(timeSynedImu[:,2],color = 'r')#s-:方形
plt.plot(npImu[:,2],color = 'b')#s-:方形
plt.xlabel("region length")#横坐标名字
plt.ylabel("accuracy")#纵坐标名字
plt.show()


# print("\n\n\n----------------------------------read Table:NTData(诺依腾)----------------------------------")
# for row in cur.execute('SELECT * FROM NTData order by PCCurTimeMS limit 3'):
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



# print("\n\n\n----------------------------------read Table:PreasureBoard(压力板)----------------------------------")
# for row in cur.execute('SELECT * FROM PreasureBoard order by PCCurTimeMS limit 3'):
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

con.close()

