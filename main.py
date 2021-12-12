#!/usr/bin/python
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
@click.option("--use-rainbow", is_flag=True, default=False)
@click.option("--num-players", "-n", multiple=True, default=[2])
@click.option("--seed", type=click.INT, default=None)
def run_simulations(num_games, strategies, create_logs, use_rainbow, num_players, seed):
    PERFECT_SCORE = (6 if use_rainbow else 5) * 5
    log_file_name = (
        LOG_PATH + "hanabi_log_" + datetime.now().isoformat(timespec="seconds") + ".txt"
    )

    log_file = None
    if create_logs:
        log_file = open(log_file_name, "w")

    for strategy in strategies:
        log_string(
            """
===========================================================================
Simulations for {} {}
===========================================================================
            """.format(
                strategy,
                "with rainbow" if use_rainbow else "no rainbow",
                log_file,
                should_print=True,
            ),
            log_file,
            should_print=True,
        )

        results = []
        for n in num_players:
            scores = []
            wasted_discard_pcts = []
            for _ in range(num_games):
                g = Game(
                    n,
                    strategy,
                    use_rainbow,
                    should_print=False,
                    log_file=log_file,
                    seed=seed,
                )
                scores.append(g.run_game())
                wasted_discard_pcts.append(g.wasted_discards / g.current_turn)
            results.append(
                [
                    n,
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
                    "Players",
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
