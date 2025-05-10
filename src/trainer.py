#!/usr/bin/env python3
"""
Open-face Chinese Poker Trainer
This is the main entry point for the OFC trainer
"""

import argparse
import random
import time
from .game import OFCGame
from .player import RandomPlayer, HumanPlayer, GreedyPlayer

def play_game(player1_type, player2_type, verbose=True):
    """
    Play a game of Open-face Chinese Poker
    
    Args:
        player1_type: Type of player 1 ('random', 'greedy', 'human')
        player2_type: Type of player 2 ('random', 'greedy', 'human')
        verbose: If True, print game progress
        
    Returns:
        Game results
    """
    # Create players
    player1 = create_player(player1_type, "Player1")
    player2 = create_player(player2_type, "Player2")
    
    # Create game
    game = OFCGame(player1, player2)
    
    # Play game
    results = game.play_game(verbose=verbose)
    
    return results

def create_player(player_type, player_id):
    """
    Create a player of the specified type
    
    Args:
        player_type: Type of player ('random', 'greedy', 'human')
        player_id: Player identifier
        
    Returns:
        Player object
    """
    if player_type == 'random':
        return RandomPlayer(player_id)
    elif player_type == 'greedy':
        return GreedyPlayer(player_id)
    elif player_type == 'human':
        return HumanPlayer(player_id)
    else:
        raise ValueError(f"Unknown player type: {player_type}")

def evaluate_players(player1_type, player2_type, num_games=100):
    """
    Evaluate two player types by playing multiple games
    
    Args:
        player1_type: Type of player 1 ('random', 'greedy')
        player2_type: Type of player 2 ('random', 'greedy')
        num_games: Number of games to play
        
    Returns:
        Dictionary with evaluation results
    """
    player1_wins = 0
    player2_wins = 0
    ties = 0
    
    player1_points = 0
    player2_points = 0
    
    start_time = time.time()
    
    for game_num in range(num_games):
        # Progress indicator
        if (game_num + 1) % 10 == 0:
            print(f"Playing game {game_num + 1}/{num_games}...")
        
        # Play a game
        results = play_game(player1_type, player2_type, verbose=False)
        
        # Count wins
        if results['player1_points'] > results['player2_points']:
            player1_wins += 1
        elif results['player2_points'] > results['player1_points']:
            player2_wins += 1
        else:
            ties += 1
        
        # Accumulate points
        player1_points += results['player1_points']
        player2_points += results['player2_points']
    
    end_time = time.time()
    
    # Compute statistics
    win_rate_player1 = player1_wins / num_games
    win_rate_player2 = player2_wins / num_games
    tie_rate = ties / num_games
    
    avg_points_player1 = player1_points / num_games
    avg_points_player2 = player2_points / num_games
    
    # Return results
    return {
        'num_games': num_games,
        'player1_type': player1_type,
        'player2_type': player2_type,
        'player1_wins': player1_wins,
        'player2_wins': player2_wins,
        'ties': ties,
        'win_rate_player1': win_rate_player1,
        'win_rate_player2': win_rate_player2,
        'tie_rate': tie_rate,
        'total_points_player1': player1_points,
        'total_points_player2': player2_points,
        'avg_points_player1': avg_points_player1,
        'avg_points_player2': avg_points_player2,
        'time_elapsed': end_time - start_time
    }

def print_evaluation_results(results):
    """
    Print evaluation results
    
    Args:
        results: Dictionary with evaluation results
    """
    print("\nEvaluation Results:")
    print(f"Player 1 ({results['player1_type']})")
    print(f"Player 2 ({results['player2_type']})")
    print(f"Number of games: {results['num_games']}")
    print(f"Time elapsed: {results['time_elapsed']:.2f} seconds")
    print("\nWin Statistics:")
    print(f"Player 1 wins: {results['player1_wins']} ({results['win_rate_player1'] * 100:.2f}%)")
    print(f"Player 2 wins: {results['player2_wins']} ({results['win_rate_player2'] * 100:.2f}%)")
    print(f"Ties: {results['ties']} ({results['tie_rate'] * 100:.2f}%)")
    print("\nPoint Statistics:")
    print(f"Player 1 total points: {results['total_points_player1']}")
    print(f"Player 2 total points: {results['total_points_player2']}")
    print(f"Player 1 average points per game: {results['avg_points_player1']:.2f}")
    print(f"Player 2 average points per game: {results['avg_points_player2']:.2f}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Open-face Chinese Poker Trainer')
    
    # Game mode
    parser.add_argument('--mode', choices=['play', 'evaluate'], default='play',
                        help='Play a single game or evaluate player types')
    
    # Player types
    parser.add_argument('--player1', choices=['random', 'greedy', 'human'], default='human',
                        help='Type of player 1')
    parser.add_argument('--player2', choices=['random', 'greedy', 'human'], default='random',
                        help='Type of player 2')
    
    # Evaluation settings
    parser.add_argument('--num-games', type=int, default=100,
                        help='Number of games to play in evaluation mode')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set random seed for reproducibility
    random.seed(42)
    
    if args.mode == 'play':
        # Play a single game
        play_game(args.player1, args.player2, verbose=True)
    else:
        # Evaluate player types
        results = evaluate_players(args.player1, args.player2, num_games=args.num_games)
        print_evaluation_results(results)

if __name__ == '__main__':
    main()