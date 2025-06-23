#!/usr/bin/env python3

import numpy as np

RSI_PERIOD = 14


class RSIPositionGenerator:
    """Constructor"""
    def __init__(self, stock_prices):
        self.__data = {} # TODO: RENAME THIS TO SMTH MORE CLEAR
        self.__stock_prices = stock_prices

    def add_data(self, day, average_gain, average_loss):
        """Add data such as avg_gain and avg_loss"""
        self.__data[day] = {"avg_gain": average_gain, "avg_loss": average_loss}

    def get_data(self, day):
        """Retrieve data"""
        return self.__data[day]

    def get_stock_prices(self):
        """Retrieve stock prices"""
        return self.__stock_prices

    def calculate_initial_rsi(self):
        """Calculate initial rsi"""
        stock_prices = self.get_stock_prices()
        delta = np.diff(stock_prices[: RSI_PERIOD + 1])

        gains = sum(d for d in delta if d > 0)
        losses = sum(abs(d) for d in delta if d < 0)

        average_gain = gains / RSI_PERIOD
        average_loss = losses / RSI_PERIOD

        if average_loss == 0:
            return 100.0

        rs = average_gain / average_loss
        rsi = 100 - (100 / (1 + rs))

        self.add_data(
            RSI_PERIOD + 1, average_gain=average_gain, average_loss=average_loss
        )

        return rsi

    def calculate_rsi(self, day):
        stock_prices = self.get_stock_prices()
        prev_day_data = self.get_data(day - 1)

        prev_avg_gain, prev_avg_loss = (
            prev_day_data["avg_gain"],
            prev_day_data["avg_loss"],
        )
        change_n = stock_prices[day] - stock_prices[day - 1]

        gain_n = max(change_n, 0)
        loss_n = max(-change_n, 0)

        curr_avg_gain = ((prev_avg_gain * (RSI_PERIOD - 1)) + gain_n) / RSI_PERIOD
        curr_avg_loss = ((prev_avg_loss * (RSI_PERIOD - 1)) + loss_n) / RSI_PERIOD

        curr_rs = curr_avg_gain / curr_avg_loss

        rsi = 100 - (100 / (1 + curr_rs))

        self.add_data(day, average_gain=curr_avg_gain, average_loss=curr_avg_loss)

        return rsi


def main():
    data = np.loadtxt("prices.txt")

    stock_prices = data[:, 0]
    pos = RSIPositionGenerator(stock_prices)

    init_rsi = pos.calculate_initial_rsi()
    print(init_rsi)
    
    # start on day 16
    for i in range(RSI_PERIOD + 2, len(stock_prices)):
        rsi = pos.calculate_rsi(i)
        print(rsi)



if __name__ == "__main__":
    main()
