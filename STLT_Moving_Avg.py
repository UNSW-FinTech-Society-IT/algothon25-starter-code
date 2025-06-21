#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("prices.txt")

stock_prices = data[:, 0]

# Constants
SHORT_TERM_DURATION = 10
LONG_TERM_DURATION = 20


class Position_Generator:
    def __init__(self):
        self.money_weighted_pos = 0
        self.short_term_avgs = []
        self.long_term_avgs = []

    def compute_position(self, day, price_history):
        if day >= LONG_TERM_DURATION:
            # Compute short term average
            short_term_avg = self.get_trailing_avg(
                SHORT_TERM_DURATION, price_history
            )
            self.short_term_avgs.append(short_term_avg)
            # Compute long term average
            long_term_avg = self.get_trailing_avg(
                LONG_TERM_DURATION, price_history
            )
            self.long_term_avgs.append(long_term_avg)

            # Price of share when sold - Price of share on the day it was traded
            # If our position is negative

            # Short term avg just became less than long term avg, then go short
            if (
                len(self.short_term_avgs) >= 2
                and self.short_term_avgs[-2] > self.long_term_avgs[-2]
                and short_term_avg <= long_term_avg
            ):
                # Set current position to 10000 worth of shares
                print("Shorted and set position to -10000 worth of shares")
                self.money_weighted_pos = -10000

            # Short term avg just became more than long term avg, then go long
            if (
                len(self.long_term_avgs) >= 2
                and self.short_term_avgs[-2] < self.long_term_avgs[-2]
                and short_term_avg >= long_term_avg
            ):
                # Add 10000 dollars worth of shares
                print("Long and set position to 10000 worth of shares")
                self.money_weighted_pos = 10000

        return self.money_weighted_pos // price_history[-1]

    # Gets the average of the last nth days of price_history and returns it
    # (n is duration)
    def get_trailing_avg(self, duration, price_history):
        return sum(price_history[-duration:]) / duration


if __name__ == "__main__":
    gen = Position_Generator()
    for day, stock_price in enumerate(stock_prices):
        position = gen.compute_position(day, stock_prices[: day + 1])
        print(f"Day: {day}, position: {position}")
