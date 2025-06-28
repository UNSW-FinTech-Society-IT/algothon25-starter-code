#!/usr/bin/env python3

# Note this code could definitely be written in a cleaner way
# If you want me to refactor this just msg me lol
# - Alex

import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("prices.txt")

stock_prices = data[:, 0]

# Sharpe ratio is (expected return - risk free rate) / (total risk taken)
# Basically profit / risk - less risk better
# Risk is the consistency we make money - for eg make 1000, 20, -1000 is very risky
# 0 - 1 bad
# 1 - 2 almost acceptable
# 2 - 3 good
# 3 > poggers


class STLT_Exp_Position_Generator:
    def __init__(self, short_term_duration, long_term_duration):
        self.cash_equiv = 0
        self.short_term_avgs = []
        self.long_term_avgs = []
        self.short_term_duration = short_term_duration
        self.long_term_duration = long_term_duration

    def compute_position(self, day, price_history):
        if day >= self.long_term_duration:
            # Compute short term average
            short_term_avg = self.get_exp_trailing_avg(
                self.short_term_duration, price_history, self.short_term_avgs
            )
            self.short_term_avgs.append(short_term_avg)
            # Compute long term average
            long_term_avg = self.get_exp_trailing_avg(
                self.long_term_duration, price_history, self.long_term_avgs
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
                # print("Shorted and set position to -10000 worth of shares")
                self.cash_equiv = -10000

            # Short term avg just became more than long term avg, then go long
            if (
                len(self.long_term_avgs) >= 2
                and self.short_term_avgs[-2] < self.long_term_avgs[-2]
                and short_term_avg >= long_term_avg
            ):
                # Add 10000 dollars worth of shares
                # print("Long and set position to 10000 worth of shares")
                self.cash_equiv = 10000

        return self.cash_equiv // price_history[-1]

    # Gets the exponential average of the last nth days of price_history and
    # returns it (n is duration)
    def get_exp_trailing_avg(self, duration, price_history, ema_history):
        # Smoothing factor
        k = 2 / (duration + 1)
        today = price_history[-1]
        # Note we haven't appended today's
        # Also on first run, use sma as initial yesterday value
        if len(ema_history) == 0:
            ema_yesterday = self.get_trailing_avg(duration, price_history)
        else:
            ema_yesterday = ema_history[-1]
        return today * k + ema_yesterday * (1 - k)

    # Gets the average of the last n days of price_history and returns it
    # (n is duration)
    def get_trailing_avg(self, duration, price_history):
        return sum(price_history[-duration:]) / duration

if __name__ == "__main__":
    gen = STLT_Exp_Position_Generator()
    for day, stock_price in enumerate(stock_prices):
        position = gen.compute_position(day, stock_prices[: day + 1])
        print(f"Day: {day}, position: {position}")
