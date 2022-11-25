import socket  # 导入 socket 模块

s = socket.socket()  # 创建 socket 对象
s.connect(('127.0.0.1', 50001))
while True:
    # print(s.recv(1024).decode(encoding='utf8'))
    s.send("".encode('utf8'))
    print(s.recv(1024).decode(encoding='utf8'))