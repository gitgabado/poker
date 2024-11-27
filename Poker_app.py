import streamlit as st
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.players import BasePokerPlayer
import random

class HonestPlayer(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        return valid_actions[1]['action'], valid_actions[1]['amount']

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


def calculate_win_probability(current_hand, community_cards):
    if not current_hand or len(current_hand) < 4:
        st.error("Please enter two valid pocket cards.")
        return

    hole_cards = [
        current_hand[:2],  # e.g. 'AH'
        current_hand[2:],  # e.g. 'AS'
    ]
    community_card_strings = community_cards.split()

    community_cards = []
    for card in community_card_strings:
        if len(card) == 2:
            community_cards.append(card)

    # Set up the game configuration
    config = setup_config(max_round=10, initial_stack=1000, small_blind_amount=10)
    config.register_player(name="player", algorithm=HonestPlayer())
    config.register_player(name="opponent", algorithm=HonestPlayer())

    # Simulate multiple games to determine winning probability
    num_simulations = 1000
    win_count = 0
    for _ in range(num_simulations):
        game_result = start_poker(config, verbose=0)
        if game_result['players'][0]['stack'] > game_result['players'][1]['stack']:
            win_count += 1

    win_probability = (win_count / num_simulations) * 100
    st.markdown(f"<h2 style='color: #ff6347;'><b>Winning Probability: {win_probability:.2f}%</b></h2>", unsafe_allow_html=True)

    # Provide advice based on winning probability
    if win_probability >= 75:
        st.markdown("<h3 style='color: #ffa500;'><b>Advice: Consider making a 4x raise. Pocket Aces or Kings are extremely strong!</b></h3>", unsafe_allow_html=True)
    elif 55 <= win_probability < 75:
        st.markdown("<h3 style='color: #ffa500;'><b>Advice: Consider making a 3x raise.</b></h3>", unsafe_allow_html=True)
    elif 30 <= win_probability < 55:
        st.markdown("<h3 style='color: #ffa500;'><b>Advice: It might be better to check or call.</b></h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='color: #ffa500;'><b>Advice: It might be better to fold.</b></h3>", unsafe_allow_html=True)


# Streamlit app interface
st.title("Poker Learning App - Ultimate Texas Hold'em")
st.header("Learn Poker with Winning Probability at Flop, Turn, and River")

# Initialize session state for input fields if not already done
if 'current_hand' not in st.session_state:
    st.session_state.current_hand = ""
if 'community_cards' not in st.session_state:
    st.session_state.community_cards = ""

# Input section
current_hand = st.text_input("Enter your pocket cards (e.g., AHAS)", value=st.session_state.current_hand, key="current_hand")
community_cards = st.text_input("Enter community cards (e.g., 7S 2H 9C) - Add more at each stage", value=st.session_state.community_cards, key="community_cards")

calculate_button = st.button("Calculate Winning Probability")

def reset_cards():
    st.session_state.current_hand = ""
    st.session_state.community_cards = ""

reset_button = st.button("Reset Cards", on_click=reset_cards)

if calculate_button:
    # Calculate win probability
    calculate_win_probability(current_hand, community_cards)

# Explanation
st.markdown("---")
st.header("How to use this App")
st.write("""
- Enter your pocket cards initially to see the winning probability.
- Add community cards as they appear at flop, turn, and river to see updated probabilities.
- The app will provide advice based on the winning probability and current stage.
- Note: This advice is tailored for Ultimate Texas Hold'em, which is a dealer vs. player game.
- You can use the "Reset Cards" button to quickly enter new pocket cards for a new round.
""")
