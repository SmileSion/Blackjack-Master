from storage.redis_db import redis_client

def set_funds(player_id, amount):
    """设置玩家的资金"""
    redis_client.hset(player_id, "funds", amount)

def get_funds(player_id):
    """获取玩家的资金"""
    return int(redis_client.hget(player_id, "funds") or 0)

def add_funds(player_id, amount):
    """增加玩家的资金"""
    current_funds = get_funds(player_id)
    set_funds(player_id, current_funds + amount)

def deduct_funds(player_id, amount):
    """扣除玩家的资金"""
    current_funds = get_funds(player_id)
    set_funds(player_id, current_funds - amount)

def set_bet(player_id, amount):
    """设置玩家的下注金额"""
    redis_client.hset(player_id, "bet", amount)

def get_bet(player_id):
    """获取玩家的下注金额"""
    return int(redis_client.hget(player_id, "bet") or 0)

def get_funds_info(player_id):
    """查询玩家的资金并返回信息"""
    funds = get_funds(player_id)
    return f"💰 你的当前资金为：{funds} 伊甸币。"
