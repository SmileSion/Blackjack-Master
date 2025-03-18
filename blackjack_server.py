import socket
import threading
import config
from game_logic.blackjack import start_game, hit_card, stand

def handle_client(conn, addr):
    """处理客户端连接"""
    print(f"玩家 {addr} 连接成功")
    conn.sendall("欢迎来到 21 点！输入 'start' 开始游戏。\n输入 'exit' 退出游戏。\n".encode("utf-8"))

    player_id = str(addr)  # 使用 IP + 端口作为玩家 ID
    while True:
        try:
            data = conn.recv(1024).decode().strip().lower()
            if not data:
                break

            if data == "start":
                response = start_game(player_id)
            elif data == "hit":
                response = hit_card(player_id)
            elif data == "stand":
                response = stand(player_id)
            elif data == "exit":  # 添加处理 exit 输入
                response = "👋 你已退出游戏。感谢你的参与！"
                conn.sendall(response.encode() + b"\n")
                break  # 退出循环，关闭连接
            else:
                response = "❓ 无效指令，请输入 'start' / 'hit' / 'stand'。"

            conn.sendall(response.encode() + b"\n")
        except ConnectionResetError:
            print(f"玩家 {addr} 连接被重置")
            break
        except Exception as e:
            print(f"错误: {e}")
            break

    print(f"玩家 {addr} 断开连接")
    conn.close()

def main():
    """启动服务器"""
    host = "0.0.0.0"
    port = 65432

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((config.SERVER_HOST, config.SERVER_PORT))
    server.listen(5)
    print(f"服务器启动，监听 {host}:{port}...")

    while True:
        conn, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    main()
