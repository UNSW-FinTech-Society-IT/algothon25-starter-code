#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import Math
data = np.loadtxt("prices.txt")

stock_prices = data[:, 0]
NUM_ROWS = len(data[:, 0])
class Position_Generator:
    def __init__(self):
        self.money_weighted_pos = 0
        self.short_term_avgs = []
        self.long_term_avgs = []

    def compute_position(self, day, stock_prices):
        # error handling, day has to be within range.
        if day <= NUM_ROWS - 11:
            recent_ten_days = stock_prices[day: day + 11]
            ten_day_moving_average = [Math.avg(stock_prices[i: i + 101]) for i in range(day, day+11)]
            times = [i for i in range(day, day+11)]
            # [day, day +1 , ..., day + 10]

            ten_day_gradient = np.gradient(recent_ten_days, times)
            moving_average_gradient = np.gradient(ten_day_moving_average, times)

            # compare the gradients
            absolute_difference = Math.abs(ten_day_gradient - moving_average_gradient)

            if absolute_difference > 0.2:
                pass # go long
            else:
                pass # go short





if __name__ == "__main__":
    gen = Position_Generator()
    for day, stock_price in enumerate(stock_prices):
        if day <= NUM_ROWS - 11:
            position = gen.compute_position(day, stock_prices)
            print(f"Day: {day}, position: {position}")