"""
data_science.py. script to fetch the data from files and to produce analisys and reports.
Current activities:
    split winner hands and provide a matris of result with coicidences and probabilities
"""
import argparse
from collections import Counter
import os
import sys
from datetime import datetime

VALUES = "23456789TJQKA"
INVERSE_VALUES = VALUES[::-1]
P_CASES = 6
S_CASES = 4
N_CASES = 12
T_HANDS = 1326

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
    with open(file_path, 'r', encoding="utf-8") as simulation_file:
        for sim_line in simulation_file:
            sim_line = sim_line.strip()
            if not sim_line:
                continue
            fields = sim_line.split('|')
            if fields[1] == "hand":
                continue
            second_field = fields[1].split(',')
            classification = classify_hand(second_field)
            result.append(classification)
    return result

def generate_matrices(win_counter, total_players):
    """Function to generate matrices"""
    o_coincidence_matrix = [[0 for _ in range(len(VALUES))] for _ in range(len(VALUES))]
    o_probability_matrix = [[0 for _ in range(len(VALUES))] for _ in range(len(VALUES))]
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
        value_probability = value*T_HANDS/(total_players*cases*num_simulations)
        o_coincidence_matrix[row_idx][col_idx] = value
        o_probability_matrix[row_idx][col_idx] = value_probability
    return o_coincidence_matrix, o_probability_matrix

def print_matrix(matrix, threshold=0, long_report=False):
    """Function to print matrices. Threshold is used to set values with low posibility to 0."""
    min_val, max_val = 0, max(value for row in matrix for value in row)

    def get_grayscale(value):
        """Helper function for print_matrix.
        get_grayscale function to set colors based on the value."""

        if value == 0:
            return "\033[0m"
        normalized = (value - min_val) / (max_val - min_val) if max_val != min_val else 0
        grayscale_level = int(normalized * 255)
        return f"\033[38;2;0;{max(100-grayscale_level,0)};{grayscale_level}m"

    max_width = 1
    for row in matrix:
        for value in row:
            value_lenght = len(f'{value}') if isinstance(value, int) else len(f'{value:.4f}')
            max_width = max(max_width, value_lenght)

    print('  ' + ' '.join(f'{rank:>{max_width+1}}' for rank in INVERSE_VALUES))
    for i, rank in enumerate(INVERSE_VALUES):
        row = []
        for j in range(len(VALUES)):
            value = matrix[i][j]
            if value < threshold or value == 0:
                row.append(f'{"":>{max_width}}')
                continue
            color_code = get_grayscale(value)
            f_v = f'{value:>{max_width}}' if isinstance(value, int) else f'{value:>{max_width}.4f}'
            f_v = f'{f_v}' if long_report else f'{color_code}{f_v}\033[0m'
            row.append(f"{f_v}")

        # Print each row with rank labels
        print(f'{rank}  ' + '  '.join(row))
    print("\n")

## generators
def report_generator(i_file_list, n_players, output="", report=True):
    """Take input parameters to make a report file with the required analisys."""
    if report:
        if output=="":
            file_path = os.getenv("POKER_OUT_FILE_PATH", "") + "reports\\"
        else:
            file_path = output
        time_format = datetime.now().strftime("%Y%m%d_%H%M%S")

        file_name = f"{file_path}PKM_summary_{n_players}_{time_format}.txt"
        print("final file_name:", file_name)
        os.makedirs(file_path, exist_ok=True)
        with open(file_name, "w", encoding="utf-8") as report_file:
            previous_output = sys.stdout
            sys.stdout = report_file
            raw_to_matriz_gen(i_file_list, n_players, long_report=True)
            sys.stdout = previous_output
        return

    raw_to_matriz_gen(i_file_list, n_players)
    return



def raw_to_matriz_gen(i_file_list, n_players, long_report=False):
    """Function raw_to_matriz_gen. Based on an input file list and the number of players based
        on the simulations create a report of the card wins and the pobability of winning."""
    if long_report:
        print("In raw_to_matriz_gen from data_science.py")
        print(f"input: \n Files: {i_file_list}, \n number of Players: {n_players}")

    winner_counter = Counter()
    for file_name in i_file_list:
        winner_counter += Counter(process_file(file_name))
        simulations_read = sum(item[1] for item in winner_counter.most_common(len(winner_counter)))
    if long_report:
        print("Wins counter per card combinations.")
        print("Combination format: [card_a][card_b][combination_type].")
        print("Combination types: P=Pairs ; S=Suits ; N=Non pairs or suits.")
        print()
    print(winner_counter)

    if long_report:
        print(f"Number of combinations: {len(winner_counter)}")
        print(f"Number of simulations found: {simulations_read}")
        print()
        print()

    coincidence_matrix, probability_matrix = generate_matrices(winner_counter, n_players)

    if long_report:
        print("Coincidence matrix:")
        print("Pairs are in the diagonal, the top triangle contains suit combinations and")
        print("the bottom triangle contains non-suit combinations.")
    print_matrix(coincidence_matrix, 0, long_report)

    if long_report:
        print("Probability_matrix:")
        print("Given the obtained pair this chart shows the probability of winning.")
        print("The probability is a number from 0 to 1.")
        print("A probability near to 1 will likely happen.")
    print_matrix(probability_matrix, 0, long_report)

    threshold=round(1/n_players, 2)
    threshold_list = [ num*threshold for num in [1, 1.5, 2] ]
    if long_report:
        print(f"Thresholds: {threshold_list}")
        print(f"A threshold of {threshold} is a fair probability, 1/num_players")
    for threshold in threshold_list:
        if long_report:
            print(f"Threshold: {threshold}")
        print_matrix(probability_matrix, threshold, long_report)
    print()


if __name__ == "__main__":
    #files created evaluating all the hand combinations

    parser = argparse.ArgumentParser(
        description='Data Analysis App for Monte Carlo Poker simulations.')
    parser.add_argument('number_of_players')
    parser.add_argument('-f', '--file')
    parser.add_argument('-o', '--output_path')
    parser.add_argument('-l', '--list_file')
    args = parser.parse_args()

    print(args)
    numner_players = int(args.number_of_players)

    input_file_list = [args.file] if args.file is not None else []
    if args.list_file is not None:
        with open(args.list_file, 'r', encoding="utf-8") as input_list_file:
            for line in input_list_file:
                input_file_list.append(line.strip())

    output_path = [args.output_path] if args.output_path is not None else ""

    print(f"numner_players: {numner_players}, output_path: {output_path}")
    print(f"input_file_list: {input_file_list}")
    report_generator(input_file_list, numner_players, output_path)
