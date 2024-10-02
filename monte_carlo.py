"""
Monte Carlo for poker version 2
In version 1 we are evaluatin all possible 5 cards combination in individual basis. 
Here in version 2 we are combining the 42 posible combinations into a single evaluation 
to improve the performance.
Version1 average performance: 0.26 seconds per evaluation
Version2 average performance: 0.01 seconds per evaluation
"""
import os
import sys
import itertools
import time
from collections import Counter
import timeit
import random
from datetime import datetime

# Hand rankings in poker from highest to lowest
HAND_RANKS = {
    "Royal Flush": 10,
    "Straight Flush": 9,
    "Four of a Kind": 8,
    "Full House": 7,
    "Flush": 6,
    "Straight": 5,
    "Three of a Kind": 4,
    "Two Pair": 3,
    "One Pair": 2,
    "High Card": 1
}

HAND_RANKS_REVERSE = [
    "High Card",
    "One Pair",
    "Two Pair",
    "Three of a Kind",
    "Straight",
    "Flush",
    "Full House",
    "Four of a Kind",
    "Straight Flush",
    "Royal Flush"
]




# Example card ranks and suits for simulation
VALUES = "23456789TJQKA"
SUITS = "CDHS"  # Clubs, Diamonds, Hearts, Spades
WORST_POSSIBLE_HAND = (1, [6,4,3,2,1])

# Helper functions
def card_value(card):
    """Returns the index of the card's rank."""
    return VALUES.index(card[0])

def is_flush(hand):
    """Returns True if all cards in hand have the same suit."""
    suits = [card[1] for card in hand]
    return len(set(suits)) == 1

def is_flush_full_hand(full_hand):
    """Returns True if all cards in hand have the same suit."""
    suit = Counter([card[1] for card in full_hand]).most_common(1)[0]
    return suit[0], suit[1] >= 5

def is_straight(hand):
    """Returns True if hand is a straight (five consecutive ranks)."""
    ranks = sorted([card_value(card) for card in hand])
    if ranks == [0, 1, 2, 3, 12]:  # Special case for A-2-3-4-5 straight
        return True
    return all(ranks[i] + 1 == ranks[i + 1] for i in range(len(ranks) - 1))

def is_straight_full_hand(full_hand):
    """Returns True if full hand is a straight (five consecutive ranks)."""
    ranks = sorted({card_value(card) for card in full_hand}, reverse=True)
    for i in range(len(ranks) - 4):
        if ranks[i] - ranks[i+4] == 4:
            return ranks[i], True
    if ranks[:1] + ranks[-4:] == [12, 3, 2, 1, 0]: # Special case for A-2-3-4-5
        return 3, True
    return 0, False

def is_straight_flush_hand(flush_hand, color):
    """Returns True if flush hand is a straight (five consecutive ranks)."""
    return is_straight_full_hand([ card for card in flush_hand if card[1] == color])

def count_values(hand):
    """Returns a dictionary with the count of each rank in the hand."""
    values = [card[0] for card in hand]
    return {v: values.count(v) for v in set(values)}

def evaluate_hand(hand):
    """Evaluates a hand of 5 cards and returns the rank of the hand with tiebreaker values."""
    value_count = count_values(hand)
    is_flush_hand = is_flush(hand)
    is_straight_hand = is_straight(hand)
    hand_type = "High Card"
    hand_value = sorted([card_value(card) for card in hand], reverse=True)

    # Helper to extract the ranks in order of frequency and card value
    ranked_values = sorted(value_count.keys(),
                           key=lambda v: (value_count[v], card_value(v)),
                           reverse=True)

    if is_flush_hand and is_straight_hand:
        hand_value = [max(card_value(card) for card in hand)]
        hand_type = "Straight Flush"
        if sorted([card_value(card) for card in hand]) == [8, 9, 10, 11, 12]:
            hand_type = "Royal Flush"

    elif 4 in value_count.values():
        # Four of a Kind: Rank by four-of-a-kind value, then kicker
        four_kind_value = ranked_values[0]  # Four of a kind is the most frequent
        hand_value = [card_value(four_kind_value), card_value(ranked_values[1])]
        hand_type = "Four of a Kind"

    elif 3 in value_count.values() and 2 in value_count.values():
        # Full House: Rank by three-of-a-kind value, then pair value
        three_kind_value = ranked_values[0]  # Three of a kind is the most frequent
        hand_value = [card_value(three_kind_value), card_value(ranked_values[1])]
        hand_type = "Full House"

    elif is_flush_hand:
        # Flush: Rank by card values
        hand_value = sorted([card_value(card) for card in hand], reverse=True)
        hand_type = "Flush"

    elif is_straight_hand:
        # Straight: Rank by the highest card in the straight
        card_values = [card_value(card) for card in hand]
        maxi = max(card_values)
        hand_value = [ maxi if maxi - min(card_values) == 4 else 3 ]
        hand_type = "Straight"

    elif 3 in value_count.values():
        # Three of a Kind: Rank by three-of-a-kind value, then kickers
        three_kind_value = ranked_values[0]
        hand_value = [card_value(three_kind_value)] + [card_value(k) for k in ranked_values[1:3]]
        hand_type = "Three of a Kind"

    elif list(value_count.values()).count(2) == 2:
        # Two Pair: Rank by both pairs, then kicker
        high_pair_value = ranked_values[0]
        low_pair_value = ranked_values[1]
        hand_value = [card_value(high_pair_value),
                      card_value(low_pair_value),
                      card_value(ranked_values[2])]
        hand_type = "Two Pair"

    elif 2 in value_count.values():
        # One Pair: Rank by pair value, then kickers
        pair_value = ranked_values[0]
        kickers = ranked_values[1:4]  # Next three highest kickers
        hand_value = [card_value(pair_value)] + [card_value(k) for k in kickers]
        hand_type = "One Pair"

    # High Card: Rank by individual card values
    return (HAND_RANKS[hand_type], hand_value)

def best_hand(seven_cards):
    """Finds the best possible poker hand from 7 cards."""
    best = WORST_POSSIBLE_HAND
    for combination in itertools.combinations(seven_cards, 5):
        current_hand = evaluate_hand(combination)
        best = max(best, current_hand)
    return best

def evaluate_full_hand(full_hand):
    """Evaluates a hand of 7 cards and returns the rank of the hand with tiebreaker values."""
    value_count = count_values(full_hand)
    flush_color, is_flush_hand = is_flush_full_hand(full_hand)
    top_straight, is_straight_hand = 0, 0
    if is_flush_hand:
        top_straight, is_straight_hand = is_straight_flush_hand(full_hand, flush_color)
    else:
        top_straight, is_straight_hand = is_straight_full_hand(full_hand)
    # High Card: Rank by individual card values
    hand_type = "High Card"
    hand_value = sorted([card_value(card) for card in full_hand], reverse=True)[:5]

    # Helper to extract the ranks in order of frequency and card value
    ranked_values = sorted(value_count.keys(),
                           key=lambda v: (value_count[v], card_value(v)),
                           reverse=True)

    if is_flush_hand and is_straight_hand:
        hand_type = "Royal Flush" if top_straight == 12 else "Straight Flush"
        hand_value = [top_straight]

    elif 4 in value_count.values():
        # Four of a Kind: Rank by four-of-a-kind value, then kicker
        #four_kind_value = ranked_values[0]
        hand_type = "Four of a Kind"
        hand_value = [card_value(ranked_values[0]), max(map(card_value,ranked_values[1:]))]

    elif value_count[ranked_values[0]] == 3 and value_count[ranked_values[1]] >= 2:
        # Full House: Rank by three-of-a-kind value, then pair value
        #three_kind_value = ranked_values[0]
        pair_value = max(card_value(k)
                         for k, v in value_count.items()
                         if v >= 2 and k != ranked_values[0])
        hand_type = "Full House"
        hand_value = [card_value(ranked_values[0]), pair_value]

    elif is_flush_hand:
        # Flush: Rank by card values
        hand_type = "Flush"
        hand_value = sorted([card_value(card) for card in full_hand if card[1] == flush_color],
                            reverse=True)[:5]

    elif is_straight_hand:
        # Straight: Rank by the highest card in the straight
        hand_type = "Straight"
        hand_value = [top_straight]

    elif 3 in value_count.values():
        # Three of a Kind: Rank by three-of-a-kind value, then kickers
        #three_kind_value = ranked_values[0]
        kickers = ranked_values[1:3]  # Next two highest kickers
        hand_type = "Three of a Kind"
        hand_value = [card_value(ranked_values[0])] + [card_value(k) for k in kickers]

    elif list(value_count.values()).count(2) >= 2:
        # Two Pair: Rank by both pairs, then kicker
        #high_pair_value = ranked_values[0]
        #low_pair_value = ranked_values[1]
        kicker = max(map(card_value,ranked_values[2:]))
        hand_type = "Two Pair"
        hand_value = [card_value(ranked_values[0]), card_value(ranked_values[1]), kicker]

    elif 2 in value_count.values():
        # One Pair: Rank by pair value, then kickers
        pair_value = ranked_values[0]
        kickers = ranked_values[1:4]  # Next three highest kickers
        hand_type = "One Pair"
        hand_value = [card_value(pair_value)] + [card_value(k) for k in kickers]

    return (HAND_RANKS[hand_type], hand_value)


def create_deck():
    """ Helper function to create a full deck of cards. """
    ranks = "23456789TJQKA"
    suits = "CDHS"  # Clubs, Diamonds, Hearts, Spades
    return [rank + suit for rank in ranks for suit in suits]

def create_community_cards():
    """Generate a community_cards, any 5 cards combination from the deck.
    Output: community_cards (five cards), where any card in the hand is a 2 caracter string."""
    deck = create_deck()
    hand = random.sample(deck, 5)
    return hand

def player_hand(community_cards):
    """Generate a hand, any 2 cards combination from the deck excluding the community_cards.
    Output: Hand (two cards), where any card in the hand is a 2 caracter string."""
    deck = create_deck()
    remaining_deck = [card for card in deck if card not in community_cards]
    hand = random.sample(remaining_deck, 2)
    return hand

def all_possible_hands(community_cards, number_of_hands=None, repeated=False):
    """Generate number_of_hands for possible players, by default generate all possible hand 
    combinartions 47!/(2!*45!). Output: list of hands (two cards), where any card in the hand 
    is a 2 caracter string."""
    # Create the full deck of cards
    deck = create_deck()
    # Remove the cards that are already in the common hand
    remaining_deck = [card for card in deck if card not in community_cards]
    if repeated:
        # Generate all possible 2-card combinations from the remaining deck
        possible_hands = list(itertools.combinations(remaining_deck, 2))
        random.shuffle(possible_hands)
        if number_of_hands is None:
            return possible_hands
        return possible_hands[:number_of_hands]

    if number_of_hands is None:
        number_of_hands = 9
    flat_hand_list = random.sample(remaining_deck, number_of_hands*2)
    possible_hands = []
    for i in range(number_of_hands):
        possible_hands.append((flat_hand_list[2*i], flat_hand_list[2*i+1]))
    return possible_hands

def best_possible_hand(community_cards, number_of_hands=None ):
    """Evaluate the best movement against with community cards for number_of_hands players 
    generated. Output: Best possible hand and its result given the generated hands"""
    best_hand_result = WORST_POSSIBLE_HAND
    best_pair = None
    possible_hands = all_possible_hands(community_cards, number_of_hands)
    #print(possible_hands)

    for hand in possible_hands:
        # Combine the pair with the 5 community cards to form a 7-card hand
        seven_card_hand = community_cards + list(hand)
        # Evaluate the best hand for this 7-card hand
        current_hand = evaluate_full_hand(seven_card_hand)
        # Update the best hand result if the current hand is better
        if current_hand > best_hand_result:
            best_hand_result = current_hand
            best_pair = hand
    return best_pair, best_hand_result

def monte_carlo_training(n=10000, number_of_hands=None):
    """monte_carlo_training method. generate n simulations with number_of_hands players and print 
    the results. output: common cards, winner hand, hand result, execution time"""
    i=n
    while i>0:
        i -= 1
        start_time = time.time()
        community_cards = create_community_cards()
        hand, hand_result = best_possible_hand(community_cards, number_of_hands)
        end_time = time.time()
        execution_time = end_time - start_time
        print(",".join(community_cards),
              ",".join(hand), hand_result[0],
              ",".join(map(str,hand_result[1])),
              execution_time,
              sep="|")

### data collections

def data_collection():
    """Save a file with simulations results."""
    print(sys.argv, len(sys.argv) < 2, len(sys.argv) < 3)
    simulations = 5 if len(sys.argv) < 2 else int(sys.argv[1])
    num_of_hands = 1081 if len(sys.argv) < 3 else int(sys.argv[2])
    file_identifier = "all" if num_of_hands >= 1000 else str(num_of_hands) + "hands"
    time_format = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Running {simulations} simulations with {num_of_hands} num_of_hands at {time_format}.")
    print("file_identifier: {file_identifier}.")
    file_path = os.getenv("POKER_OUT_FILE_PATH", "")

    file_name = f"{file_path}poker_monte_carlo_{simulations}_{file_identifier}_{time_format}.csv"
    print("file_name:", file_name)
    with open(file_name, "w", encoding="utf-8") as file:
        sys.stdout = file
        print("community_cards|hand|hand_result_1|hand_result_2|execution_time")
        monte_carlo_training(simulations, num_of_hands)
        sys.stdout = sys.__stdout__

###Testing###

def full_test():
    """Automated full testing."""
    tc2_methods_comparizon()
    tc3_validate_distinct_hands()

def tc3_validate_distinct_hands(number_of_siluations=100):
    """Evaluate that all hands given by  against evaluate_full_hand. The results should be the same
    in all cases. No output"""
    for _ in range(number_of_siluations):
        community_cards = create_community_cards()
        possible_hands = all_possible_hands(community_cards, 9)
        set_cards = set()
        for hand in possible_hands:
            set_cards.add(hand[0])
            set_cards.add(hand[1])
        print("set_cards:", set_cards)
        assert len(set_cards) == 18, f"duplicated cards in {possible_hands}"

def tc2_methods_comparizon(number_of_siluations=100):
    """Evaluate best_hand against evaluate_full_hand. The results should be the same
    in all cases. No output"""
    for _ in range(number_of_siluations):
        community_cards = create_community_cards()
        #print(f"community_cards: {community_cards}")
        player_hand1 = player_hand(community_cards)
        #print(f"player_hand: {player_hand}")
        seven_cards = community_cards + player_hand1
        print(f"seven_cards: {seven_cards}", end = " ")
        best = best_hand(seven_cards)
        best2 = evaluate_full_hand(seven_cards)
        print(f"best: {best} and {best2}")
        assert best == best2, "different expressions"

def tc1_simple_hand_usage():
    """tc1 to validate the usage of basic methods created."""
    community_cards = create_community_cards()
    print(f"community_cards: {community_cards}")
    player_hand_1 = player_hand(community_cards)
    print(f"player_hand: {player_hand}")
    seven_cards = community_cards + player_hand_1
    print(f"seven_cards: {seven_cards}")
    best = best_hand(seven_cards)
    print(f"best: {best}")
    best = evaluate_full_hand(seven_cards)
    print(f"best2: {best}")

    #Example to validate print and performance
    community_cards = create_community_cards()
    print(f"community_cards: {community_cards}")
    start_time = time.time()
    best = best_possible_hand(community_cards)
    end_time = time.time()
    print(f"Best Hand: {best[0]} with cards: {best[1]}, {HAND_RANKS_REVERSE[best[1][0]]}")
    execution_time = end_time - start_time
    print(f"Execution Time: {execution_time} seconds")

    execution_time = timeit.timeit("best_possible_hand(community_cards)",
        globals=globals(), number=10)
    print(f"Average Execution Time: {execution_time / 10} seconds")

    monte_carlo_training(1, 2)


if __name__ == "__main__":
    #full_test()
    data_collection()
