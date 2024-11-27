# File name: texas_holdem_advisor.py

import streamlit as st
from treys import Card, Evaluator, Deck
import random
import re

# Function to parse card input (unchanged)
def parse_card(card_str):
    # [Function code remains the same]
    # ...

# Function to calculate winning probability (unchanged)
def calculate_win_prob(hole_cards, community_cards, num_opponents=1, num_simulations=1000):
    # [Function code remains the same]
    # ...

# Function to reset input fields
def reset_inputs():
    st.session_state['hole_card_1'] = ''
    st.session_state['hole_card_2'] = ''
    st.session_state['community_cards'] = ''

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
    hole_card_1 = st.text_input(
        "Hole Card 1 (e.g., As, Kh, 5d)",
        key="hole_card_1",
        value=st.session_state['hole_card_1']
    )
with col2:
    hole_card_2 = st.text_input(
        "Hole Card 2 (e.g., As, Kh, 5d)",
        key="hole_card_2",
        value=st.session_state['hole_card_2']
    )

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
community_cards_input = st.text_input(
    "Community Cards (e.g., Flop or Flop+Turn+River)",
    key="community_cards",
    value=st.session_state['community_cards']
)

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

# Buttons
col1, col2 = st.columns(2)
with col1:
    calculate = st.button("Calculate Winning Probability")
with col2:
    reset = st.button("Reset", on_click=reset_inputs)

if calculate:
    if len(hole_cards) != 2:
        st.error("Please enter both of your hole cards.")
    else:
        result = calculate_win_prob(
            hole_cards,
            community_cards,
            num_opponents=num_opponents,
            num_simulations=num_simulations
        )
        if result[0] is not None:
            win_prob, tie_prob, loss_prob = result
            st.subheader("Winning Probability:")
            st.write(f"**Win:** {win_prob:.2f}%")
            st.write(f"**Tie:** {tie_prob:.2f}%")
            st.write(f"**Lose:** {loss_prob:.2f}%")
