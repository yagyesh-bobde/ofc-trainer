import unittest
from deuces import Card
from src.game import OFCGame
from src.player import RandomPlayer
from src.utils import FRONT, MIDDLE, BACK

class TestOFCGame(unittest.TestCase):
    
    def setUp(self):
        """Set up a new game before each test"""
        self.player1 = RandomPlayer("Player1")
        self.player2 = RandomPlayer("Player2")
        self.game = OFCGame(self.player1, self.player2)
    
    def test_game_initialization(self):
        """Test that the game initializes correctly"""
        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(self.game.current_player_idx, 0)
        self.assertFalse(self.game.game_over)
        self.assertIsNone(self.game.results)
        
        # The deuces Deck doesn't provide a direct size method,
        # so we'll just verify we can draw cards
    
    def test_deal_initial_cards(self):
        """Test that the initial cards are dealt correctly"""
        self.game.deal_initial_cards()
        
        # Check that each player has 5 cards
        self.assertEqual(len(self.player1.hand), 5)
        self.assertEqual(len(self.player2.hand), 5)
        
        # We can't directly check the deck size in deuces,
        # but we can verify we dealt 10 cards
    
    def test_deal_card(self):
        """Test that a single card is dealt correctly"""
        # Deal a card to the current player
        card = self.game.deal_card()
        
        # Check that the card was dealt
        self.assertIsNotNone(card)
        self.assertEqual(len(self.player1.hand), 1)
    
    def test_place_card(self):
        """Test that a card is placed correctly"""
        # Deal a card to the current player
        self.game.deal_card()
        
        # Place the card
        success = self.game.place_card(FRONT)
        
        # Check that the card was placed
        self.assertTrue(success)
        self.assertEqual(len(self.player1.hand), 0)
        self.assertEqual(len(self.player1.board[FRONT]), 1)
    
    def test_switch_player(self):
        """Test that the current player switches correctly"""
        initial_player_idx = self.game.current_player_idx
        
        # Switch player
        self.game.switch_player()
        
        # Check that the current player has changed
        self.assertNotEqual(self.game.current_player_idx, initial_player_idx)
        self.assertEqual(self.game.current_player_idx, 1)
    
    def test_is_game_over(self):
        """Test that the game over condition is detected correctly"""
        # Initially the game is not over
        self.assertFalse(self.game.is_game_over())
        
        # Manually fill player boards
        for player in self.game.players:
            # Fill front
            for _ in range(3):
                card = self.game.deck.draw()
                player.receive_cards([card])
                player.place_card(card, FRONT)
            
            # Fill middle
            for _ in range(5):
                card = self.game.deck.draw()
                player.receive_cards([card])
                player.place_card(card, MIDDLE)
            
            # Fill back
            for _ in range(5):
                card = self.game.deck.draw()
                player.receive_cards([card])
                player.place_card(card, BACK)
        
        # Now the game should be over
        self.assertTrue(self.game.is_game_over())
    
    def test_play_game(self):
        """Test that a full game plays correctly"""
        # Play a full game
        results = self.game.play_game(verbose=False)
        
        # Check that results are returned
        self.assertIsNotNone(results)
        
        # Check that the game is marked as over
        self.assertTrue(self.game.game_over)
        
        # Check that both players have complete boards
        for player in self.game.players:
            self.assertEqual(len(player.board[FRONT]), 3)
            self.assertEqual(len(player.board[MIDDLE]), 5)
            self.assertEqual(len(player.board[BACK]), 5)
            self.assertEqual(len(player.hand), 0)

if __name__ == '__main__':
    unittest.main()