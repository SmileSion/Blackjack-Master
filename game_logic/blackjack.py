import json
import config
from storage.redis_db import redis_client
from game_logic.cards import get_deck, calculate_hand_value
from game_logic.funds import get_funds, deduct_funds, add_funds, set_bet, get_bet

# 分隔线
separator = config.separator

def start_game(player_id):
    """初始化游戏"""
    # 获取玩家的资金
    funds = get_funds(player_id)
    if funds <= 0:
        return f"{separator}⚠️ 你的资金不足，无法继续游戏。请重新输入起始资金。{separator}"

    # 获取下注金额
    bet = get_bet(player_id)
    if bet <= 0 or bet > funds:
        return f"{separator}⚠️ 下注金额无效，请重新下注。{separator}"

    # 扣除下注金额
    deduct_funds(player_id, bet)

    deck = get_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    
    player_score = calculate_hand_value(player_hand)
    dealer_score = calculate_hand_value(dealer_hand)
    
    # 检测玩家和庄家是否同时 Blackjack
    if player_score == 21 and dealer_score == 21:
        redis_client.hset(player_id, "game_over", "True")
        # add_funds(player_id, bet)  # 退还下注金额
        return f"{separator}😐 平局！你和庄家都拿到了 Blackjack！\n" \
               f"你的手牌: {', '.join(player_hand)}（21 点）\n" \
               f"庄家的手牌: {', '.join(dealer_hand)}（21 点）\n" \
               f"💰 当前资金: {get_funds(player_id)} 伊甸币{separator}"

    # 检测玩家 Blackjack
    if player_score == 21:
        redis_client.hset(player_id, "game_over", "True")
        add_funds(player_id, int(bet * 2.5))  # Blackjack 1.5倍赔付
        return f"{separator}🎉 恭喜！你拿到了 Blackjack！\n" \
               f"你的手牌: {', '.join(player_hand)}（21 点）\n" \
               f"💰 当前资金: {get_funds(player_id)} 伊甸币{separator}"

    # 检测庄家 Blackjack
    if dealer_score == 21:
        redis_client.hset(player_id, "game_over", "True")
        return f"{separator}😢 庄家拿到了 Blackjack！\n" \
               f"你的手牌: {', '.join(player_hand)}（{player_score} 点）\n" \
               f"庄家的手牌: {', '.join(dealer_hand)}（21 点）\n" \
               f"💰 当前资金: {get_funds(player_id)} 伊甸币{separator}"

    game_data = {
        "deck": json.dumps(deck),
        "player_hand": json.dumps(player_hand),
        "dealer_hand": json.dumps(dealer_hand),
        "game_over": "False"  # 确保存储的是字符串
    }
    redis_client.hset(player_id, mapping=game_data)

    return f"{separator}🎰 你拿到的牌: {', '.join(player_hand)}（{calculate_hand_value(player_hand)} 点）\n" \
           f"🃏 庄家的明牌: {dealer_hand[0]}\n" \
           f"💰 当前资金: {get_funds(player_id)} 伊甸币{separator}" \
           f"输入 'hit'（要牌） 或 'stand'（停牌）。\n" \
           f"输入 'funds' 查看资金。"

def hit_card(player_id):
    """玩家要牌"""
    game_data = redis_client.hgetall(player_id)
    if not game_data or game_data.get("game_over") == b"True":  # 注意：Redis 返回值是字节类型，比较时要转换为字节
        return f"{separator}⚠️ 你还没开始游戏！请输入 'start' 开始新一局。{separator}"

    deck = json.loads(game_data["deck"])
    player_hand = json.loads(game_data["player_hand"])

    player_hand.append(deck.pop())
    player_score = calculate_hand_value(player_hand)

    redis_client.hset(player_id, "player_hand", json.dumps(player_hand))
    redis_client.hset(player_id, "deck", json.dumps(deck))

    if player_score > 21:
        redis_client.hset(player_id, "game_over", "True")  # 存储 "True" 字符串
        return f"{separator}😵 你爆牌了！\n" \
               f"你的手牌: {', '.join(player_hand)}（{player_score} 点）\n" \
               f"💰 当前资金: {get_funds(player_id)} 伊甸币{separator}" \
               f"输入 'start' 重新开始游戏。\n" \
               f"输入 'funds' 查看资金。"

    return f"{separator}🃏 你拿到了 {', '.join(player_hand)}（{player_score} 点）\n" \
           f"💰 当前资金: {get_funds(player_id)} 伊甸币{separator}" \
           f"输入 'hit'（要牌） 或 'stand'（停牌）。\n" \
           f"输入 'funds' 查看资金。"

def stand(player_id):
    """玩家停牌，庄家操作"""
    game_data = redis_client.hgetall(player_id)
    if not game_data or game_data.get("game_over") == b"True":  # 同样的，处理字节数据
        return f"{separator}⚠️ 你还没开始游戏！请输入 'start' 开始新一局。{separator}"

    player_hand = json.loads(game_data["player_hand"])
    dealer_hand = json.loads(game_data["dealer_hand"])
    deck = json.loads(game_data["deck"])

    player_score = calculate_hand_value(player_hand)
    dealer_score = calculate_hand_value(dealer_hand)

    while dealer_score < 17:
        dealer_hand.append(deck.pop())
        dealer_score = calculate_hand_value(dealer_hand)

    redis_client.hset(player_id, "dealer_hand", json.dumps(dealer_hand))
    redis_client.hset(player_id, "game_over", "True")  # 存储 "True" 字符串

    bet = get_bet(player_id)
    funds = get_funds(player_id)

    if dealer_score > 21 or player_score > dealer_score:
        result = "🎉 你赢了！"
        add_funds(player_id, bet * 2)  # 赔付
    elif player_score < dealer_score:
        result = "😢 庄家赢了！"
    else:
        result = "😐 平局！"
        add_funds(player_id, bet)  # 退还下注金额

    return f"{separator}🃏 你的手牌: {', '.join(player_hand)}（{player_score} 点）\n" \
           f"🏦 庄家的手牌: {', '.join(dealer_hand)}（{dealer_score} 点）\n" \
           f"{result}\n" \
           f"💰 当前资金: {get_funds(player_id)} 伊甸币{separator}" \
           f"输入 'start' 重新开始游戏。\n" \
           f"输入 'funds' 查看资金。"
