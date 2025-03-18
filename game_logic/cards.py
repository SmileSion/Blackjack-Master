import random
import config



# 牌面点数
CARD_VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
               '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': [1, 11]}

# 牌面花色
SUITS = ['♠', '♥', '♦', '♣']

def get_deck():
    #生成牌堆
    deck = [f"{rank}{suit}" for rank in CARD_VALUES for suit in SUITS] * config.PILES
    random.shuffle(deck)
    return deck

def calculate_hand_value(hand):
    """计算手牌点数"""
    value = 0
    aces = 0
    
    for card in hand:
        rank = card[:-1]  # 提取牌面点数（去掉最后的花色字符）
        
        if rank == 'A':
            aces += 1
            value += 11
        else:
            value += CARD_VALUES[rank]
    
    # 如果点数超过 21，A 变为 1
    while value > 21 and aces:
        value -= 10
        aces -= 1
    
    return value