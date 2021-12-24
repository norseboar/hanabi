#!/usr/bin/python
from collections import defaultdict
from datetime import datetime

import click
from numpy import mean, percentile, std
from tabulate import tabulate

from game import Game, log_string

LOG_PATH = "/Users/reed/hanabi/game_logs/"


@click.command()
@click.argument("num_games", type=click.INT)
@click.option("--strategy", "-s", "strategies", multiple=True)
@click.option("--create-logs", is_flag=True, default=False)
@click.option("--verbose", is_flag=True, default=False)
@click.option("--use-rainbow", is_flag=True, default=False)
@click.option("--num-players", "-n", multiple=True, default=[2])
@click.option("--seed", type=click.INT, default=None)
@click.option(
    "--weight",
    "-w",
    "param_weights",
    multiple=True,
    nargs=2,
    type=click.Tuple([str, float]),
)
def run_simulations(
    num_games,
    strategies,
    create_logs,
    verbose,
    use_rainbow,
    num_players,
    seed,
    param_weights,
):
    PERFECT_SCORE = (6 if use_rainbow else 5) * 5
    log_file_name = (
        LOG_PATH + "hanabi_log_" + datetime.now().isoformat(timespec="seconds") + ".txt"
    )

    log_file = None
    if create_logs:
        log_file = open(log_file_name, "w")

    weights = defaultdict(int)
    for p, w in param_weights:
        weights[p] = w

    for n in num_players:
        log_string(
            """
===========================================================================
Simulations for {} players {}
===========================================================================
            """.format(
                n,
                "with rainbow" if use_rainbow else "no rainbow",
                log_file,
                should_print=True,
            ),
            log_file,
            should_print=True,
        )

        results = []
        for strategy in strategies:
            scores = []
            wasted_discard_pcts = []
            for _ in range(num_games):
                g = Game(
                    n,
                    strategy,
                    use_rainbow,
                    should_print=verbose,
                    log_file=log_file,
                    seed=seed,
                    weights=weights,
                )
                scores.append(g.run_game())
                wasted_discard_pcts.append(g.wasted_discards / g.current_turn)
            results.append(
                [
                    strategy,
                    round(mean(scores), 2),
                    percentile(scores, 10),
                    percentile(scores, 50),
                    percentile(scores, 90),
                    round((scores.count(PERFECT_SCORE) / num_games) * 100, 2),
                    round(std(scores), 2),
                    round(mean(wasted_discard_pcts) * 100, 2),
                ]
            )

        result_table = (
            tabulate(
                results,
                headers=[
                    "Strategy",
                    "Mean",
                    "P10",
                    "P50",
                    "P90",
                    "Perfect",
                    "std",
                    "Wasted discard %",
                ],
                tablefmt="pretty",
            )
            + "\n"
        )
        log_string(result_table, log_file, should_print=True)

    if log_file:
        log_file.close()


if __name__ == "__main__":
    run_simulations()
