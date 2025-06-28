#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("prices.txt")

stock_prices = data[:, 0]

# Bollinger needs
#  - sd
#  - three bands
#  - middle band is moving average
#  - upper and lower bands represent SD



class Bollinger_Position_Generator:
    def __init__(self, time_period, num_sd):
        self.multiplier = num_sd
        # Time period (from curr day) used to calculate SMA and SD
        self.time_period = time_period
        self.cash_equiv = 0
        # NOTE: these lists are not necessary if we are only considering values from
        # the current day.
        self.sma_ls = []
        self.upper_band_ls = []
        self.lower_band_ls = []

    def compute_position(self, day, price_history):
        if day >= self.time_period:
            # Compute simple moving average
            sma = self.get_trailing_avg(self.time_period, price_history)
            # Add to list of daily moving averages
            self.sma_ls.append(sma)

            std = self.get_std(self.time_period, price_history)
            # Calculate upper and lower bounds for current day and add to the lists
            self.upper_band_ls.append(sma + self.multiplier * std)
            self.lower_band_ls.append(sma - self.multiplier * std)

            # Check if stock price is trading around the upper/lower bands
            if price_history[-1] >= self.upper_band_ls[-1]:
                self.cash_equiv = -10000
            elif price_history[-1] <= self.lower_band_ls[-1]:
                self.cash_equiv = 10000
        
        return self.cash_equiv // price_history[-1]

    # Gets the average of the last n days of price_history and returns it
    # (n is duration)
    def get_trailing_avg(self, duration, price_history):
        return sum(price_history[-duration:]) / duration

    # Gets the standard deviation from the last n days of price_history and
    # returns it (n is duration/time period)
    def get_std(self, duration, price_history):
        return np.std(price_history[-duration:])


# if __name__ == "__main__":