# Open-face Chinese Poker Trainer

This is an implementation of an Open-face Chinese Poker (OFC) trainer based on the paper "Mastering Open-face Chinese Poker by Self-play Reinforcement Learning" by Andrew Tan and Jarry Xiao.

## Rules

Open-face Chinese Poker is a stochastic, perfect-information zero-sum game played between 2-4 players. This implementation focuses on the two-player variant.

### Basic Rules:
- Each player takes turns placing cards on their board with three streets: front (3 cards), middle (5 cards), and back (5 cards).
- On the first turn, each player is dealt 5 cards and may place them in any valid configuration.
- For subsequent turns, players are dealt a single card and can place it on any street that is not fully occupied.
- All actions are visible to both players.
- For a valid board, the back street must contain a poker hand that beats the hand in the middle street, and the middle street must beat the hand in the front street.
- If a player's board is invalid ("fouled"), they forfeit all street comparisons and are not eligible for royalties.

### Scoring:
- Points are computed by pairwise comparisons of streets.
- A player receives 1 point for each street they win.
- If a player wins all 3 streets, they receive 3 additional points for "scooping".
- Additional points ("royalties") are awarded for premium hands in each street.

## Getting Started

### Prerequisites
- Python 3.7+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ofc-trainer.git
cd ofc-trainer

# Install dependencies
pip install -r requirements.txt
```

### Running the Trainer

```bash
python -m src.trainer
```

## Features

- Full Open-face Chinese Poker game simulator
- Interactive gameplay for testing strategies
- Evaluates hands, determines scores, and enforces game rules

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This implementation uses the [deuces](https://github.com/worldveil/deuces) library for poker hand evaluation.
- Based on research by Andrew Tan and Jarry Xiao on reinforcement learning for OFC Poker.