import streamlit as st
from treys import Evaluator, Card, Deck
import itertools

def convert_card_input(card_str):
    # Map suits and ranks to correct treys representation
    rank_map = {'2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', 'T': 'T', 'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A'}
    suit_map = {'S': 's', 'H': 'h', 'D': 'd', 'C': 'c'}
    
    rank = card_str[0].upper()
    suit = card_str[1].upper()
    
    if rank in rank_map and suit in suit_map:
        return Card.new(rank_map[rank] + suit_map[suit])
    else:
        raise ValueError(f"Invalid card input: {card_str}")

def calculate_win_probability(current_hand, community_cards):
    try:
        # Convert input strings into lists of cards
        current_hand = [convert_card_input(card.strip()) for card in current_hand.split(',')]
        community_cards = [convert_card_input(card.strip()) for card in community_cards.split(',') if card.strip()]
    except ValueError as e:
        st.error(str(e))
        return
    
    evaluator = Evaluator()
    deck = Deck()
    for card in current_hand + community_cards:
        deck.cards.remove(card)

    win, tie, total = 0, 0, 0

    # Iterate over all possible opponent hands using remaining cards
    remaining_cards = deck.cards
    opponent_combinations = itertools.combinations(remaining_cards, 2)

    for opponent_hand in opponent_combinations:
        total += 1
        opponent_score = evaluator.evaluate(community_cards, list(opponent_hand))
        my_score = evaluator.evaluate(community_cards, current_hand)

        if my_score < opponent_score:
            win += 1
        elif my_score == opponent_score:
            tie += 1

    if total > 0:
        win_probability = (win + tie / 2) / total * 100
    else:
        win_probability = 0

    st.write(f"Winning Probability: {win_probability:.2f}%")
    return win_probability

# Streamlit app interface
st.title("Poker Learning App")
st.header("Learn Poker with Winning Probability at Flop, Turn, and River")

# Input section
current_hand = st.text_input("Enter your pocket cards (e.g., AH, KH)")
community_cards = st.text_input("Enter community cards (e.g., 7S, 2H, 9C) - Add more at each stage")

calculate_button = st.button("Calculate Winning Probability")

if calculate_button:
    # Calculate win probability
    calculate_win_probability(current_hand, community_cards)

# Explanation
st.markdown("---")
st.header("How to use this App")
st.write("""
- Enter your pocket cards initially to see the winning probability.
- Add community cards as they appear at flop, turn, and river to see updated probabilities.
""")

