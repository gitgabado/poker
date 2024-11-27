# File name: texas_holdem_advisor.py

import streamlit as st
from treys import Card, Evaluator, Deck
import random
import re

# Function to parse card input
def parse_card(card_str):
    rank_map = {
        '2': '2',
        '3': '3',
        '4': '4',
        '5': '5',
        '6': '6',
        '7': '7',
        '8': '8',
        '9': '9',
        '10': 'T',
        't': 'T',
        'ten': 'T',
        'j': 'J',
        'jack': 'J',
        'q': 'Q',
        'queen': 'Q',
        'k': 'K',
        'king': 'K',
        'a': 'A',
        'ace': 'A'
    }
    suit_map = {
        's': 's',
        'spades': 's',
        '♠': 's',
        'h': 'h',
        'hearts': 'h',
        '♥': 'h',
        'd': 'd',
        'diamonds': 'd',
        '♦': 'd',
        'c': 'c',
        'clubs': 'c',
        '♣': 'c'
    }

    # Remove spaces and make lower case
    card_str = card_str.strip().lower().replace(' ', '')

    # Build regex pattern
    rank_pattern = '|'.join(sorted(rank_map.keys(), key=lambda x: -len(x)))  # Longest first to match '10' before '1'
    suit_pattern = '|'.join(sorted(suit_map.keys(), key=lambda x: -len(x)))  # Longest first

    pattern = f'^({rank_pattern})({suit_pattern})$'

    match = re.match(pattern, card_str)
    if match:
        rank_input = match.group(1)
        suit_input = match.group(2)
        rank = rank_map.get(rank_input)
        suit = suit_map.get(suit_input)
        if rank and suit:
            card_str_standard = rank + suit
            try:
                return Card.new(card_str_standard)
            except:
                st.error(f"Invalid card input: {card_str}")
                return None
    else:
        st.error(f"Invalid card input: {card_str}")
        return None

# Function to calculate winning probability (unchanged)
def calculate_win_prob(hole_cards, community_cards, num_opponents=1, num_simulations=1000):
    evaluator = Evaluator()
    wins = 0
    ties = 0
    losses = 0

    # Known cards
    known_cards = hole_cards + community_cards

    # Check if there are enough cards in the deck
    total_known_cards = len(known_cards)
    cards_needed_per_simulation = num_opponents * 2 + (5 - len(community_cards))
    if total_known_cards + cards_needed_per_simulation > 52:
        st.error("Not enough cards to simulate this scenario with the given number of opponents.")
        return None, None, None

    for _ in range(num_simulations):
        # Prepare deck
        deck = Deck()
        for card in known_cards:
            if card in deck.cards:
                deck.cards.remove(card)

        # Shuffle the deck
        random.shuffle(deck.cards)

        # Draw opponents' hole cards
        opponents_hole_cards = []
        for _ in range(num_opponents):
            opp_hole = [deck.draw(1)[0], deck.draw(1)[0]]
            opponents_hole_cards.append(opp_hole)

        # Complete community cards if needed
        needed_community_cards = 5 - len(community_cards)
        current_community = community_cards[:]
        if needed_community_cards > 0:
            current_community += deck.draw(needed_community_cards)

        # Evaluate player's hand
        player_score = evaluator.evaluate(hole_cards, current_community)

        # Evaluate opponents' hands
        opponent_better = False
        tie = False
        for opp_hole in opponents_hole_cards:
            opp_score = evaluator.evaluate(opp_hole, current_community)
            if opp_score < player_score:
                opponent_better = True
                break
            elif opp_score == player_score:
                tie = True

        if opponent_better:
            losses += 1
        elif tie:
            ties += 1
        else:
            wins += 1

        # No need to return cards to the deck since we create a fresh deck each simulation

    total = wins + ties + losses
    win_prob = (wins / total) * 100
    tie_prob = (ties / total) * 100
    loss_prob = (losses / total) * 100

    return win_prob, tie_prob, loss_prob

# Initialize session state variables if they don't exist
if 'hole_card_1' not in st.session_state:
    st.session_state['hole_card_1'] = ''
if 'hole_card_2' not in st.session_state:
    st.session_state['hole_card_2'] = ''
if 'community_cards' not in st.session_state:
    st.session_state['community_cards'] = ''

# Streamlit UI
st.title("♠️ Texas Hold'em Advisory App ♠️")

st.sidebar.header("Game Settings")
num_opponents = st.sidebar.slider("Number of Opponents", 1, 8, 1)
num_simulations = st.sidebar.slider("Number of Simulations", 1000, 10000, 1000, step=1000)

st.header("Enter Your Hole Cards")
col1, col2 = st.columns(2)
with col1:
    hole_card_1 = st.text_input("Hole Card 1 (e.g., As, Kh, 5d)", value=st.session_state['
