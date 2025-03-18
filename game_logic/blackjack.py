import json
from storage.redis_db import redis_client
from game_logic.cards import get_deck, calculate_hand_value

def start_game(player_id):
    """初始化游戏"""
    deck = get_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    game_data = {
        "deck": json.dumps(deck),
        "player_hand": json.dumps(player_hand),
        "dealer_hand": json.dumps(dealer_hand),
        "game_over": False
    }
    redis_client.hmset(player_id, game_data)

    return f"🎰 你拿到的牌: {player_hand}（{calculate_hand_value(player_hand)} 点）\n" \
           f"🃏 庄家的明牌: {dealer_hand[0]}\n输入 'hit'（要牌） 或 'stand'（停牌）。"

def hit_card(player_id):
    """玩家要牌"""
    game_data = redis_client.hgetall(player_id)
    if not game_data or game_data.get("game_over") == "True":
        return "⚠️ 你还没开始游戏！请输入 'start' 开始新一局。"

    deck = json.loads(game_data["deck"])
    player_hand = json.loads(game_data["player_hand"])

    player_hand.append(deck.pop())
    player_score = calculate_hand_value(player_hand)

    redis_client.hset(player_id, "player_hand", json.dumps(player_hand))
    redis_client.hset(player_id, "deck", json.dumps(deck))

    if player_score > 21:
        redis_client.hset(player_id, "game_over", "True")
        return f"😵 你爆牌了！\n你的手牌: {player_hand}（{player_score} 点）\n输入 'start' 重新开始游戏。"

    return f"🃏 你拿到了 {player_hand}（{player_score} 点）\n输入 'hit'（要牌） 或 'stand'（停牌）。"

def stand(player_id):
    """玩家停牌，庄家操作"""
    game_data = redis_client.hgetall(player_id)
    if not game_data or game_data.get("game_over") == "True":
        return "⚠️ 你还没开始游戏！请输入 'start' 开始新一局。"

    player_hand = json.loads(game_data["player_hand"])
    dealer_hand = json.loads(game_data["dealer_hand"])
    deck = json.loads(game_data["deck"])

    player_score = calculate_hand_value(player_hand)
    dealer_score = calculate_hand_value(dealer_hand)

    while dealer_score < 17:
        dealer_hand.append(deck.pop())
        dealer_score = calculate_hand_value(dealer_hand)

    redis_client.hset(player_id, "dealer_hand", json.dumps(dealer_hand))
    redis_client.hset(player_id, "game_over", "True")

    if dealer_score > 21 or player_score > dealer_score:
        result = "🎉 你赢了！"
    elif player_score < dealer_score:
        result = "😢 庄家赢了！"
    else:
        result = "😐 平局！"

    return f"🃏 你的手牌: {player_hand}（{player_score} 点）\n" \
           f"🏦 庄家的手牌: {dealer_hand}（{dealer_score} 点）\n{result}\n输入 'start' 重新开始游戏。"
