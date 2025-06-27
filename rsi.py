#!/usr/bin/env python3

import numpy as np
from enum import Enum

RSI_PERIOD = 14
MOVING_AVERAGE_WINDOW = 14


class Position(Enum):
    FLAT = 1
    SHORT = 2
    LONG = 3


class RSIPositionGenerator:
    """Constructor"""

    def __init__(self, stock_prices):
        self.__data = {}  # TODO: RENAME THIS TO SMTH MORE CLEAR
        self.__stock_prices = stock_prices
        self.__money_weighted_pos = 0
        self.__current_position = Position.FLAT
        self.__entry_price = 0
        self.__entry_ma = 0

    def add_data(self, day, average_gain, average_loss):
        """Add data such as avg_gain and avg_loss"""
        self.__data[day] = {"avg_gain": average_gain, "avg_loss": average_loss}

    def get_data(self, day: int):
        """Retrieve data"""
        return self.__data[day]

    def set_entry_price(self, price: int):
        """Setter"""
        self.__entry_price = price

    def get_entry_price(self):
        """Getter"""
        return self.__entry_price

    def set_entry_ma(self, ma):
        """Set entry moving average"""
        self.__entry_ma = ma

    def get_entry_ma(self):
        """Get entry moving average"""
        return self.__entry_ma

    def get_stock_prices(self):
        """Retrieve stock prices"""
        return self.__stock_prices

    def get_money_pos(self):
        """Get money positon"""
        return self.__money_weighted_pos

    def set_money_pos(self, value):
        """Set money position"""
        self.__money_weighted_pos = value

    def buy(self):
        self.set_money_pos(10000)

    def sell(self):
        self.set_money_pos(-10000)

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

    def calculate_rsi(self, day: int):
        """Calculate the RSI on day"""
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

    def get_moving_average(self, day: int):
        stocks = self.get_stock_prices()

        return np.mean(stocks[day - MOVING_AVERAGE_WINDOW + 1 : day + 1])

    def get_current_position(self):
        return self.__current_position

    def set_position(self, new_position: Position):
        self.__current_position = new_position

    def calculate_position(self, day):
        """The main logic function to decide on trading actions for a given day."""
        rsi = self.calculate_rsi(day)
        moving_average = self.get_moving_average(day)
        current_price = self.get_stock_prices()[day]

        position = self.get_current_position()

        if position == Position.FLAT:  # If we are flat, check for an entry signal
            if rsi < 20:
                self.set_position(Position.LONG)
                self.set_entry_price(current_price)
                self.set_entry_ma(moving_average)
                self.buy()
                # print(
                #     f"Day {day}: RSI < 20 ({rsi:.2f}). Entering LONG position at {current_price:.2f}"
                # )
            elif rsi > 80:
                self.set_position(Position.SHORT)
                self.set_entry_price(current_price)
                self.set_entry_ma(moving_average)
                self.sell()
                # print(
                #     f"Day {day}: RSI > 80 ({rsi:.2f}). Entering SHORT position at {current_price:.2f}"
                # )

        # If we are not flat, check for an exit signal
        elif position == Position.LONG:
            if rsi > 60:
                # print(
                #     f"Day {day}: RSI > 60 ({rsi:.2f}). Take Profit on LONG at {current_price:.2f}. Profit: {current_price - self.get_entry_price():.2f}"
                # )
                self.set_position(Position.FLAT)
                self.set_money_pos(0)
            else:
                # point WHEN you entered trade.
                entry_price = self.get_entry_price()
                stop_loss_level = self.get_entry_price() - (self.get_entry_ma() / 2)
                if entry_price < stop_loss_level:
                    # print("stop loss")
                    self.set_position(Position.FLAT)
                    self.set_money_pos(0)

        elif position == Position.SHORT:
            if rsi < 40:
                # print(
                #     f"Day {day}: RSI < 40 ({rsi:.2f}). Take Profit on SHORT at {current_price:.2f}. Profit: {self.get_money_pos() - current_price:.2f}"
                # )
                self.set_position(Position.FLAT)
                self.set_money_pos(0.0)
            else:
                entry_price = self.get_entry_price()
                stop_loss_level = entry_price + (self.get_entry_ma() / 2)
                if entry_price > stop_loss_level:
                    # print(
                    #     f"Day {day}: Price {current_price:.2f} hit Stop Loss {stop_loss_level:.2f}. Closing SHORT. Loss: {self.get_money_pos() - current_price:.2f}"
                    # )
                    self.set_position(Position.FLAT)
                    self.set_money_pos(0.0)
        return self.get_money_pos() / current_price

def main():
    """Main function"""
    data = np.loadtxt("prices.txt")

    stock_prices = data[:, 0]
    pos = RSIPositionGenerator(stock_prices)

    init_rsi = pos.calculate_initial_rsi()
    print(init_rsi)

    # start on day 16
    for i in range(RSI_PERIOD + 2, len(stock_prices)):
        rsi = pos.calculate_position(i)
        print(rsi)


if __name__ == "__main__":
    main()
