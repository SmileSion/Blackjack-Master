import socket

HOST = "127.0.0.1"  # 服务器 IP
PORT = 65432        # 服务器端口

# 连接服务器
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# 接收服务器欢迎消息
print(client.recv(1024).decode())

while True:
    msg = input("请输入指令（start/hit/stand）：").strip()
    if not msg:
        continue

    client.sendall(msg.encode())  # 发送消息
    response = client.recv(1024).decode()  # 接收服务器返回信息
    print(response)

    if "游戏结束" in response or "重新开始" in response:
        break  # 结束游戏

client.close()
