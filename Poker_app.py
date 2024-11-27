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

def calculate_win_probability(current_hand, community_cards):
    try:
        # Convert input strings into lists of cards
        current_hand = [convert_card_input(card.strip()) for card in current_hand.split(',')]
        community_cards = [convert_card_input(card.strip()) for card in community_cards.split(',') if card.strip()]
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

    if len(community_cards)
