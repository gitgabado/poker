import streamlit as st
from treys import Evaluator, Card, Deck

def calculate_win_probability(current_hand, community_cards):
    # Convert input strings into lists of cards
    current_hand = [Card.new(card.strip()) for card in current_hand.split(',')]
    community_cards = [Card.new(card.strip()) for card in community_cards.split(',') if card.strip()]
    evaluator = Evaluator()
    deck = Deck()
    for card in current_hand + community_cards:
        deck.cards.remove(card)

    win, tie, total = 0, 0, 0

    # Iterate over remaining cards to simulate all possible opponent hands
    for opponent_hand in deck.draw(2):
        total += 1
        opponent_score = evaluator.evaluate(community_cards, opponent_hand)
        my_score = evaluator.evaluate(community_cards, current_hand)

        if my_score < opponent_score:
            win += 1
        elif my_score == opponent_score:
            tie += 1

    win_probability = (win + tie / 2) / total * 100
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
