#!/usr/bin/env python3

import numpy as np

data = np.loadtxt("prices.txt")

stock_prices = data[:, 0]
NUM_ROWS = len(data[:, 1])
RECENT_DAYS = 9
MOVING_AVG_DAYS = 10
MIN_DAYS = 11

class FTG_Position_Generator:
    def __init__(self):
        self.money_weighted_pos = 0  # how much the stocks are worth in money.
        self.short_term_avgs = []
        self.long_term_avgs = []

    # position is the number of stocks you are buying/selling.
   # In Follow_The_Gradient.py


    def compute_position(self, day, stock_prices):
        current_price = stock_prices[day]

        # --- FIX ---
        # The logic must be based on PAST data.
        # We need at least 101 days of history for the moving average calculation.
        if day > MIN_DAYS: 
            # Use data from the 10 days PRIOR to the current 'day'
            recent_ten_days = stock_prices[day - RECENT_DAYS : day]
            times = np.arange(RECENT_DAYS) # A simple range of 10 points

            # The 100-day moving average must also be calculated from past data
            hundred_day_moving_average = [
                np.mean(stock_prices[i - MOVING_AVG_DAYS : i]) for i in range(day - RECENT_DAYS, day)
            ]
            
            # Now len(recent_ten_days) and len(times) will both be 10, fixing the error.
            ten_day_gradient = np.gradient(recent_ten_days, times)
            moving_average_gradient = np.gradient(
                hundred_day_moving_average, times
            )

            # compare the gradients
            difference = np.mean(ten_day_gradient - moving_average_gradient)

            GRADIENT_DIFF = 0.1
            if difference < GRADIENT_DIFF:
                self.money_weighted_pos = 10000
            elif difference > GRADIENT_DIFF:
                self.money_weighted_pos = -10000

        return self.money_weighted_pos / current_price


if __name__ == "__main__":
    gen = FTG_Position_Generator()
    for day, stock_price in enumerate(stock_prices[250:], start=250):
        if day <= NUM_ROWS - 11:
            position = gen.compute_position(day, stock_prices)
            print(f"Day: {day + 1}, position: {position}")
