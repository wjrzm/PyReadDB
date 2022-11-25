import re
import socket
from threading import Thread

def MsgHandle(data):
    """
    消息处理
    """
    print(thread.name)
    # print(data.decode("utf-8"))
    # ret_data = "OK, starting..."
    # conn.send(ret_data.encode('utf-8'))

    # 按照不同的type对数据进行切片处理，进而得到相应的数据，接入到应用接口中
    print("ret:", data[:4])
    


if __name__ == '__main__':
    tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcpServer.bind(("172.27.143.68", 50001))
    tcpServer.bind(("127.0.0.1", 50001))
    tcpServer.listen(5)

    while True:
        conn, addr = tcpServer.accept()
        print(conn)
        while True:
            try:
                data = conn.recv(10240)
                if not data:
                    print("No found Data")
                    break
                thread = Thread(target=MsgHandle, args=(data,))
                # 设置成守护线程
                thread.setDaemon(True)
                thread.start()

            except Exception :
                print(Exception)
                break
        conn.close()
