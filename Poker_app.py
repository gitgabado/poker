# File name: ultimate_texas_holdem_advisor.py

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
    rank_pattern = '|'.join(sorted(rank_map.keys(), key=lambda x: -len(x)))  # Longest first
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

# Function to get strategic advice
def get_advice(hole_cards, community_cards, stage):
    evaluator = Evaluator()
    # Convert hole_cards to rank and suit
    rank_int_to_str = {14: 'A', 13: 'K', 12: 'Q', 11: 'J', 10: 'T', 9: '9', 8: '8', 7: '7',
                       6: '6', 5: '5', 4: '4', 3: '3', 2: '2'}
    suit_int_to_char = {1: 's', 2: 'h', 4: 'd', 8: 'c'}

    # Extract ranks and suits
    card1_rank = Card.get_rank_int(hole_cards[0])
    card1_suit = Card.get_suit_int(hole_cards[0])
    card2_rank = Card.get_rank_int(hole_cards[1])
    card2_suit = Card.get_suit_int(hole_cards[1])

    card1_rank_str = rank_int_to_str[card1_rank]
    card2_rank_str = rank_int_to_str[card2_rank]

    card1_suit_char = suit_int_to_char[card1_suit]
    card2_suit_char = suit_int_to_char[card2_suit]

    # Determine if cards are suited
    suited = card1_suit == card2_suit

    # Build hand representation
    hand = card1_rank_str + card2_rank_str
    if suited:
        hand += 's'
    else:
        hand += 'o'  # 'o' for offsuit

    # Strategy based on stage
    advice = ""
    if stage == "Pre-Flop":
        advice = pre_flop_strategy(card1_rank, card2_rank, suited)
    elif stage == "Post-Flop":
        advice = post_flop_strategy(hole_cards, community_cards)
    elif stage == "River":
        advice = river_strategy(hole_cards, community_cards)
    else:
        advice = "No advice available."

    return advice

# Pre-Flop Strategy for Ultimate Texas Hold'em
def pre_flop_strategy(card1_rank, card2_rank, suited):
    high_card = max(card1_rank, card2_rank)
    low_card = min(card1_rank, card2_rank)

    # Convert rank integers to 2-14 (2 being lowest, Ace being 14)
    # Pairs
    if card1_rank == card2_rank:
        return "Raise 4x"
    # Any Ace
    if card1_rank == 14 or card2_rank == 14:
        return "Raise 4x"
    # King-high hands (K5 or better)
    if high_card == 13 and low_card >= 5:
        return "Raise 4x"
    # Queen-high hands (Q8 or better)
    if high_card == 12 and low_card >= 8:
        return "Raise 4x"
    # Jack-high suited (J10 suited)
    if suited and ((card1_rank == 11 and card2_rank == 10) or (card1_rank == 10 and card2_rank == 11)):
        return "Raise 4x"
    # Else
    return "Check"

# Post-Flop Strategy
def post_flop_strategy(hole_cards, community_cards):
    evaluator = Evaluator()
    hand_rank = evaluator.evaluate(hole_cards, community_cards)
    hand_class = evaluator.get_rank_class(hand_rank)

    # Get hand class name
    hand_name = Evaluator.class_to_string(hand_class)

    # Check for made hand (pair or better)
    if hand_class <= 6:  # High Card is class 9, so <=6 means at least a Pair
        return "Raise 2x"
    # Check for four to a flush
    if has_four_to_flush(hole_cards, community_cards):
        return "Raise 2x"
    # Check for four to a straight
    if has_four_to_straight(hole_cards, community_cards):
        return "Raise 2x"
    # Else
    return "Check"

# River Strategy
def river_strategy(hole_cards, community_cards):
    evaluator = Evaluator()
    hand_rank = evaluator.evaluate(hole_cards, community_cards)
    hand_class = evaluator.get_rank_class(hand_rank)

    # Call with Pair or better
    if hand_class <= 6:
        return "Call (Bet 1x)"
    # Else
    return "Fold"

# Helper function to check for four to a flush
def has_four_to_flush(hole_cards, community_cards):
    suits = [Card.get_suit_int(card) for card in hole_cards + community_cards]
    suit_counts = {}
    for suit in suits:
        suit_counts[suit] = suit_counts.get(suit, 0) + 1
    return max(suit_counts.values()) == 4

# Helper function to check for four to a straight
def has_four_to_straight(hole_cards, community_cards):
    ranks = [Card.get_rank_int(card) for card in hole_cards + community_cards]
    ranks = list(set(ranks))  # Remove duplicates
    ranks.sort()
    # Check for sequences of length 4
    for i in range(len(ranks) - 3):
        if ranks[i+3] - ranks[i] == 3:
            return True
    return False

# Function to calculate winning probability (modified for Ultimate Texas Hold'em)
def calculate_win_prob(hole_cards, community_cards, num_simulations=1000):
    evaluator = Evaluator()
    wins = 0
    ties = 0
    losses = 0

    # Known cards
    known_cards = hole_cards + community_cards

    for _ in range(num_simulations):
        # Prepare deck
        deck = Deck()
        for card in known_cards:
            if card in deck.cards:
                deck.cards.remove(card)

        # Shuffle the deck
        random.shuffle(deck.cards)

        # Dealer's hole cards
        dealer_hole_cards = [deck.draw(1)[0], deck.draw(1)[0]]

        # Complete community cards if needed
        needed_community_cards = 5 - len(community_cards)
        current_community = community_cards[:]
        if needed_community_cards > 0:
            current_community += deck.draw(needed_community_cards)

        # Evaluate player's hand
        player_score = evaluator.evaluate(hole_cards, current_community)
        player_class = evaluator.get_rank_class(player_score)

        # Evaluate dealer's hand
        dealer_score = evaluator.evaluate(dealer_hole_cards, current_community)
        dealer_class = evaluator.get_rank_class(dealer_score)

        # Dealer must qualify with a pair or better
        dealer_qualifies = dealer_class <= 6  # Pair or better

        if player_score < dealer_score:
            wins += 1
        elif player_score == dealer_score:
            ties += 1
        else:
            losses += 1

    total = wins + ties + losses
    win_prob = (wins / total) * 100
    tie_prob = (ties / total) * 100
    loss_prob = (losses / total) * 100

    return win_prob, tie_prob, loss_prob

# Streamlit UI
st.title("♠️ Ultimate Texas Hold'em Advisory App ♠️")

st.sidebar.header("Game Settings")
num_simulations = st.sidebar.slider("Number of Simulations", 1000, 10000, 1000, step=1000)

st.header("Enter Your Hole Cards")
col1, col2 = st.columns(2)
with col1:
    hole_card_1 = st.text_input("Hole Card 1 (e.g., As, Kh, 5d)", key="hole_card_1")
with col2:
    hole_card_2 = st.text_input("Hole Card 2 (e.g., As, Kh, 5d)", key="hole_card_2")

hole_cards = []
if hole_card_1 and hole_card_2:
    card1 = parse_card(hole_card_1)
    card2 = parse_card(hole_card_2)
    if card1 and card2:
        if card1 != card2:
            hole_cards = [card1, card2]
        else:
            st.error("Hole cards cannot be the same.")

st.header("Enter Community Cards")
community_cards_input = st.text_input("Community Cards (Flop, Turn, River)", key="community_cards")

community_cards = []
if community_cards_input:
    community_strs = community_cards_input.strip().split()
    for card_str in community_strs:
        card = parse_card(card_str)
        if card:
            if card not in hole_cards and card not in community_cards:
                community_cards.append(card)
            else:
                st.error(f"Duplicate card detected: {card_str}")

# Determine the stage of the game
if len(community_cards) == 0:
    stage = "Pre-Flop"
elif len(community_cards) == 3:
    stage = "Post-Flop"
elif len(community_cards) == 5:
    stage = "River"
else:
    stage = "Unknown"

if st.button("Get Advice"):
    if len(hole_cards) != 2:
        st.error("Please enter both of your hole cards.")
    else:
        advice = get_advice(hole_cards, community_cards, stage)
        win_prob, tie_prob, loss_prob = calculate_win_prob(
            hole_cards, community_cards, num_simulations=num_simulations
        )
        if win_prob is not None:
            st.markdown(f"<h2 style='color: blue;'>Winning Probability: {win_prob:.2f}%</h2>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: green;'>Advice: {advice}</h2>", unsafe_allow_html=True)
