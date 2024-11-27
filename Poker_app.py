# File name: texas_holdem_advisor.py

import streamlit as st
from treys import Card, Evaluator, Deck
import random

# Function to parse card input
def parse_card(card_str):
    try:
        return Card.new(card_str)
    except:
        st.error(f"Invalid card input: {card_str}")
        return None

# Function to calculate winning probability
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

# Streamlit UI
st.title("♠️ Texas Hold'em Advisory App ♠️")

st.sidebar.header("Game Settings")
num_opponents = st.sidebar.slider("Number of Opponents", 1, 8, 1)
num_simulations = st.sidebar.slider("Number of Simulations", 1000, 10000, 1000, step=1000)

st.header("Enter Your Hole Cards")
col1, col2 = st.columns(2)
with col1:
    hole_card_1 = st.text_input("Hole Card 1 (e.g., As, Kh, 5d)", key="hole_card_1")
with col2:
    hole_card_2 = st.text_input("Hole Card 2 (e.g., As, Kh, 5d)", key="hole_card_2")

hole_cards = []
if hole_card_1 and hole_card_2:
    card1 = parse_card(hole_card_1.strip())
    card2 = parse_card(hole_card_2.strip())
    if card1 and card2:
        if card1 != card2:
            hole_cards = [card1, card2]
        else:
            st.error("Hole cards cannot be the same.")

st.header("Enter Community Cards")
community_cards_input = st.text_input("Community Cards (e.g., Flop or Flop+Turn+River)", key="community_cards")

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

if st.button("Calculate Winning Probability"):
    if len(hole_cards) != 2:
        st.error("Please enter both of your hole cards.")
    else:
        result = calculate_win_prob(
            hole_cards, community_cards, num_opponents=num_opponents, num_simulations=num_simulations
        )
        if result[0] is not None:
            win_prob, tie_prob, loss_prob = result
            st.subheader("Winning Probability:")
            st.write(f"**Win:** {win_prob:.2f}%")
            st.write(f"**Tie:** {tie_prob:.2f}%")
            st.write(f"**Lose:** {loss_prob:.2f}%")
