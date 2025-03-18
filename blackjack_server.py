import socket
import threading
import config
from game_logic.blackjack import start_game, hit_card, stand
from game_logic.funds import set_funds, set_bet, get_funds_info

def handle_client(conn, addr):
    """处理客户端连接"""
    print(f"玩家 {addr} 连接成功")
    conn.sendall("🎉 欢迎来到 21 点！🎉\n".encode("utf-8"))
    conn.sendall("请输入你的昵称：\n".encode("utf-8"))

    # 获取玩家昵称作为玩家 ID
    player_id = conn.recv(1024).decode().strip()
    
    if not player_id:
        player_id = str(addr)  # 如果玩家没有输入昵称，则使用 IP + 端口作为玩家 ID

    print(f"玩家 ID: {player_id}")

    # 获取起始资金
    conn.sendall("💰 请输入你的起始资金（伊甸币）：\n".encode("utf-8"))
    funds = int(conn.recv(1024).decode().strip())
    set_funds(player_id, funds)

    conn.sendall(f"👋 欢迎，{player_id}！\n" \
                 f"💰 你的起始资金为 {funds} 伊甸币。\n" \
                 f"🃏 游戏指令：\n" \
                 f"  - 输入 'start' 开始游戏\n" \
                 f"  - 输入 'funds' 查看资金\n" \
                 f"  - 输入 'exit' 退出游戏\n".encode("utf-8"))
    
    while True:
        try:
            data = conn.recv(1024).decode().strip().lower()
            if not data:
                break

            if data == "start":
                # 获取下注金额
                conn.sendall("💰 请输入你的下注金额（伊甸币）：\n".encode("utf-8"))
                bet = int(conn.recv(1024).decode().strip())
                set_bet(player_id, bet)
                response = start_game(player_id)
            elif data == "hit":
                response = hit_card(player_id)
            elif data == "stand":
                response = stand(player_id)
            elif data == "funds":
                response = get_funds_info(player_id)
            elif data == "exit":  # 添加处理 exit 输入
                response = "👋 你已退出游戏。感谢你的参与！"
                conn.sendall(response.encode() + b"\n")
                break  # 退出循环，关闭连接
            else:
                response = "❌ 无效指令，请输入以下指令之一：\n" \
                           "  - 'start'：开始游戏\n" \
                           "  - 'hit'：要牌\n" \
                           "  - 'stand'：停牌\n" \
                           "  - 'funds'：查看资金\n" \
                           "  - 'exit'：退出游戏"

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
    print(f"服务器启动，监听 {host}:{config.SERVER_PORT}...")

    while True:
        conn, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    main()
