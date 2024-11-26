import streamlit as st
from collections import Counter

def calculate_outs(current_hand, community_cards):
    # Convert input strings into lists of cards
    current_hand = current_hand.split(',')
    community_cards = community_cards.split(',')
    all_known_cards = current_hand + community_cards
    # The full deck without the known cards
    full_deck = [
        rank + suit
        for rank in '23456789TJQKA'
        for suit in 'CDHS'
    ]
    remaining_deck = [card for card in full_deck if card not in all_known_cards]
    # Count how many cards of each rank are present
    ranks = [card[0] for card in all_known_cards]
    rank_counts = Counter(ranks)
    outs = 0
    for card in remaining_deck:
        rank = card[0]
        if rank_counts[rank] == 1:  # Looking for pairs
            outs += 1
        elif rank_counts[rank] == 2:  # Looking for sets/trips
            outs += 1
    st.write(f"Current outs: {outs}")
    return outs

def calculate_odds(outs, unseen_cards):
    if unseen_cards == 0:
        return 0
    odds = (outs / unseen_cards) * 100
    st.write(f"Odds of improving your hand: {odds:.2f}%")
    return odds

def calculate_pot_odds(pot_size, bet_size):
    if (pot_size + bet_size) == 0:
        return 0
    pot_odds = (bet_size / (pot_size + bet_size)) * 100
    st.write(f"Pot odds: {pot_odds:.2f}%")
    return pot_odds

def should_you_call(odds, pot_odds):
    if odds > pot_odds:
        st.success("You should call!")
    else:
        st.error("You should fold!")

# Streamlit app interface
st.title("Poker Learning App")
st.header("Learn Poker with Outs, Odds, and Pot Odds")

# Input section
current_hand = st.text_input("Enter your current hand (e.g., AH, KH)")
community_cards = st.text_input("Enter community cards (e.g., 7S, 2H, 9C)")

pot_size = st.number_input("Enter the current pot size", min_value=0, step=10)
bet_size = st.number_input("Enter the current bet size", min_value=0, step=10)

calculate_button = st.button("Calculate Outs, Odds, and Decision")

if calculate_button:
    # A simplified logic to show the sequence
    outs = calculate_outs(current_hand, community_cards)
    odds = calculate_odds(outs, 47 - len(community_cards) - len(current_hand))  # 52 cards - known cards
    pot_odds = calculate_pot_odds(pot_size, bet_size)
    should_you_call(odds, pot_odds)

# Explanation
st.markdown("---")
st.header("How to use this App")
st.write("""
- **Outs** are the number of cards that will improve your hand.
- **Odds** are the probability of hitting one of your outs.
- **Pot odds** represent the ratio of the current pot size to the cost of a contemplated call.
- **Decision** on whether to call is based on comparing the odds to pot odds.
""")
