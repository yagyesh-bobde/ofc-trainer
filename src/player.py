from deuces import Card
from .utils import FRONT, MIDDLE, BACK, STREET_SIZES, print_card

class Player:
    """Base player class for OFC Poker"""
    
    def __init__(self, player_id):
        self.player_id = player_id
        self.board = {
            FRONT: [],
            MIDDLE: [],
            BACK: []
        }
        self.hand = []
    
    def receive_cards(self, cards):
        """
        Add cards to player's hand
        
        Args:
            cards: List of card integers in deuces format
        """
        self.hand.extend(cards)
    
    def place_card(self, card, street):
        """
        Place a card on a specific street
        
        Args:
            card: Card integer in deuces format
            street: Street name (front, middle, back)
            
        Returns:
            Boolean indicating if the placement was successful
        """
        if card not in self.hand:
            print(f"Error: Card {print_card(card)} not in hand")
            return False
        
        if street not in self.board:
            print(f"Error: Invalid street {street}")
            return False
        
        if len(self.board[street]) >= STREET_SIZES[street]:
            print(f"Error: Street {street} is full")
            return False
        
        # Place the card
        self.board[street].append(card)
        self.hand.remove(card)
        return True
    
    def get_legal_moves(self):
        """
        Get all legal moves (street placements) for the current hand
        
        Returns:
            List of legal street names where cards can be placed
        """
        legal_moves = []
        
        for street in [FRONT, MIDDLE, BACK]:
            if len(self.board[street]) < STREET_SIZES[street]:
                legal_moves.append(street)
        
        return legal_moves
    
    def select_move(self, card=None):
        """
        Select a move (street) for the current card
        This should be overridden by subclasses
        
        Args:
            card: The card to place (if None, use the first card in hand)
            
        Returns:
            Street name or None if no legal moves
        """
        raise NotImplementedError("Subclasses must implement select_move")
    
    def is_board_complete(self):
        """
        Check if the player's board is complete
        
        Returns:
            Boolean indicating if the board is complete
        """
        return (len(self.board[FRONT]) == STREET_SIZES[FRONT] and
                len(self.board[MIDDLE]) == STREET_SIZES[MIDDLE] and
                len(self.board[BACK]) == STREET_SIZES[BACK])
    
    def reset(self):
        """Reset the player's board and hand"""
        self.board = {
            FRONT: [],
            MIDDLE: [],
            BACK: []
        }
        self.hand = []
    
    def select_pineapple_moves(self, cards):
        """
        Select 2 cards to place and 1 to discard from the 3 dealt Pineapple cards.
        Should be overridden by subclasses.
        Args:
            cards: List of 3 card ints
        Returns:
            (place_cards, discard_card): tuple (list of 2, single card)
        """
        raise NotImplementedError("Subclasses must implement select_pineapple_moves")
    
    def select_initial_placements(self, cards):
        """
        Assign each of the 5 initial cards to a row. Should be overridden by subclasses.
        Args:
            cards: List of 5 card ints
        Returns:
            placements: List of (card, street) tuples
        """
        raise NotImplementedError("Subclasses must implement select_initial_placements")


class RandomPlayer(Player):
    """Player that makes random legal moves"""
    
    def select_move(self, card=None):
        """
        Select a random legal move
        
        Args:
            card: The card to place (if None, use the first card in hand)
            
        Returns:
            Street name or None if no legal moves
        """
        import random
        
        if not self.hand:
            return None
        
        if card is None:
            card = self.hand[0]
        
        legal_moves = self.get_legal_moves()
        if not legal_moves:
            return None
        
        return random.choice(legal_moves)
    
    def select_pineapple_moves(self, cards):
        import random
        chosen = random.sample(cards, 2)
        discard = [c for c in cards if c not in chosen][0]
        return chosen, discard
    
    def select_initial_placements(self, cards):
        import random
        placements = []
        available = cards[:]
        for card in available:
            legal = self.get_legal_moves()
            street = random.choice(legal)
            placements.append((card, street))
            self.place_card(card, street)
        return placements


class HumanPlayer(Player):
    """Human player that takes input from console"""
    
    def select_move(self, card=None):
        """
        Ask for human input to select a move
        
        Args:
            card: The card to place (if None, use the first card in hand)
            
        Returns:
            Street name or None if no legal moves
        """
        from .utils import print_card, print_board
        
        if not self.hand:
            return None
        
        if card is None:
            card = self.hand[0]
        
        legal_moves = self.get_legal_moves()
        if not legal_moves:
            return None
        
        # Show current board
        print("\nYour current board:")
        print(print_board(self.board))
        
        # Show current card
        print(f"\nCurrent card: {print_card(card)}")
        
        # Present legal moves
        print("\nLegal moves:")
        for i, move in enumerate(legal_moves):
            print(f"{i+1}. {move}")
        
        # Get player input
        valid_input = False
        selected_move = None
        
        while not valid_input:
            choice = input("\nEnter your choice (number): ")
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(legal_moves):
                    selected_move = legal_moves[choice_idx]
                    valid_input = True
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        return selected_move
    
    def select_pineapple_moves(self, cards):
        from .utils import print_card, print_board
        print("\nYour current board:")
        print(print_board(self.board))
        print("\nYou have been dealt:")
        for i, card in enumerate(cards):
            print(f"{i+1}. {print_card(card)}")
        # Ask user to pick 2 to place
        while True:
            try:
                picks = input("Enter the numbers of the 2 cards to PLACE (e.g. 1 3): ").split()
                if len(picks) != 2:
                    print("Please enter exactly 2 numbers.")
                    continue
                idx1, idx2 = int(picks[0])-1, int(picks[1])-1
                if idx1 == idx2 or not (0 <= idx1 < 3) or not (0 <= idx2 < 3):
                    print("Invalid selection. Try again.")
                    continue
                place_cards = [cards[idx1], cards[idx2]]
                discard = [c for c in cards if c not in place_cards][0]
                return place_cards, discard
            except Exception:
                print("Invalid input. Try again.")
    
    def select_initial_placements(self, cards):
        from .utils import print_card, print_board
        available = cards[:]
        placements = []
        for i in range(5):
            print("\nYour current board:")
            print(print_board(self.board))
            print("\nYour initial cards:")
            for idx, card in enumerate(available):
                print(f"{idx+1}. {print_card(card)}")
            while True:
                try:
                    pick = int(input(f"Select card #{i+1} to place (1-{len(available)}): ")) - 1
                    if not (0 <= pick < len(available)):
                        print("Invalid card selection.")
                        continue
                    card = available[pick]
                    legal = self.get_legal_moves()
                    print("Legal rows:")
                    for j, street in enumerate(legal):
                        print(f"{j+1}. {street}")
                    row_pick = int(input(f"Select row for {print_card(card)}: ")) - 1
                    if not (0 <= row_pick < len(legal)):
                        print("Invalid row selection.")
                        continue
                    street = legal[row_pick]
                    placements.append((card, street))
                    self.place_card(card, street)
                    available.pop(pick)
                    break
                except Exception:
                    print("Invalid input. Try again.")
        return placements


class GreedyPlayer(Player):
    """
    Player that uses a greedy starting hand strategy, as described in the paper
    For the first 5 cards, it tries to place strong poker hands in the back
    """
    
    def _is_same_suit(self, cards):
        """Check if cards are all the same suit"""
        if not cards:
            return False
        
        suits = [Card.get_suit_int(card) for card in cards]
        return all(suit == suits[0] for suit in suits)
    
    def _is_sequential(self, cards):
        """Check if cards are sequential in rank"""
        if not cards:
            return False
        
        ranks = sorted([Card.get_rank_int(card) for card in cards])
        for i in range(1, len(ranks)):
            if ranks[i] != ranks[i-1] + 1:
                return False
        
        return True
    
    def _count_ranks(self, cards):
        """Count occurrences of each rank"""
        rank_counts = {}
        for card in cards:
            rank = Card.get_rank_int(card)
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        return rank_counts
    
    def _find_strong_hand(self, cards):
        """
        Find the strongest hand pattern in the cards
        Returns a tuple of (pattern, cards_in_pattern)
        """
        rank_counts = self._count_ranks(cards)
        
        # Check for four of a kind
        for rank, count in rank_counts.items():
            if count == 4:
                quads = [card for card in cards if Card.get_rank_int(card) == rank]
                return "four_of_a_kind", quads
        
        # Check for full house
        three_kind = None
        pair = None
        
        for rank, count in rank_counts.items():
            if count == 3 and three_kind is None:
                three_kind = rank
            elif count >= 2 and pair is None:
                pair = rank
        
        if three_kind is not None and pair is not None:
            trips = [card for card in cards if Card.get_rank_int(card) == three_kind]
            pair_cards = [card for card in cards if Card.get_rank_int(card) == pair][:2]
            return "full_house", trips + pair_cards
        
        # Check for flush
        if self._is_same_suit(cards) and len(cards) >= 5:
            return "flush", cards[:5]
        
        # Check for straight
        if self._is_sequential(cards) and len(cards) >= 5:
            sorted_cards = sorted(cards, key=lambda c: Card.get_rank_int(c))
            return "straight", sorted_cards[:5]
        
        # Check for 4 cards of the same suit
        suits = {}
        for card in cards:
            suit = Card.get_suit_int(card)
            suits[suit] = suits.get(suit, []) + [card]
        
        for suit, suited_cards in suits.items():
            if len(suited_cards) >= 4:
                return "four_flush", suited_cards[:4]
        
        # Check for two pair
        pairs = []
        for rank, count in rank_counts.items():
            if count >= 2:
                pair_cards = [card for card in cards if Card.get_rank_int(card) == rank][:2]
                pairs.extend(pair_cards)
                if len(pairs) >= 4:
                    return "two_pair", pairs[:4]
        
        # Check for three of a kind
        for rank, count in rank_counts.items():
            if count == 3:
                trips = [card for card in cards if Card.get_rank_int(card) == rank]
                return "three_of_a_kind", trips
        
        # Check for 4 cards of sequential rank
        sorted_by_rank = sorted(cards, key=lambda c: Card.get_rank_int(c))
        for i in range(len(sorted_by_rank) - 3):
            subset = sorted_by_rank[i:i+4]
            if self._is_sequential(subset):
                return "four_straight", subset
        
        # Check for 3 cards of the same suit
        for suit, suited_cards in suits.items():
            if len(suited_cards) >= 3:
                return "three_flush", suited_cards[:3]
        
        # Check for 3 cards of sequential rank
        for i in range(len(sorted_by_rank) - 2):
            subset = sorted_by_rank[i:i+3]
            if self._is_sequential(subset):
                return "three_straight", subset
        
        # If no pattern is found, return the high cards
        sorted_by_rank = sorted(cards, key=lambda c: Card.get_rank_int(c), reverse=True)
        return "high_cards", sorted_by_rank
    
    def _first_five_strategy(self, cards):
        """
        Strategy for placing the first 5 cards
        
        Args:
            cards: List of 5 cards
            
        Returns:
            Dictionary mapping streets to lists of cards to place
        """
        # Find the strongest pattern in the cards
        pattern, pattern_cards = self._find_strong_hand(cards)
        
        # Set of cards not in the pattern
        remaining_cards = [card for card in cards if card not in pattern_cards]
        
        # Default placement - high cards in back, mid in middle, low in front
        sorted_cards = sorted(cards, key=lambda c: Card.get_rank_int(c), reverse=True)
        
        placement = {
            BACK: [],
            MIDDLE: [],
            FRONT: []
        }
        
        # Place strong patterns in the back
        if pattern in ["four_of_a_kind", "full_house", "flush", "straight"]:
            placement[BACK] = pattern_cards
            remaining_cards = [card for card in cards if card not in pattern_cards]
            
            # Sort remaining cards by rank
            remaining_cards.sort(key=lambda c: Card.get_rank_int(c), reverse=True)
            
            # Place high cards in middle, low cards in front
            middle_count = min(len(remaining_cards), 2)
            placement[MIDDLE] = remaining_cards[:middle_count]
            placement[FRONT] = remaining_cards[middle_count:]
            
        # Place medium patterns in the middle
        elif pattern in ["four_flush", "two_pair", "three_of_a_kind", "four_straight"]:
            placement[MIDDLE] = pattern_cards
            remaining_cards = [card for card in cards if card not in pattern_cards]
            
                            # Put highest remaining card in back
            if remaining_cards:
                high_card = max(remaining_cards, key=lambda c: Card.get_rank_int(c))
                placement[BACK] = [high_card]
                remaining_cards.remove(high_card)
                
                # Put any remaining cards in front
                placement[FRONT] = remaining_cards
            
        # Place small patterns in front, distribute remaining cards
        elif pattern in ["three_flush", "three_straight"]:
            placement[FRONT] = pattern_cards
            remaining_cards = [card for card in cards if card not in pattern_cards]
            
            # Sort remaining cards by rank
            remaining_cards.sort(key=lambda c: Card.get_rank_int(c), reverse=True)
            
            # Put highest cards in back, rest in middle
            placement[BACK] = remaining_cards[:2]
            placement[MIDDLE] = remaining_cards[2:]
            
        # Default strategy - distribute by card rank
        else:
            # Sort cards by rank (highest first)
            sorted_cards = sorted(cards, key=lambda c: Card.get_rank_int(c), reverse=True)
            
            # Back gets the highest two cards
            placement[BACK] = sorted_cards[:2]
            
            # Middle gets the next highest two cards
            placement[MIDDLE] = sorted_cards[2:4]
            
            # Front gets the lowest card
            placement[FRONT] = sorted_cards[4:]
        
        return placement
    
    def select_move(self, card=None):
        """
        Select a move based on greedy strategy
        
        Args:
            card: The card to place (if None, use the first card in hand)
            
        Returns:
            Street name or None if no legal moves
        """
        import random
        
        if not self.hand:
            return None
        
        if card is None:
            card = self.hand[0]
        
        legal_moves = self.get_legal_moves()
        if not legal_moves:
            return None
        
        # First turn with 5 cards - use special strategy
        if len(self.hand) == 5 and sum(len(self.board[street]) for street in self.board) == 0:
            placement = self._first_five_strategy(self.hand)
            
            # Find the first street with cards assigned to it
            for street in [FRONT, MIDDLE, BACK]:
                if street in legal_moves and placement[street]:
                    return street
        
        # For subsequent cards, place according to rank
        card_rank = Card.get_rank_int(card)
        
        # High cards (J, Q, K, A) go to back if possible
        if card_rank >= 9 and BACK in legal_moves:  # Jack or higher
            return BACK
        
        # Medium cards (8, 9, 10) go to middle if possible
        if card_rank >= 6 and MIDDLE in legal_moves:
            return MIDDLE
        
        # Low cards go to front if possible
        if FRONT in legal_moves:
            return FRONT
        
        # If preferred street is full, choose the next best option
        if BACK in legal_moves:
            return BACK
        elif MIDDLE in legal_moves:
            return MIDDLE
        else:
            return FRONT
    
    def select_pineapple_moves(self, cards):
        # Greedy: pick the 2 highest rank cards to place
        cards_sorted = sorted(cards, key=lambda c: Card.get_rank_int(c), reverse=True)
        return cards_sorted[:2], cards_sorted[2]
    
    def select_initial_placements(self, cards):
        # Use greedy logic: try to place strong hands in back, etc.
        placements = []
        placement_plan = self._first_five_strategy(cards)
        used = set()
        for street in [BACK, MIDDLE, FRONT]:
            for card in placement_plan[street]:
                if card not in used:
                    placements.append((card, street))
                    self.place_card(card, street)
                    used.add(card)
        # If any cards left, just place them in legal rows
        for card in cards:
            if card not in used:
                legal = self.get_legal_moves()
                street = legal[0]
                placements.append((card, street))
                self.place_card(card, street)
                used.add(card)
        return placements