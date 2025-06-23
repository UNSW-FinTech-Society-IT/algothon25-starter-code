from typing import List, Optional
import numpy as np
import matplotlib.pyplot as plt

from sigMA.STLT_Moving_Avg import Position_Generator

data = np.loadtxt("prices.txt")

stock_prices = data[:, 0]
plt()
# Constants
SHORT_TERM_MA_WINDOW = 20

#Standard Deviation Formula
np.std(stock_prices[:14])

class STD_Revert_Generator:

    def __init__(self, price_history):
        self.execute_trade = 0
        self.price_history = price_history
        
        
    def short_term_ma(self) -> Any:
        return 
    def compute_position(self, day):
        price_history = self.price_history
        if SIGMA >= 2.00:
        sell

    def bollinger_band_strategy(self) -> Any:
        # calculate a short term moving average
        short_term_moving_average = self.short_term_moving_average()
        # Execute trade whenever the current stock price hits upper/lower band
        if short_term_moving_average > self.upper_band():
            # Sell if price hits upper band
            self.execute_trade = -10000 # sell 10000 worth of shares
        if short_term_moving_average < self.lower_band():
            self.execute_trade = 10000 # buy 10000 worth of shares
        
    def short_term_moving_average() -> float:
        short_term_avg = Position_Generator.get_trailing_avg(
                SHORT_TERM_MA_WINDOW, price_history

    # Create a upper band and lower band value based off of standard deviations from the short term moving average price
    def upper_band() -> float:
        pass

    def lower_band() -> float:
        pass

    def execute_trade() -> None:
    
        # Buy if price hits lower band
        pass






class A:
    a: int
    b: int
    c: int
    
    def __init__(self, a: int, b: Optional[int] = None):
        self.a = a
        if not b:
            b = 100
        self.b = b
        self.c = 25

    def some_func(self) -> int:
        self.a += 1
        return self.a + self.b - self.c