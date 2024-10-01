### Monte carlo for poker

This project is meant to undestant probabilities in poker given actual player hands.

## Usage

To use this software python 3.11 was used, please check the compatibility of your python version. Use pip to install required packages. 

> Run monte_carlo.py to generate simulations.

```
Usage:

python monte_carlo.py <number_of_simulations> <number_of_players>
```

Files with be generated as in the included file: "poker_monte_carlo_2_3hands_20241001_162523.csv"

> Modify data_science.py to fetch analisys. based on the generated files.

## project roadmap

 - [x] Create a function which given 7 cards validate what is the bigest hand.
 - [x] Create a function which convert the bigest 5 cards hand into a number
 - [x] Create a function which assest the number obtained with every 2 cards + a random 5 cards set and determine the pair which will win. that pair will allocate point to see which pair is the best.

 - [ ] Create a program which determine the posibility to win given 5 cards, 2 player cards + 3 randon cards assuming two input cards.
 - [ ] Create a function to determine the effectivenes of the program given the number of samples
 - [ ] Implement this in cloud, explore options between lambda and ec2 using the free tier. See which option generate the most compute limit.
 - [ ] Implement real time analisys of probability based on preloaded information.
 - [ ] Implement a way to tract information of the game for further analisys based on all game activities. 

### Known issues:

 - [ ] In "monte_carlo.py", while fetching pairs for all players pairs can repit cards. A validation is required to avoid that.
 - [ ] In "monte_carlo.py", There is not a way to set a path for generated files.
 - [ ] format "data_science.py" acording to pylint
 - [ ] In "data_science.py", probability is not declared properly
 - [ ] In "data_science.py", the file usage is not intuitebly. 
 - [ ] In "data_science.py", there is not a way to generate reports of the information. All the information is printed.

## Contributions 

Please feel free to contribute on this project, there is a lot of investigation to do on this field.
