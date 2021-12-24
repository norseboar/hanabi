#!/usr/bin/python
from collections import defaultdict
import multiprocessing as mp
from multiprocessing import process

import click
from numpy import mean

from game import Game


LOG_PATH = "/Users/reed/hanabi/game_logs/"
PARAM_RANGE = 5
SEARCH_INTERVAL = 1


@click.command()
@click.option("--trials", "-t", type=click.INT)
@click.option("--parameter", "-p", "params", multiple=True)
@click.option("--process-num", default=6)
def find_optimal_params(trials, params, process_num):
    assert process_num <= mp.cpu_count()
    pool = mp.Pool(process_num)

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
            click.echo("Trying weights {}".format(w))
            trial_args = [w for _ in range(trials)]
            scores = pool.map_async(score_weights, trial_args).get()
            score = mean(list(scores))
            click.echo("Score is {}".format(score))
            if score > new_best_score:
                new_best_score = score
                new_best_weights = w

    pool.close()
    click.echo("Best score: {}".format(best_score))
    click.echo("Best weights: {}".format(best_weights))


def score_weights(weights):
    g = Game(
        3,
        "INFO",
        should_print=False,
        weights=weights,
    )
    return g.run_game()


if __name__ == "__main__":
    find_optimal_params()
