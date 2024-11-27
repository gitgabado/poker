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
def calculate_win_prob(hole_cards, community_cards, num_opponents=1, num_simulations=10000):
    evaluator = Evaluator()
    wins = 0
    ties = 0
    losses = 0

    # Prepare deck
    deck = Deck()
    for card in hole_cards + community_cards:
        if card in deck.cards:
            deck.cards.remove(card)

    for _ in range(num_simulations):
        deck.shuffle()

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
        opponent_wins = False
        tie = False
        for opp_hole in opponents_hole_cards:
            opp_score = evaluator.evaluate(opp_hole, current_community)
            if opp_score < player_score:
                opponent_wins = True
                break
            elif opp_score == player_score:
                tie = True

        if opponent_wins:
            losses += 1
        elif tie:
            ties += 1
        else:
            wins += 1

        # Return cards to deck
        deck.cards.extend([card for opp_hole in opponents_hole_cards for card in opp_hole])
        deck.cards.extend(current_community[len(community_cards):])

    total = wins + ties + losses
    win_prob = (wins / total) * 100
    tie_prob = (ties / total) * 100
    loss_prob = (losses / total) * 100

    return win_prob, tie_prob, loss_prob

# Streamlit UI
st.title("♠️ Texas Hold'em Advisory App ♠️")

st.sidebar.header("Game Settings")
num_opponents = st.sidebar.slider("Number of Opponents", 1, 8, 1)

st.header("Enter Your Hole Cards")
col1, col2 = st.columns(2)
with col1:
    hole_card_1 = st.text_input("Hole Card 1 (e.g., As, Kh, 5d)")
with col2:
    hole_card_2 = st.text_input("Hole Card 2 (e.g., As, Kh, 5d)")

hole_cards = []
if hole_card_1 and hole_card_2:
    card1 = parse_card(hole_card_1.strip())
    card2 = parse_card(hole_card_2.strip())
    if card1 and card2:
        hole_cards = [card1, card2]

st.header("Enter Community Cards")
community_cards_input = st.text_input("Community Cards (e.g., Flop or Flop+Turn+River)")

community_cards = []
if community_cards_input:
    community_strs = community_cards_input.strip().split()
    for card_str in community_strs:
        card = parse_card(card_str)
        if card:
            community_cards.append(card)

if st.button("Calculate Winning Probability"):
    if len(hole_cards) != 2:
        st.error("Please enter both of your hole cards.")
    else:
        win_prob, tie_prob, loss_prob = calculate_win_prob(
            hole_cards, community_cards, num_opponents=num_opponents
        )
        st.subheader("Winning Probability:")
        st.write(f"**Win:** {win_prob:.2f}%")
        st.write(f"**Tie:** {tie_prob:.2f}%")
        st.write(f"**Lose:** {loss_prob:.2f}%")
