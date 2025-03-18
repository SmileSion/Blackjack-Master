# config.py

# Redis 配置
REDIS_HOST = "192.168.3.225"
REDIS_PORT = 6379
REDIS_DB = 7

# 服务器配置
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 65432

# 游戏规则
DEALER_HIT_THRESHOLD = 17  # 庄家小于 17 点必须要牌

#使用的牌数
PILES = 6