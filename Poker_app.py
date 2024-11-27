import streamlit as st
from treys import Evaluator, Card, Deck
import itertools
import random

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

def calculate_win_probability(current_hand, community_cards, use_fixed_seed=False):
    try:
        # Convert input strings into lists of cards
        current_hand = [convert_card_input(card.strip().upper()) for card in current_hand.replace(',', '').replace(' ', '').split() if card.strip()]
        community_cards = [convert_card_input(card.strip().upper()) for card in community_cards.replace(',', '').replace(' ', '').split() if card.strip()]
    except ValueError as e:
        st.error(str(e))
        return
    
    # Check for duplicate cards between pocket and community
    all_cards = current_hand + community_cards
    if len(all_cards) != len(set(all_cards)):
        st.error("Duplicate cards detected between pocket cards and community cards. Please enter unique cards.")
        return

    evaluator = Evaluator()
    deck = Deck()
    for card in all_cards:
        if card in deck.cards:
            deck.cards.remove(card)

    if use_fixed_seed:
        random.seed(12345)  # Fix the seed to ensure consistent results

    if len(community_cards) < 5:  # Not enough community cards for evaluation
        win, tie, total = 0, 0, 0
        num_simulations = 10000  # Increased number of simulations to get more consistent results

        for _ in range(num_simulations):
            # Draw remaining community cards (up to 5 cards)
            simulated_community = community_cards[:]
            simulated_community += deck.draw(5 - len(community_cards))

            # Draw opponent hand
            remaining_cards = [card for card in deck.cards if card not in simulated_community]
            opponent_hand = random.sample(remaining_cards, 2)

            # Evaluate hands
            my_score = evaluator.evaluate(simulated_community, current_hand)
            opponent_score = evaluator.evaluate(simulated_community, opponent_hand)

            if my_score < opponent_score:
                win += 1
            elif my_score == opponent_score:
                tie += 1

            # Return cards back to deck
            deck = Deck()
            for card in all_cards:
                if card in deck.cards:
                    deck.cards.remove(card)

        if num_simulations > 0:
            win_probability = (win + tie / 2) / num_simulations * 100
        else:
            win_probability = 0

    else:  # Full board available, evaluate against all possible dealer hands
        win, tie, total = 0, 0, 0

        # Iterate over all possible dealer hands using remaining cards
        remaining_cards = deck.cards
        opponent_combinations = itertools.combinations(remaining_cards, 2)

        for opponent_hand in opponent_combinations:
            total += 1
            all_community_cards = community_cards[:]
            my_score = evaluator.evaluate(all_community_cards, current_hand)
            opponent_score = evaluator.evaluate(all_community_cards, list(opponent_hand))

            if my_score < opponent_score:
                win += 1
            elif my_score == opponent_score:
                tie += 1

        if total > 0:
            win_probability = (win + tie / 2) / total * 100
        else:
            win_probability = 0

    st.markdown(f"<h2 style='color: #ff6347;'><b>Winning Probability: {win_probability:.2f}%</b></h2>", unsafe_allow_html=True)

    # Provide advice based on winning probability
    if len(community_cards) == 0:  # Pre-flop
        if win_probability >= 65:
            st.markdown(f"<h3 style='color: #ffa500;'><b>Advice: Consider making a 4x raise.</b></h3>", unsafe_allow_html=True)
        elif 50 <= win_probability < 65:
            st.markdown(f"<h3 style='color: #ffa500;'><b>Advice: Consider making a 3x raise.</b></h3>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h3 style='color: #ffa500;'><b>Advice: It might be better to check.</b></h3>", unsafe_allow_html=True)
    elif len(community_cards) == 3:  # Flop
        if win_probability >= 50:
            st.markdown(f"<h3 style='color: #ffa500;'><b>Advice: Consider making a 2x raise.</b></h3>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h3 style='color: #ffa500;'><b>Advice: It might be better to check.</b></h3>", unsafe_allow_html=True)
    elif len(community_cards) in [4, 5]:  # Turn or River
        if win_probability >= 50:
            st.markdown(f"<h3 style='color: #ffa500;'><b>Advice: Consider calling.</b></h3>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h3 style='color: #ffa500;'><b>Advice: It might be better to fold.</b></h3>", unsafe_allow_html=True)
    return win_probability

# Streamlit app interface
st.title("Poker Learning App - Ultimate Texas Hold'em")
st.header("Learn Poker with Winning Probability at Flop, Turn, and River")

# Initialize session state for input fields if not already done
if 'current_hand' not in st.session_state:
    st.session_state.current_hand = ""
if 'community_cards' not in st.session_state:
    st.session_state.community_cards = ""

# Input section
current_hand = st.text_input("Enter your pocket cards (e.g., AH, KH)", value=st.session_state.current_hand, key="current_hand")
community_cards = st.text_input("Enter community cards (e.g., 7S, 2H, 9C) - Add more at each stage", value=st.session_state.community_cards, key="community_cards")
use_fixed_seed = st.checkbox("Use Fixed Random Seed for Consistent Results", value=True)

calculate_button = st.button("Calculate Winning Probability")

def reset_cards():
    st.session_state.current_hand = ""
    st.session_state.community_cards = ""

reset_button = st.button("Reset Cards", on_click=reset_cards)

if calculate_button:
    # Calculate win probability
    calculate_win_probability(current_hand, community_cards, use_fixed_seed)

# Explanation
st.markdown("---")
st.header("How to use this App")
st.write("""
- Enter your pocket cards initially to see the winning probability.
- Add community cards as they appear at flop, turn, and river to see updated probabilities.
- The app will provide advice based on the winning probability and current stage.
- Note: This advice is tailored for Ultimate Texas Hold'em, which is a dealer vs. player game.
- You can use the "Reset Cards" button to quickly enter new pocket cards for a new round.
- To get consistent results across multiple runs, you can enable the "Use Fixed Random Seed" checkbox.
""")
