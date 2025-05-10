from deuces import Card
from colorama import Fore, Style, init

# Initialize colorama
init()

# Card suit color mapping
SUIT_COLORS = {
    'h': Fore.RED,    # hearts
    'd': Fore.RED,    # diamonds
    's': Fore.WHITE,  # spades
    'c': Fore.WHITE,  # clubs
}

RESET_COLOR = Style.RESET_ALL

# Street names
FRONT = 'front'
MIDDLE = 'middle'
BACK = 'back'

STREET_SIZES = {
    FRONT: 3,
    MIDDLE: 5,
    BACK: 5
}

# Royalty points based on hand strength for each street
ROYALTIES = {
    FRONT: {
        "Pair of 6s": 1,
        "Pair of 7s": 2,
        "Pair of 8s": 3,
        "Pair of 9s": 4,
        "Pair of 10s": 5,
        "Pair of Js": 6,
        "Pair of Qs": 7,
        "Pair of Ks": 8,
        "Pair of As": 9,
        "Three of a Kind, 2s": 10,
        "Three of a Kind, 3s": 11,
        "Three of a Kind, 4s": 12,
        "Three of a Kind, 5s": 13,
        "Three of a Kind, 6s": 14,
        "Three of a Kind, 7s": 15,
        "Three of a Kind, 8s": 16,
        "Three of a Kind, 9s": 17,
        "Three of a Kind, 10s": 18,
        "Three of a Kind, Js": 19,
        "Three of a Kind, Qs": 20,
        "Three of a Kind, Ks": 21,
        "Three of a Kind, As": 22
    },
    MIDDLE: {
        "Three of a Kind": 2,
        "Straight": 4,
        "Flush": 8,
        "Full House": 12,
        "Four of a Kind": 20,
        "Straight Flush": 30,
        "Royal Flush": 50
    },
    BACK: {
        "Three of a Kind": 2,
        "Straight": 4,
        "Flush": 8,
        "Full House": 12,
        "Four of a Kind": 20,
        "Straight Flush": 30,
        "Royal Flush": 50
    }
}

JOKER_1 = 53
JOKER_2 = 54

def print_card(card):
    """Print a single card with color based on suit"""
    if card == 0:  # Empty slot
        return "[ ]"
    if card == JOKER_1 or card == JOKER_2:
        return f"{Fore.YELLOW}[JK]{RESET_COLOR}"
    card_str = Card.int_to_str(card)
    rank, suit = card_str[0], card_str[1]
    color = SUIT_COLORS.get(suit, '')
    return f"{color}[{rank}{suit}]{RESET_COLOR}"

def print_cards(cards):
    """Print a list of cards side by side"""
    return ' '.join(print_card(card) for card in cards)

def print_board(board):
    """Print a player's board in a readable format"""
    front = board.get(FRONT, [0, 0, 0])
    middle = board.get(MIDDLE, [0, 0, 0, 0, 0])
    back = board.get(BACK, [0, 0, 0, 0, 0])
    
    # Pad arrays with zeros if they're not full length
    front = front + [0] * (3 - len(front))
    middle = middle + [0] * (5 - len(middle))
    back = back + [0] * (5 - len(back))
    
    output = [
        f"Front:  {print_cards(front)}",
        f"Middle: {print_cards(middle)}",
        f"Back:   {print_cards(back)}"
    ]
    
    return '\n'.join(output)

def get_hand_category(hand_rank, num_cards):
    """
    Convert a deuces hand rank to a category name for royalty calculation
    
    Args:
        hand_rank: Integer hand rank from deuces evaluator
        num_cards: Number of cards in the hand
    
    Returns:
        String hand category or None if not a special hand
    """
    from deuces import Evaluator
    
    if num_cards < 3:
        return None
    
    # These are ordered from worst to best in deuces
    categories = [
        "High Card", 
        "Pair", 
        "Two Pair", 
        "Three of a Kind", 
        "Straight", 
        "Flush", 
        "Full House", 
        "Four of a Kind", 
        "Straight Flush",
    ]
    
    # Deuces evaluator gives lower numbers to better hands
    # 7462 is the worst possible high card hand
    rank_class = 7462 - hand_rank
    
    if rank_class <= 0:
        return None
    
    # Scale the rank to get the category index
    category_index = min(int(rank_class / 7462 * len(categories)), len(categories) - 1)
    category = categories[category_index]
    
    # Special case for Royal Flush
    if category == "Straight Flush" and is_royal_flush(hand_rank):
        return "Royal Flush"
    
    return category

def is_royal_flush(hand_rank):
    """Check if a hand rank is a royal flush"""
    # In deuces, the best hand (Royal Flush) has a rank of 1
    return hand_rank == 1

def html_card(card):
    """Return an HTML string for a visually appealing card for Streamlit UI."""
    if card == 0:
        return '<span style="display:inline-block;border:1px solid #888;padding:8px 12px;margin:2px;background:#eee;font-size:1.5em;">[ ]</span>'
    if card == JOKER_1 or card == JOKER_2:
        return '<span style="display:inline-block;border:2px solid gold;padding:8px 12px;margin:2px;background:yellow;font-size:1.5em;font-weight:bold;">🃏</span>'
    card_str = Card.int_to_str(card)
    rank, suit = card_str[0], card_str[1]
    suit_map = {'h': '♥', 'd': '♦', 's': '♠', 'c': '♣'}
    color = 'red' if suit in 'hd' else 'black'
    return f'<span style="display:inline-block;border:1px solid #888;padding:8px 12px;margin:2px;background:#fff;font-size:1.5em;color:{color};">{rank}{suit_map[suit]}</span>'

def html_cards(cards):
    return ''.join([html_card(card) for card in cards])