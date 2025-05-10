from deuces import Evaluator, Card
from .utils import FRONT, MIDDLE, BACK, ROYALTIES, get_hand_category, JOKER_1, JOKER_2
import itertools

class OFCEvaluator:
    """
    Evaluator for Open-face Chinese Poker hands and scoring
    Uses deuces library for hand evaluation
    """
    
    def __init__(self):
        self.evaluator = Evaluator()
    
    def evaluate_street(self, cards):
        """
        Evaluate a street of cards using deuces, handling jokers as wildcards
        Args:
            cards: List of card integers in deuces format (may include jokers)
        Returns:
            Integer hand rank (lower is better)
        """
        # Filter out any zeros (empty slots)
        valid_cards = [card for card in cards if card != 0]
        num_jokers = valid_cards.count(JOKER_1) + valid_cards.count(JOKER_2)
        non_joker_cards = [card for card in valid_cards if card != JOKER_1 and card != JOKER_2]
        
        # If less than 3 cards, return worst possible rank
        if len(valid_cards) < 3:
            return 7462  # Worst possible hand in deuces
        
        # Deuces evaluator expects exactly 5 or 7 cards
        # For front street (3 cards), pad with dummy cards
        if len(valid_cards) == 3:
            # Add two dummy cards that don't affect the hand
            dummy_cards = [
                Card.new('Ah'),  # Ace of hearts
                Card.new('Kh'),  # King of hearts
            ]
            non_joker_cards = non_joker_cards + dummy_cards
        
        # If no jokers, evaluate normally
        if num_jokers == 0:
            return self.evaluator.evaluate(non_joker_cards, [])
        
        # Generate all possible substitutions for jokers
        all_ranks = '23456789TJQKA'
        all_suits = 'shdc'
        all_cards = set(Card.new(rank + suit) for rank in all_ranks for suit in all_suits)
        used_cards = set(non_joker_cards)
        available_cards = list(all_cards - used_cards)
        
        best_rank = 7462
        if num_jokers == 1:
            for sub in available_cards:
                test_hand = non_joker_cards + [sub]
                rank = self.evaluator.evaluate(test_hand, [])
                if rank < best_rank:
                    best_rank = rank
        elif num_jokers == 2:
            for sub1, sub2 in itertools.combinations(available_cards, 2):
                test_hand = non_joker_cards + [sub1, sub2]
                rank = self.evaluator.evaluate(test_hand, [])
                if rank < best_rank:
                    best_rank = rank
        return best_rank
    
    def is_valid_board(self, board):
        """
        Check if a board is valid (back >= middle >= front)
        
        Args:
            board: Dictionary of street names to lists of cards
            
        Returns:
            Boolean indicating if the board is valid
        """
        # Only check if all streets are filled
        if (len(board.get(FRONT, [])) != 3 or
            len(board.get(MIDDLE, [])) != 5 or
            len(board.get(BACK, [])) != 5):
            return True
        
        front_rank = self.evaluate_street(board.get(FRONT, []))
        middle_rank = self.evaluate_street(board.get(MIDDLE, []))
        back_rank = self.evaluate_street(board.get(BACK, []))
        
        # Lower ranks are better in deuces
        return back_rank <= middle_rank <= front_rank
    
    def is_top_row_straight_or_flush(self, cards):
        """Return True if the 3-card top row is a straight or flush (even with jokers)"""
        from deuces import Card
        # Remove jokers for suit/rank check
        real_cards = [card for card in cards if card != JOKER_1 and card != JOKER_2]
        if len(real_cards) < 2:
            return False
        # Check flush
        suits = [Card.get_suit_int(card) for card in real_cards]
        if len(set(suits)) == 1 and len(real_cards) == 3:
            return True
        # Check straight (with jokers, brute force)
        ranks = [Card.get_rank_int(card) for card in real_cards]
        for missing in range(13):
            test_ranks = ranks + [missing] * (3 - len(ranks))
            test_ranks = sorted(set(test_ranks))
            if len(test_ranks) == 3 and max(test_ranks) - min(test_ranks) == 2:
                return True
        return False

    def get_royalties(self, board):
        """
        Calculate royalties for a board
        
        Args:
            board: Dictionary of street names to lists of cards
            
        Returns:
            Dictionary of street names to royalty points
        """
        # Initialize royalties
        royalty_points = {
            FRONT: 0,
            MIDDLE: 0,
            BACK: 0
        }
        
        # Check if board is valid
        if not self.is_valid_board(board):
            return royalty_points
        
        # Calculate front street royalties (special handling for pairs and trips)
        front_cards = board.get(FRONT, [])
        if len(front_cards) == 3:
            # Block straight/flush royalties in top row
            if self.is_top_row_straight_or_flush(front_cards):
                return royalty_points
            front_rank = self.evaluate_street(front_cards)
            
            # Check for pair or three of a kind
            ranks = [Card.get_rank_int(card) for card in front_cards]
            rank_counts = {}
            for rank in ranks:
                rank_counts[rank] = rank_counts.get(rank, 0) + 1
            
            # Check for three of a kind
            for rank, count in rank_counts.items():
                if count == 3:
                    rank_str = Card.STR_RANKS[rank]
                    royalty_key = f"Three of a Kind, {rank_str}s"
                    if royalty_key in ROYALTIES[FRONT]:
                        royalty_points[FRONT] = ROYALTIES[FRONT][royalty_key]
                    break
            
            # If no three of a kind, check for pairs
            if royalty_points[FRONT] == 0:
                for rank, count in rank_counts.items():
                    if count == 2:
                        rank_str = Card.STR_RANKS[rank]
                        royalty_key = f"Pair of {rank_str}s"
                        if royalty_key in ROYALTIES[FRONT]:
                            royalty_points[FRONT] = ROYALTIES[FRONT][royalty_key]
                        break
        
        # Calculate middle and back street royalties
        for street in [MIDDLE, BACK]:
            street_cards = board.get(street, [])
            if len(street_cards) == 5:
                rank = self.evaluate_street(street_cards)
                category = get_hand_category(rank, len(street_cards))
                
                if category in ROYALTIES[street]:
                    royalty_points[street] = ROYALTIES[street][category]
        
        return royalty_points
    
    def compare_streets(self, board1, board2):
        """
        Compare two boards street by street
        
        Args:
            board1: Dictionary of street names to lists of cards for player 1
            board2: Dictionary of street names to lists of cards for player 2
            
        Returns:
            Dictionary with result of comparison for each street and overall points
        """
        # Initialize results
        results = {
            FRONT: 0,  # 1 for player1 win, -1 for player2 win, 0 for tie
            MIDDLE: 0,
            BACK: 0,
            'player1_points': 0,
            'player2_points': 0,
            'player1_royalties': 0,
            'player2_royalties': 0
        }
        
        # Check if either board is fouled
        board1_valid = self.is_valid_board(board1)
        board2_valid = self.is_valid_board(board2)
        
        # If both boards are fouled, no points awarded
        if not board1_valid and not board2_valid:
            return results
        
        # If only one board is fouled, the other player gets 6 points and all their royalties, and the fouled player pays opponent's royalties
        if not board1_valid:
            results['player2_points'] = 6 + sum(self.get_royalties(board2).values())
            results[FRONT] = -1
            results[MIDDLE] = -1
            results[BACK] = -1
            # Fouled player forfeits all royalties
            results['player1_royalties'] = 0
            results['player2_royalties'] = sum(self.get_royalties(board2).values())
            return results
        
        if not board2_valid:
            results['player1_points'] = 6 + sum(self.get_royalties(board1).values())
            results[FRONT] = 1
            results[MIDDLE] = 1
            results[BACK] = 1
            # Fouled player forfeits all royalties
            results['player2_royalties'] = 0
            results['player1_royalties'] = sum(self.get_royalties(board1).values())
            return results
        
        # Both boards are valid, compare each street
        p1_wins = 0
        p2_wins = 0
        
        # Calculate royalties
        p1_royalties = self.get_royalties(board1)
        p2_royalties = self.get_royalties(board2)
        
        results['player1_royalties'] = sum(p1_royalties.values())
        results['player2_royalties'] = sum(p2_royalties.values())
        
        # Compare each street
        for street in [FRONT, MIDDLE, BACK]:
            p1_rank = self.evaluate_street(board1.get(street, []))
            p2_rank = self.evaluate_street(board2.get(street, []))
            
            # Lower rank is better in deuces
            if p1_rank < p2_rank:
                results[street] = 1
                p1_wins += 1
                results['player1_points'] += 1
            elif p2_rank < p1_rank:
                results[street] = -1
                p2_wins += 1
                results['player2_points'] += 1
        
        # Check for scoop (winning all three streets)
        if p1_wins == 3:
            results['player1_points'] += 3  # Scoop bonus
        elif p2_wins == 3:
            results['player2_points'] += 3  # Scoop bonus
        
        # Adjust total points
        results['player1_points'] += results['player1_royalties']
        results['player2_points'] += results['player2_royalties']
        
        return results