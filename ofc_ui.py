import streamlit as st
from src.game import OFCGame, CustomDeck
from src.player import HumanPlayer, GreedyPlayer, RandomPlayer
from src.utils import print_board, print_card, print_cards, FRONT, MIDDLE, BACK, html_card, html_cards

st.set_page_config(page_title="Pineapple OFC Trainer", layout="wide")
st.title("Pineapple Open Face Chinese Poker Trainer")

# --- Session State Setup ---
if 'game' not in st.session_state:
    player1 = HumanPlayer("You")
    player2 = GreedyPlayer("AI")
    st.session_state['game'] = OFCGame(player1, player2)
    st.session_state['step'] = 'init'  # 'init', 'pineapple', 'done'
    st.session_state['msg'] = ""
    st.session_state['last_points'] = None
    st.session_state['player1'] = player1
    st.session_state['player2'] = player2
    st.session_state['placed_init'] = []
    st.session_state['pineapple_round'] = 0
    st.session_state['pineapple_cards'] = []
    st.session_state['pineapple_placed'] = []
    st.session_state['pineapple_discard'] = None
    st.session_state['results'] = None
    st.session_state['show_points'] = False
    st.session_state['game'].reset()

# --- Helper Functions ---
def show_board(player, label):
    st.markdown(f"**{label}**")
    st.text(print_board(player.board))

def show_points(results):
    st.markdown("### Points & Royalties")
    cols = st.columns(2)
    cols[0].markdown(f"**You**\n- Total: {results['player1_points']}\n- Royalties: {results['player1_royalties']}")
    cols[1].markdown(f"**AI**\n- Total: {results['player2_points']}\n- Royalties: {results['player2_royalties']}")
    st.markdown(f"**Street Results:** Front: {results[FRONT]}, Middle: {results[MIDDLE]}, Back: {results[BACK]}")

# --- Main UI Logic ---
game = st.session_state['game']
player1 = st.session_state['player1']
player2 = st.session_state['player2']

# --- Initial Placement ---
if st.session_state['step'] == 'init':
    if 'init_cards' not in st.session_state or not st.session_state['init_cards']:
        game.deal_initial_cards()
        st.session_state['init_cards'] = game.players[0].hand[:]
        st.session_state['placed_init'] = []
        st.session_state['init_board'] = {FRONT: [], MIDDLE: [], BACK: []}
        # Reset player1's hand so we can place after all selections
        game.players[0].hand = []
    st.markdown("#### Place your initial 5 cards:")
    available = [c for c in st.session_state['init_cards'] if c not in [x[0] for x in st.session_state['placed_init']]]
    cols = st.columns(len(available) if available else 1)
    card_clicked = None
    for i, card in enumerate(available):
        if cols[i].button("", key=f"init_card_{i}"):
            card_clicked = card
        cols[i].markdown(html_card(card), unsafe_allow_html=True)
    if card_clicked is not None:
        row = st.radio("Select row for this card:", [FRONT, MIDDLE, BACK], key=f"init_row_{card_clicked}")
        if st.button(f"Place {print_card(card_clicked)} in {row}", key=f"place_init_card_{card_clicked}"):
            if len(st.session_state['init_board'][row]) < (3 if row==FRONT else 5):
                st.session_state['init_board'][row].append(card_clicked)
                st.session_state['placed_init'].append((card_clicked, row))
                st.experimental_rerun()
    st.markdown(html_cards([c for c, _ in st.session_state['placed_init']]), unsafe_allow_html=True)
    # Show preview board
    preview_board = {FRONT: [], MIDDLE: [], BACK: []}
    for c, r in st.session_state['placed_init']:
        preview_board[r].append(c)
    st.text(print_board(preview_board))
    if len(st.session_state['placed_init']) == 5:
        # Now actually place the cards in the backend
        for c, r in st.session_state['placed_init']:
            player1.place_card(c, r)
        # AI places its 5 cards
        player2.select_initial_placements(player2.hand[:])
        st.session_state['step'] = 'pineapple'
        st.session_state['init_cards'] = []
        st.session_state['placed_init'] = []
        st.session_state['init_board'] = {FRONT: [], MIDDLE: [], BACK: []}
        st.experimental_rerun()

# --- Pineapple Rounds ---
elif st.session_state['step'] == 'pineapple':
    round_num = st.session_state['pineapple_round']
    if round_num < 4:
        if not st.session_state['pineapple_cards']:
            cards = [game.deck.draw() for _ in range(3)]
            player1.receive_cards(cards)
            st.session_state['pineapple_cards'] = cards
            st.session_state['pineapple_placed'] = []
            st.session_state['pineapple_discard'] = None
        st.markdown(f"#### Pineapple Round {round_num+1}: Place 2, Discard 1")
        cols = st.columns(3)
        for i, card in enumerate(st.session_state['pineapple_cards']):
            cols[i].button(print_card(card), key=f"pineapple_card_{i}")
        # Place 2
        card_idx = st.multiselect("Pick 2 cards to place (by index):", [1,2,3], key="pineapple_place")
        row = st.radio("Select row for next card:", [FRONT, MIDDLE, BACK], key="pineapple_row")
        if len(card_idx) == 1 and st.button("Place Card", key="place_pineapple_card1"):
            card = st.session_state['pineapple_cards'][card_idx[0]-1]
            if card not in [x[0] for x in st.session_state['pineapple_placed']]:
                if len(player1.board[row]) < (3 if row==FRONT else 5):
                    player1.place_card(card, row)
                    st.session_state['pineapple_placed'].append((card, row))
        if len(card_idx) == 2 and st.button("Place Card 2", key="place_pineapple_card2"):
            for idx in card_idx:
                card = st.session_state['pineapple_cards'][idx-1]
                if card not in [x[0] for x in st.session_state['pineapple_placed']]:
                    if len(player1.board[row]) < (3 if row==FRONT else 5):
                        player1.place_card(card, row)
                        st.session_state['pineapple_placed'].append((card, row))
        # Discard
        if len(st.session_state['pineapple_placed']) == 2:
            discard_idx = [i for i in range(3) if st.session_state['pineapple_cards'][i] not in [x[0] for x in st.session_state['pineapple_placed']]][0]
            st.session_state['pineapple_discard'] = st.session_state['pineapple_cards'][discard_idx]
            if st.button("Confirm Discard and Next Round"):
                if st.session_state['pineapple_discard'] in player1.hand:
                    player1.hand.remove(st.session_state['pineapple_discard'])
                # AI turn
                ai_cards = [game.deck.draw() for _ in range(3)]
                player2.receive_cards(ai_cards)
                place, discard = player2.select_pineapple_moves(ai_cards)
                for card in place:
                    move = player2.select_move(card)
                    player2.place_card(card, move)
                if discard in player2.hand:
                    player2.hand.remove(discard)
                st.session_state['pineapple_round'] += 1
                st.session_state['pineapple_cards'] = []
                st.session_state['pineapple_placed'] = []
                st.session_state['pineapple_discard'] = None
                st.experimental_rerun()
        st.text(print_board(player1.board))
        st.text("AI Board:")
        st.text(print_board(player2.board))
    else:
        # Game over, calculate results
        game.game_over = True
        game.calculate_results()
        st.session_state['results'] = game.results
        st.session_state['step'] = 'done'
        st.experimental_rerun()

# --- Game Over ---
elif st.session_state['step'] == 'done':
    st.markdown("## Final Boards")
    show_board(player1, "Your Board")
    show_board(player2, "AI Board")
    if st.session_state['results']:
        show_points(st.session_state['results'])
    if st.button("Play Again"):
        del st.session_state['game']
        st.experimental_rerun() 