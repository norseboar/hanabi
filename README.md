main.py has a function to run simulations w/ different strategies.

E.g.
`python main.py 300 -s SORT_1 -s SORT_2 -s SORT_3 -s ADVANCED_QUEUE -n 2 -n 3 -n 4`

Parameters are explained in the file, but basics:
- First argument is the number of simulations to run for each strategy, player combination
- `-s` can be used any number of times, to try different strategies. Strategies in `players/__init__.py`
- `-n` can be used any number of times, to try different numbers of players
- `--seed` can be used to replay a specific game (useful for debugging)


To create new strategies, create a new player subclass. `BasicQueuePlayer` and `AdvancedQueuePlayer` does most of the basic stuff, and the subclasses of those are to customize e.g. how to prioritize hints.