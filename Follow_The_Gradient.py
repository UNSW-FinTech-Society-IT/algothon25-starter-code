#!/usr/bin/env python3

import numpy as np

data = np.loadtxt("prices.txt")

stock_prices = data[:, 0]
NUM_ROWS = len(data[:, 1])


class FTG_Position_Generator:
    def __init__(self):
        self.money_weighted_pos = 0  # how much the stocks are worth in money.
        self.short_term_avgs = []
        self.long_term_avgs = []

    # position is the number of stocks you are buying/selling.
    def compute_position(self, day, stock_prices):
        # error handling, day has to be within range.
        current_price = stock_prices[day]
        if day <= NUM_ROWS - 10:
            # stocks from the recent 10 days
            recent_ten_days = stock_prices[day : day + 10]
            # the 100 moving average
            ten_day_moving_average = [
                np.mean(stock_prices[i : i + 101])
                for i in range(day, day + 10)
            ]
            times = [i for i in range(day, day + 10)]
            # [day, day +1 , ..., day + 10]

            print(times)
            print(recent_ten_days)
            print(day)
            ten_day_gradient = np.gradient(recent_ten_days, times)
            moving_average_gradient = np.gradient(
                ten_day_moving_average, times
            )

            # compare the gradients
            difference = np.mean(ten_day_gradient - moving_average_gradient)

            GRADIENT_DIFF = 0.1
            if difference < GRADIENT_DIFF:
                # print("Long and set position to 10000 worth of shares")
                self.money_weighted_pos = 10000
            elif difference > GRADIENT_DIFF:
                # print("Shorted and set position to -10000 worth of shares")
                self.money_weighted_pos = -10000
            # else:
            #     print("do nothing")

        # return # of stocks
        # print()
        return self.money_weighted_pos / current_price


if __name__ == "__main__":
    gen = Position_Generator()
    for day, stock_price in enumerate(stock_prices):
        if day <= NUM_ROWS - 11:
            position = gen.compute_position(day, stock_prices)
            print(f"Day: {day + 1}, position: {position}")
