import random
from deuces import Card, Deck
from .utils import FRONT, MIDDLE, BACK, print_board, print_card, print_cards
from .evaluator import OFCEvaluator

JOKER_1 = 53  # Arbitrary unique int for joker 1
JOKER_2 = 54  # Arbitrary unique int for joker 2

class CustomDeck:
    """A deck of 52 cards plus 2 jokers"""
    def __init__(self):
        self.cards = [Card.new(rank + suit) for rank in '23456789TJQKA' for suit in 'shdc']
        self.cards.append(JOKER_1)
        self.cards.append(JOKER_2)
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n=1):
        if n == 1:
            return self.cards.pop() if self.cards else None
        else:
            return [self.cards.pop() for _ in range(n) if self.cards]

class OFCGame:
    """Open-face Chinese Poker game environment"""
    
    def __init__(self, player1, player2):
        """
        Initialize a game with two players
        
        Args:
            player1: First player object
            player2: Second player object
        """
        self.players = [player1, player2]
        self.current_player_idx = 0
        self.evaluator = OFCEvaluator()
        self.deck = CustomDeck()
        self.game_over = False
        self.results = None
    
    def reset(self):
        """Reset the game state"""
        self.deck = CustomDeck()
        self.current_player_idx = 0
        self.game_over = False
        self.results = None
        
        # Reset players
        for player in self.players:
            player.reset()
    
    def deal_initial_cards(self):
        """Deal the initial 5 cards to each player"""
        # Deal 5 cards to each player
        for player in self.players:
            cards = [self.deck.draw() for _ in range(5)]
            player.receive_cards(cards)
    
    def deal_card(self):
        """Deal a single card to the current player"""
        try:
            card = self.deck.draw()
            if card is None:
                print("Deck is empty!")
                self.game_over = True
                return None
            self.players[self.current_player_idx].receive_cards([card])
            return card
        except IndexError:
            # If we get an index error, the deck is empty
            print("Deck is empty!")
            self.game_over = True
            return None
    
    def place_card(self, street):
        """
        Place a card from the current player's hand to a street
        
        Args:
            street: Street name (front, middle, back)
            
        Returns:
            Boolean indicating if the placement was successful
        """
        player = self.players[self.current_player_idx]
        
        if not player.hand:
            print("Player has no cards in hand")
            return False
        
        card = player.hand[0]
        return player.place_card(card, street)
    
    def switch_player(self):
        """Switch to the next player"""
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
    
    def is_game_over(self):
        """
        Check if the game is over (both players have completed their boards)
        
        Returns:
            Boolean indicating if the game is over
        """
        return all(player.is_board_complete() for player in self.players)
    
    def get_current_player(self):
        """Get the current player"""
        return self.players[self.current_player_idx]
    
    def play_turn(self):
        """
        Play a single turn:
        1. Deal a card to the current player
        2. Get the player's move
        3. Place the card
        4. Switch to the next player
        
        Returns:
            Boolean indicating if the turn was completed successfully
        """
        if self.game_over:
            return False
        
        # Deal a card to the current player
        card = self.deal_card()
        if card is None:
            return False
        
        # Get the player's move
        player = self.get_current_player()
        move = player.select_move(card)
        
        if move is None:
            print("No legal moves available")
            return False
        
        # Place the card
        success = player.place_card(card, move)
        if not success:
            print("Failed to place card")
            return False
        
        # Check if the game is over
        if self.is_game_over():
            self.game_over = True
            self.calculate_results()
            return True
        
        # Switch to the next player
        self.switch_player()
        return True
    
    def play_initial_round(self):
        """
        Play the initial round where both players place their first 5 cards (all at once)
        Returns:
            Boolean indicating if the initial round was completed successfully
        """
        # Deal initial cards
        self.deal_initial_cards()
        # Each player places all 5 cards in their first turn
        for _ in range(len(self.players)):
            player = self.get_current_player()
            if hasattr(player, 'select_initial_placements'):
                cards = player.hand[:]
                player.select_initial_placements(cards)
            else:
                # Fallback: place one at a time
                for _ in range(5):
                    if not player.hand:
                        print("Player has no cards in hand")
                        return False
                    card = player.hand[0]
                    move = player.select_move(card)
                    if move is None:
                        print("No legal moves available")
                        return False
                    success = player.place_card(card, move)
                    if not success:
                        print("Failed to place card")
                        return False
            # Switch to the next player
            self.switch_player()
        return True
    
    def calculate_results(self):
        """
        Calculate the game results
        
        Returns:
            Dictionary with the comparison results
        """
        player1_board = self.players[0].board
        player2_board = self.players[1].board
        
        self.results = self.evaluator.compare_streets(player1_board, player2_board)
        return self.results
    
    def play_pineapple_rounds(self):
        """
        Play the 4 Pineapple rounds: each player receives 3 cards, places 2, discards 1, until 13 cards are set.
        """
        for _ in range(4):  # 4 rounds to reach 13 cards (5 + 2*4 = 13)
            for player in self.players:
                # Deal 3 cards
                cards = [self.deck.draw() for _ in range(3)]
                player.receive_cards(cards)
                # Player must choose 2 to place, 1 to discard
                if hasattr(player, 'select_pineapple_moves'):
                    place_cards, discard_card = player.select_pineapple_moves(cards)
                else:
                    # Default: place first 2, discard last
                    place_cards, discard_card = cards[:2], cards[2]
                for card in place_cards:
                    move = player.select_move(card)
                    player.place_card(card, move)
                # Remove the discarded card from hand
                if discard_card in player.hand:
                    player.hand.remove(discard_card)

    def print_running_points(self):
        """Print current boards and running points/royalties if possible."""
        print("\nCurrent Boards:")
        for i, player in enumerate(self.players):
            print(f"Player {i+1} (ID: {player.player_id}):")
            print(print_board(player.board))
        # Only score if both boards have at least one full street
        p1 = self.players[0]
        p2 = self.players[1]
        # Score only filled streets
        def partial_board(board):
            return {
                FRONT: board[FRONT] if len(board[FRONT]) == 3 else [],
                MIDDLE: board[MIDDLE] if len(board[MIDDLE]) == 5 else [],
                BACK: board[BACK] if len(board[BACK]) == 5 else [],
            }
        p1_partial = partial_board(p1.board)
        p2_partial = partial_board(p2.board)
        results = self.evaluator.compare_streets(p1_partial, p2_partial)
        print("\nRunning Points:")
        print(f"Player 1: {results['player1_points']} (Royalties: {results['player1_royalties']})")
        print(f"Player 2: {results['player2_points']} (Royalties: {results['player2_royalties']})")
        print(f"Street Results: Front: {results[FRONT]}, Middle: {results[MIDDLE]}, Back: {results[BACK]}")

    def play_game(self, verbose=True):
        """
        Play a complete game with Pineapple mechanics and Fantasyland
        """
        # Reset the game
        self.reset()
        for player in self.players:
            player.in_fantasyland = False
        if verbose:
            print("Starting a new game of Open-face Chinese Poker")
        # Initial round - 5 cards each
        success = self.play_initial_round()
        if not success:
            print("Error in initial round")
            return None
        if verbose:
            print("\nAfter initial round:")
            self.print_game_state()
            self.print_running_points()
        # Pineapple rounds: 3 cards, place 2, discard 1, repeat 4 times
        for pineapple_round in range(4):
            self.play_pineapple_rounds_step()
            if verbose:
                print(f"\nAfter Pineapple round {pineapple_round+1}:")
                self.print_game_state()
                self.print_running_points()
        # Game is over after 13 cards
        self.game_over = True
        self.calculate_results()
        if verbose:
            print("\nGame over! Final boards:")
            self.print_game_state()
            self.print_results()
        # Fantasyland check (for next hand)
        for i, player in enumerate(self.players):
            if self.qualifies_fantasyland(player):
                player.in_fantasyland = True
                if verbose:
                    print(f"Player {i+1} enters Fantasyland for next hand!")
        return self.results
    
    def print_game_state(self):
        """Print the current game state"""
        for i, player in enumerate(self.players):
            print(f"\nPlayer {i+1} (ID: {player.player_id}):")
            print(print_board(player.board))
            
            if player.hand:
                print("Hand:", print_cards(player.hand))
    
    def print_results(self):
        """Print the game results"""
        if self.results is None:
            print("No results available")
            return
        
        print("\nGame Results:")
        
        # Print street comparisons
        for street in [FRONT, MIDDLE, BACK]:
            result = self.results[street]
            if result == 1:
                winner = "Player 1"
            elif result == -1:
                winner = "Player 2"
            else:
                winner = "Tie"
            
            print(f"{street.capitalize()}: {winner}")
        
        # Print royalties
        print(f"\nPlayer 1 royalties: {self.results['player1_royalties']}")
        print(f"Player 2 royalties: {self.results['player2_royalties']}")
        
        # Print total points
        print(f"\nPlayer 1 total points: {self.results['player1_points']}")
        print(f"Player 2 total points: {self.results['player2_points']}")
        
        # Determine winner
        if self.results['player1_points'] > self.results['player2_points']:
            print("\nPlayer 1 wins!")
        elif self.results['player2_points'] > self.results['player1_points']:
            print("\nPlayer 2 wins!")
        else:
            print("\nIt's a tie!")

    def qualifies_fantasyland(self, player):
        """
        Check if player qualifies for Fantasyland (QQ+ in top row, valid hand)
        """
        from .utils import Card
        board = player.board
        if len(board[FRONT]) != 3:
            return False
        # Check for valid hand
        if not self.evaluator.is_valid_board(board):
            return False
        # Count ranks in top row
        ranks = [Card.get_rank_int(card) for card in board[FRONT]]
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        # QQ or better (rank 10=Q, 11=K, 12=A)
        for rank, count in rank_counts.items():
            if count == 2 and rank >= 10:
                return True
            if count == 3 and rank >= 10:
                return True
        return False

    def play_pineapple_rounds_step(self):
        """
        Play a single Pineapple round (3 cards to each, place 2, discard 1)
        """
        for player in self.players:
            # Deal 3 cards
            cards = [self.deck.draw() for _ in range(3)]
            player.receive_cards(cards)
            # Player must choose 2 to place, 1 to discard
            if hasattr(player, 'select_pineapple_moves'):
                place_cards, discard_card = player.select_pineapple_moves(cards)
            else:
                # Default: place first 2, discard last
                place_cards, discard_card = cards[:2], cards[2]
            for card in place_cards:
                move = player.select_move(card)
                player.place_card(card, move)
            # Remove the discarded card from hand
            if discard_card in player.hand:
                player.hand.remove(discard_card)