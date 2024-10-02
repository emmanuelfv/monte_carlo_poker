"""
data_science.py. script to fetch the data from files and to produce analisys and reports.
Current activities:
    split winner hands and provide a matris of result with coicidences and probabilities
"""

from collections import Counter
VALUES = "23456789TJQKA"
INVERSE_VALUES = VALUES[::-1]
P_CASES = 6
S_CASES = 4
N_CASES = 12

def card_rank(card):
    """helper function to rank the cards for sorting purposes"""
    order = {'2': 0, '3': 1, '4': 2,
             '5': 3, '6': 4, '7': 5,
             '8': 6, '9': 7, 'T': 8,
             'J': 9, 'Q': 10,
             'K': 11, 'A': 12}
    return order[card[0]]

def classify_hand(cards):
    """Function to process the second field and classify the pairings"""
    sorted_cards = sorted(cards, key=card_rank)
    ranks = [card[0] for card in sorted_cards]
    suits = [card[1] for card in sorted_cards]
    if ranks[0] == ranks[1]:
        return ranks[0] + ranks[0] + 'P'
    if suits[0] == suits[1]:
        return ''.join(ranks) + 'S'
    return ''.join(ranks) + 'N'

def process_file(file_path):
    """Function to process the file"""
    result = []
    with open(file_path, 'r', encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            fields = line.split('|')
            if fields[1] == "hand":
                continue
            second_field = fields[1].split(',')
            classification = classify_hand(second_field)
            result.append(classification)
    return result

def generate_matrices(win_counter):
    """Function to generate matrices"""
    o_coincidence_matrix = [[None for _ in range(len(VALUES))] for _ in range(len(VALUES))]
    o_probability_matrix = [[None for _ in range(len(VALUES))] for _ in range(len(VALUES))]
    num_simulations = sum(item[1] for item in win_counter.most_common(len(win_counter)))
    cases = 1
    for key, value in win_counter.items():
        row_rank, col_rank = "", ""
        if key[2] == "P":
            row_rank = key[0]
            col_rank = key[1]
            cases = P_CASES
        elif key[2] == "S":
            row_rank = key[1]
            col_rank = key[0]
            cases = S_CASES
        else:
            row_rank = key[0]
            col_rank = key[1]
            cases = N_CASES
        row_idx = INVERSE_VALUES.index(row_rank)
        col_idx = INVERSE_VALUES.index(col_rank)
        o_coincidence_matrix[row_idx][col_idx] = value
        o_probability_matrix[row_idx][col_idx] = 100*value/(cases*num_simulations)
    return o_coincidence_matrix, o_probability_matrix

def print_matrix(matrix, threshold=0):
    """Function to print matrices. Threshold is used to set values with low posibility to 0."""

    all_values = [value for row in matrix for value in row if value is not None]
    min_val, max_val = 0, max(all_values)

    def get_grayscale(value):
        """get_grayscale function to set colors based on the value."""

        if value is None:
            return "\033[0m"
        normalized = (value - min_val) / (max_val - min_val) if max_val != min_val else 0
        grayscale_level = int(normalized * 255)
        return f"\033[38;2;0;{max(100-grayscale_level,0)};{grayscale_level}m"

    max_width = 1
    for row in matrix:
        for value in row:
            if value is not None:
                value_lenght = len(f'{value}') if isinstance(value, int) else len(f'{value:.4f}')
                max_width = max(max_width, value_lenght)

    print('  ' + ' '.join(f'{rank:>{max_width+1}}' for rank in INVERSE_VALUES))
    for i, rank in enumerate(INVERSE_VALUES):
        row = []
        for j in range(len(INVERSE_VALUES)):
            value = matrix[i][j]
            if value < threshold:
                value = 0
            color_code = get_grayscale(value)
            if value is None:
                row.append(f'{"":>{max_width}}')
            elif isinstance(value, int):
                row.append(f'{color_code}{value:>{max_width}}\033[0m')
            else:
                if value < threshold:
                    value = 0
                row.append(f'{color_code}{value:>{max_width}.4f}\033[0m')

        # Print each row with rank labels
        print(f'{rank}  ' + '  '.join(row))
    print("\n\n")

if __name__ == "__main__":
    #files created evaluating all the hand combinations
    file_list = [
    "poker_monte_carlo_1727515339.1416242.csv",
    "poker_monte_carlo_1727517452.8591456.csv",
    "poker_monte_carlo_1727517793.1466877.csv",
    "poker_monte_carlo_1727518170.7944028.csv",
    "poker_monte_carlo_1727518363.9386613.csv"
    ]

    file_list_9 = [
    "poker_monte_carlo_9hands1727521142.7800896.csv"
    ]

    file_list_9_long = [
    "poker_monte_carlo_30000000_9hands1727522804.684028.csv"
    ]

    file_list_3_long = [
    "poker_monte_carlo_100000000_3hands_20240928_105040.csv"
    ]

    winner_counter = Counter()
    for file_name in file_list_3_long:
        winner_counter += Counter(process_file(file_name))
        print(winner_counter)
        simulations_read = sum(item[1] for item in winner_counter.most_common(len(winner_counter)))
        print(len(winner_counter), simulations_read)

    coincidence_matrix, probability_matrix = generate_matrices(winner_counter)
    print_matrix(coincidence_matrix)
    print_matrix(probability_matrix, 0.1)
    print_matrix(probability_matrix, 0.085)
    print_matrix(probability_matrix, 0.0)
    #print_matrix_percentage(matrix)
    #best_values = counter.most_common(int(0.3*169))
    #counter_top_30 = Counter(dict(best_values))
    #print(counter_top_30)
    #coincidence_matrix, probability_matrix = generate_matrices(counter_top_30)
    #print_matrix(coincidence_matrix)
    #print_matrix(probability_matrix)
