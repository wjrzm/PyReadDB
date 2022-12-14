from ctypes import sizeof
import sqlite3
import struct

# con = sqlite3.connect('testDB.db')
# cur = con.cursor()

# for row in cur.execute('SELECT * FROM table1'):
#     print(row[0][0], ", ", row[0][1], ", ", row[0][2])

# for row in cur.execute('SELECT * FROM table2'):
#     v1 = struct.unpack('i', bytes(row[0][0:4]))
#     v2 = struct.unpack('i', bytes(row[0][4:8]))
#     v3 = struct.unpack('i', bytes(row[0][8:12]))
#     print(v1[0], ", ", v2[0], ", ", v3[0])

#     v1 = struct.unpack('f', bytes(row[1][0:4]))
#     v2 = struct.unpack('f', bytes(row[1][4:8]))
#     v3 = struct.unpack('f', bytes(row[1][8:12]))
#     print(v1[0], ", ", v2[0], ", ", v3[0])



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


con = sqlite3.connect('20220809_103505_424.db')
cur = con.cursor()

print("----------------------------------read Table:IMUData(北京超核电子)----------------------------------")
for row in cur.execute('SELECT * FROM IMUData order by PCCurTimeMS limit 3'):
    print("DeviceID(long integer):", row[0])
    print("PCCurTimeMS(long integer):", row[1])
    print("Quat(float 四元数wxyz):", getFloatFromByteArray(row[2],4))#只有这里的w在最前面，他们的程序默认就这样
    print("Eul(float 欧拉角,可能是yaw,roll,pitch):", getFloatFromByteArray(row[3],3))
    print("Acc(float 加速度xyz):", getFloatFromByteArray(row[4],3))
    print("Gyr(float 角速度xyz):", getFloatFromByteArray(row[5],3))
    print("\n")



print("\n\n\n----------------------------------read Table:Kinect(Kinect Azure)----------------------------------")
for row in cur.execute('SELECT * FROM Kinect order by PCCurTimeMS limit 3'):
    print("DeviceTimeMS(long integer):", row[0])
    print("PCCurTimeMS(long integer):", row[1])
    print("Pos3dRawData(float 3d位置xyz):", getFloatFromByteArray(row[2],3))
    print("Pos2dRawData(float 2d位置xy):", getFloatFromByteArray(row[3],2))
    print("RotationRawData(float 旋转四元数xyzw):", getFloatFromByteArray(row[4],4))#这里的w在最后面
    print("\n")



print("\n\n\n----------------------------------read Table:NTData(诺依腾)----------------------------------")
for row in cur.execute('SELECT * FROM NTData order by PCCurTimeMS limit 3'):
    print("PCCurTimeMS(long integer):", row[0])
    print("JointTag(integer):", row[1]) #关于节点的数值，参见本文件最后
    print("JointLocalPosition(float  本地位置xyz):", getFloatFromByteArray(row[2],3))
    print("JointLocalRotation(float  本地旋转四元数xyzw):", getFloatFromByteArray(row[3],4))
    print("JointLocalRotationByEuler(float  本地旋转欧拉角):", getFloatFromByteArray(row[4],3))#可能是yaw,roll,pitch
    print("SensorModuleId(long integer 传感器模块的id):", row[5])#目前都是0，不知道为啥
    print("SensorModulePosture(float  传感器模块的姿态四元数xyzw):", getFloatFromByteArray(row[6],4))#目前都是0，不知道为啥
    print("SensorModuleAngularVelocity(float 传感器模块的角速度xyz):", getFloatFromByteArray(row[7],3))#目前都是0，不知道为啥
    print("SensorModuleAcceleratedVelocity(float 传感器模块的加速度xyz):", getFloatFromByteArray(row[8],3))#目前都是0，不知道为啥
    print("BodyPartPosture(float '身体部位'的姿态四元素xyzw):", getFloatFromByteArray(row[9],4))#目前都是0，不知道为啥
    print("ParentJointTag(integer 父亲节点的id):", row[10])#根节点没有父亲，数值为-1
    print("ChildrenJointsID(integer数组， 所有孩子节点的id):", ''.join([chr(x) for x in getIntArrayFromByteArray(row[11])]))
    print("\n")



print("\n\n\n----------------------------------read Table:PreasureBoard(压力板)----------------------------------")
for row in cur.execute('SELECT * FROM PreasureBoard order by PCCurTimeMS limit 3'):
    print("DeviceTimeStamp(long integer):", row[0])
    print("PCCurTimeMS(integer):", row[1])
    print("BoardIP(string  板子的Ip地址):", row[2])#一共三块小的板子拼接成一块大的，每块都有自己的ip
    for h in range(60):
        s = ""
        for w in range(60):
            s += str(row[3][h*60+w])
            if(  w+1<60):
                s += ", "
        print(s)

    print("\n")

con.close()


#诺依腾设备的骨骼节点的枚举数值
    # public enum EMCPJointTag
    # {
    #     JointTag_Invalid=-1,
    #     JointTag_Hips=0,
    #     JointTag_RightUpLeg=1,
    #     JointTag_RightLeg=2,
    #     JointTag_RightFoot=3,
    #     JointTag_LeftUpLeg=4,
    #     JointTag_LeftLeg=5,
    #     JointTag_LeftFoot=6,
    #     JointTag_Spine=7,
    #     JointTag_Spine1=8,
    #     JointTag_Spine2=9,
    #     JointTag_Neck=10,
    #     JointTag_Neck1=11,
    #     JointTag_Head=12,
    #     JointTag_RightShoulder=13,
    #     JointTag_RightArm=14,
    #     JointTag_RightForeArm=15,
    #     JointTag_RightHand=16,
    #     JointTag_RightHandThumb1=17,
    #     JointTag_RightHandThumb2=18,
    #     JointTag_RightHandThumb3=19,
    #     JointTag_RightInHandIndex=20,
    #     JointTag_RightHandIndex1=21,
    #     JointTag_RightHandIndex2=22,
    #     JointTag_RightHandIndex3=23,
    #     JointTag_RightInHandMiddle=24,
    #     JointTag_RightHandMiddle1=25,
    #     JointTag_RightHandMiddle2=26,
    #     JointTag_RightHandMiddle3=27,
    #     JointTag_RightInHandRing=28,
    #     JointTag_RightHandRing1=29,
    #     JointTag_RightHandRing2=30,
    #     JointTag_RightHandRing3=31,
    #     JointTag_RightInHandPinky=32,
    #     JointTag_RightHandPinky1=33,
    #     JointTag_RightHandPinky2=34,
    #     JointTag_RightHandPinky3=35,
    #     JointTag_LeftShoulder=36,
    #     JointTag_LeftArm=37,
    #     JointTag_LeftForeArm=38,
    #     JointTag_LeftHand=39,
    #     JointTag_LeftHandThumb1=40,
    #     JointTag_LeftHandThumb2=41,
    #     JointTag_LeftHandThumb3=42,
    #     JointTag_LeftInHandIndex=43,
    #     JointTag_LeftHandIndex1=44,
    #     JointTag_LeftHandIndex2=45,
    #     JointTag_LeftHandIndex3=46,
    #     JointTag_LeftInHandMiddle=47,
    #     JointTag_LeftHandMiddle1=48,
    #     JointTag_LeftHandMiddle2=49,
    #     JointTag_LeftHandMiddle3=50,
    #     JointTag_LeftInHandRing=51,
    #     JointTag_LeftHandRing1=52,
    #     JointTag_LeftHandRing2=53,
    #     JointTag_LeftHandRing3=54,
    #     JointTag_LeftInHandPinky=55,
    #     JointTag_LeftHandPinky1=56,
    #     JointTag_LeftHandPinky2=57,
    #     JointTag_LeftHandPinky3=58,
    #     JointTag_Spine3=59,
    #     JointTag_JointsCount=60,
    # };