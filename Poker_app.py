import streamlit as st
from treys import Evaluator, Card, Deck
from itertools import combinations


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

    win, tie, total = 0, 0, 0

    # Enumerate all possible opponent hands
    opponent_hands = list(combinations(deck.cards, 2))
    for opponent_hand in opponent_hands:
        my_score = evaluator.evaluate(community_cards + current_hand, [])
        opponent_score = evaluator.evaluate(community_cards + list(opponent_hand), [])

        if my_score < opponent_score:
            win += 1
        elif my_score == opponent_score:
            tie += 1
        total += 1

    if total > 0:
        win_probability = (win + tie / 2) / total * 100
    else:
        win_probability = 0

    st.markdown(f"<h2 style='color: #ff6347;'><b>Winning Probability: {win_probability:.2f}%</b></h2>", unsafe_allow_html=True)

    # Provide advice based on winning probability
    if len(community_cards) == 0:  # Pre-flop
        if win_probability >= 75:  # Increase threshold as pocket Aces are very strong
            st.markdown("<h3 style='color: #ffa500;'><b>Advice: Consider making a 4x raise. Pocket Aces or Kings are extremely strong!</b></h3>", unsafe_allow_html=True)
        elif 55 <= win_probability < 75:
            st.markdown("<h3 style='color: #ffa500;'><b>Advice: Consider making a 3x raise.</b></h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='color: #ffa500;'><b>Advice: It might be better to check.</b></h3>", unsafe_allow_html=True)
    elif len(community_cards) == 3:  # Flop
        if win_probability >= 65:
            st.markdown("<h3 style='color: #ffa500;'><b>Advice: Consider making a 2x raise.</b></h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='color: #ffa500;'><b>Advice: It might be better to check.</b></h3>", unsafe_allow_html=True)
    elif len(community_cards) in [4, 5]:  # Turn or River
        if win_probability >= 55:
            st.markdown("<h3 style='color: #ffa500;'><b>Advice: Consider calling.</b></h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='color: #ffa500;'><b>Advice: It might be better to fold.</b></h3>", unsafe_allow_html=True)
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
