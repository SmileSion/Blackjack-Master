import random

#使用的牌数
PILES = 6

# 牌面点数
CARD_VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
               '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': [1, 11]}

def get_deck():
    #生成牌堆
    deck = [rank for rank in CARD_VALUES] * 4 * PILES
    random.shuffle(deck)
    return deck

def calculate_hand_value(hand):
    value = 0
    aces = 0
    for card in hand:
        if card == 'A':
            aces += 1
            value += 11
        else:
            value += CARD_VALUES[card]
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value