#!/usr/bin/python
from collections import defaultdict

import click
from numpy import mean

from game import Game


LOG_PATH = "/Users/reed/hanabi/game_logs/"
PARAM_RANGE = 5
SEARCH_INTERVAL = 1


@click.command()
@click.option("--trials", "-t", type=click.INT)
@click.option("--parameter", "-p", "params", multiple=True)
def find_optimal_params(trials, params):
    best_score = -2
    best_weights = None

    new_best_score = -1
    new_best_weights = defaultdict(float)
    for p in params:
        new_best_weights[p] = PARAM_RANGE / 2
    while new_best_score > best_score:
        best_score = new_best_score
        best_weights = new_best_weights

        new_best_score = -1
        new_best_weights = None

        neighbor_weights = []
        for p in params:
            new_weights = best_weights.copy()
            new_weights[p] += SEARCH_INTERVAL
            neighbor_weights.append(new_weights)

            new_weights = best_weights.copy()
            new_weights[p] -= SEARCH_INTERVAL
            neighbor_weights.append(new_weights)

        for w in neighbor_weights:
            score = score_weights(w, trials)
            if score > new_best_score:
                new_best_score = score
                new_best_weights = w

    click.echo("Best score: {}".format(best_score))
    click.echo("Best weights: {}".format(best_weights))


def score_weights(weights, num_games):
    click.echo("Trying weights {}".format(weights))
    scores = []
    for _ in range(num_games):
        g = Game(
            3,
            "INFO",
            should_print=False,
            weights=weights,
        )
        scores.append(g.run_game())
    click.echo("Score is {}".format(mean(scores)))
    return mean(scores)


if __name__ == "__main__":
    find_optimal_params()
