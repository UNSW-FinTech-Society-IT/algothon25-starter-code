#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from rsi import RSI_Position_Generator, RSI_PERIOD, MOVING_AVERAGE_WINDOW

data = np.loadtxt("prices.txt")

stock_prices = data[:, 0]

# Bollinger needs
#  - sd
#  - three bands
#  - middle band is moving average
#  - upper and lower bands represent SD * multiplier



class Bollinger_RSI_Position_Generator:
    def __init__(self, time_period, num_sd):
        self.multiplier = num_sd
        # Time period (from curr day) used to calculate SMA and SD
        self.time_period = time_period
        self.cash_equiv = 0
        # Initialise one RSI object for each stock
        self.rsi_obj = RSI_Position_Generator()
        self.rsi_history = []

        # Initialise boolean reflecting if we are currently entered into a position
        self.has_entered_position = False
        # Declare boolean reflecting what position we are entered in
        self.position_is_long = False
        # Initialise a stop-loss
        self.stop_loss = 0
        # Declare variable to store price of band on day we entered the trade
        self.band_price = 0
        # Initialise variable that stores the number of shares held for this stock
        self.num_shares_held = 0

        # Counter to track how many days has passed, since day does not always start from 0.
        self.days_passed = 0
        # NOTE: these lists are not necessary if we are only considering values from
        # the current day.
        self.sma_ls = []
        self.upper_band_ls = []
        self.lower_band_ls = []

    def compute_position(self, day, price_history):
        # Start calculating RSI value and adding to the list rsi_history when
        # enough days has passed.
        if self.days_passed < RSI_PERIOD + 1:
            self.days_passed += 1
            return 0
        elif self.days_passed == RSI_PERIOD + 1:
            rsi = self.rsi_obj.calculate_initial_rsi(day, stock_prices)
            self.rsi_history.append(rsi)
            self.days_passed += 1
        else:
            rsi = self.rsi_obj.calculate_rsi(day, stock_prices)
            self.rsi_history.append(rsi)

        # If there's enough past data to calculate the SMA, compute position
        # using Bollinger bands and then confirm with RSI.
        if day >= self.time_period:
            # Compute simple moving average
            sma = self.get_trailing_avg(self.time_period, price_history)
            # Add to list of daily moving averages
            self.sma_ls.append(sma)

            std = self.get_std(self.time_period, price_history)
            # Calculate upper and lower bounds for current day and add to the lists
            self.upper_band_ls.append(sma + self.multiplier * std)
            self.lower_band_ls.append(sma - self.multiplier * std)

            # Set stop-loss to be half the difference between the bands and the SMA
            # Note that the take-profit will just be the price of the SMA.
            stop_loss_band_diff = (self.multiplier * std) / 2

            # Check whether we have previously entered or exited a position.
            # If we have entered a position, check if price has met stop-loss or
            # take-profit.
            # If not, see if we should enter a position based on Bollinger.
            if self.has_entered_position and self.position_is_long:
                # We were already buying on a previous day
                if (
                    price_history[-1] <= self.band_price - stop_loss_band_diff or
                    price_history[-1] >= sma
                ):
                    # Exit if price drops below stop-loss to reduce losses, or cash out
                    # if price rises above take-profit.
                    self.cash_equiv -= (self.num_shares_held * price_history[-1])
                    self.has_entered_position = False
                    self.num_shares_held = 0
            elif self.has_entered_position:
                # We were already shorting on some previous day
                if (
                    price_history[-1] >= self.band_price + stop_loss_band_diff or
                    price_history[-1] <= sma
                ):
                    # Exit if price rises above stop-loss to reduce losses, or cash out
                    # if price falls below take-profit.
                    self.cash_equiv += (self.num_shares_held * price_history[-1])
                    self.has_entered_position = False
                    self.num_shares_held = 0
            else:
                ### Not entered in any trade (positionless) ###
                # Check if stock price is trading around the upper/lower bands,
                # confirm with RSI value.
                if (
                    price_history[-1] >= self.upper_band_ls[-1] and
                    self.rsi_history[-1] > 70
                ):
                    self.cash_equiv -= 10000
                    self.has_entered_position = True
                    self.position_is_long = False
                    self.band_price = self.upper_band_ls[-1]
                    self.num_shares_held = self.cash_equiv // price_history[-1]
                elif (
                    price_history[-1] <= self.lower_band_ls[-1] and
                    self.rsi_history[-1] < 30
                ):
                    self.cash_equiv += 10000
                    self.has_entered_position = True
                    self.position_is_long = True
                    self.band_price = self.lower_band_ls[-1]
                    self.num_shares_held = self.cash_equiv // price_history[-1]
        
        return self.num_shares_held

    # Gets the average of the last n days of price_history and returns it
    # (n is duration)
    def get_trailing_avg(self, duration, price_history):
        return sum(price_history[-duration:]) / duration

    # Gets the standard deviation from the last n days of price_history and
    # returns it (n is duration/time period)
    def get_std(self, duration, price_history):
        return np.std(price_history[-duration:])

    # Gets the RSI for the last RSI_PERIOD days of price_history and returns
    # it

# if __name__ == "__main__":