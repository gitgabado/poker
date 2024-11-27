import streamlit as st
from treys import Card, Evaluator, Deck
import random
import re

# Function to parse card input
def parse_card(card_str):
    rank_map = {
        '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
        '10': 'T', 't': 'T', 'ten': 'T', 'j': 'J', 'jack': 'J', 'q': 'Q', 'queen': 'Q',
        'k': 'K', 'king': 'K', 'a': 'A', 'ace': 'A'
    }
    suit_map = {
        's': 's', 'spades': 's', '♠': 's', 'h': 'h', 'hearts': 'h', '♥': 'h',
        'd': 'd', 'diamonds': 'd', '♦': 'd', 'c': 'c', 'clubs': 'c', '♣': 'c'
    }

    card_str = card_str.strip().lower().replace(' ', '')
    rank_pattern = '|'.join(sorted(rank_map.keys(), key=lambda x: -len(x)))
    suit_pattern = '|'.join(sorted(suit_map.keys(), key=lambda x: -len(x)))

    pattern = f'^({rank_pattern})({suit_pattern})$'
    match = re.match(pattern, card_str)
    if match:
        rank_input = match.group(1)
        suit_input = match.group(2)
        rank = rank_map.get(rank_input)
        suit = suit_map.get(suit_input)
        if rank and suit:
            return Card.new(rank + suit)
    st.error(f"Invalid card input: {card_str}")
    return None

# Function to calculate winning probability
def calculate_win_prob(hole_cards, community_cards, num_opponents=1, num_simulations=1000):
    evaluator = Evaluator()
    wins, ties, losses = 0, 0, 0
    known_cards = hole_cards + community_cards

    for _ in range(num_simulations):
        deck = Deck()
        for card in known_cards:
            if card in deck.cards:
                deck.cards.remove(card)
        random.shuffle(deck.cards)

        opponents_hole_cards = [deck.draw(2) for _ in range(num_opponents)]
        current_community = community_cards[:]
        if len(current_community) < 5:
            current_community += deck.draw(5 - len(current_community))

        player_score = evaluator.evaluate(hole_cards, current_community)
        opponent_scores = [evaluator.evaluate(opp_hole, current_community) for opp_hole in opponents_hole_cards]

        if any(opp_score < player_score for opp_score in opponent_scores):
            losses += 1
        elif any(opp_score == player_score for opp_score in opponent_scores):
            ties += 1
        else:
            wins += 1

    total = wins + ties + losses
    return (wins / total) * 100, (ties / total) * 100, (losses / total) * 100

# Initialize session state variables
def reset_inputs():
    st.session_state['hole_card_1'] = ''
    st.session_state['hole_card_2'] = ''
    st.session_state['community_cards'] = ''
    st.session_state['chart_data'] = None

if 'chart_data' not in st.session_state:
    reset_inputs()

# Streamlit UI
st.title("♠️ Texas Hold'em Advisory App ♠️")
st.markdown("#### Analyze your winning probabilities with ease!")

st.sidebar.header("Game Settings")
num_opponents = st.sidebar.slider("Number of Opponents", 1, 8, 1)
num_simulations = st.sidebar.slider("Number of Simulations", 1000, 10000, 1000, step=1000)

st.header("Enter Your Hole Cards")
hole_card_1 = st.selectbox("Hole Card 1:", ["", "As", "Ah", "Ad", "Ac", "Ks", "Kh", "Kd", "Kc", "2s", "2h", "2d", "2c"], key="hole_card_1")
hole_card_2 = st.selectbox("Hole Card 2:", ["", "As", "Ah", "Ad", "Ac", "Ks", "Kh", "Kd", "Kc", "2s", "2h", "2d", "2c"], key="hole_card_2")

st.header("Enter Community Cards")
community_cards_input = st.text_area("Community Cards (e.g., Flop+Turn+River)", key="community_cards")

hole_cards = []
if hole_card_1 and hole_card_2:
    card1 = parse_card(hole_card_1)
    card2 = parse_card(hole_card_2)
    if card1 and card2 and card1 != card2:
        hole_cards = [card1, card2]
    else:
        st.error("Hole cards cannot be the same.")

community_cards = []
if community_cards_input:
    for card_str in community_cards_input.strip().split():
        card = parse_card(card_str)
        if card and card not in hole_cards:
            community_cards.append(card)
        else:
            st.error(f"Invalid or duplicate card: {card_str}")

# Buttons and actions
col1, col2 = st.columns(2)
with col1:
    if st.button("Calculate Winning Probability"):
        if len(hole_cards) == 2:
            win_prob, tie_prob, loss_prob = calculate_win_prob(hole_cards, community_cards, num_opponents, num_simulations)
            st.session_state['chart_data'] = {
                "Win": win_prob,
                "Tie": tie_prob,
                "Lose": loss_prob
            }
        else:
            st.error("Please select valid hole cards.")

with col2:
    if st.button("Reset"):
        reset_inputs()

# Display results
if st.session_state['chart_data']:
    st.subheader("Winning Probability:")
    st.write(f"**Win:** {st.session_state['chart_data']['Win']:.2f}%")
    st.write(f"**Tie:** {st.session_state['chart_data']['Tie']:.2f}%")
    st.write(f"**Lose:** {st.session_state['chart_data']['Lose']:.2f}%")

    st.bar_chart({
        "Win": [st.session_state['chart_data']['Win']],
        "Tie": [st.session_state['chart_data']['Tie']],
        "Lose": [st.session_state['chart_data']['Lose']]
    })
