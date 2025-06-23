from typing import List, Optional
import numpy as np

# from sigMA.STLT_Moving_Avg import Position_Generator

data = np.loadtxt("prices.txt")

# plt()
# Constants
SHORT_TERM_MA_WINDOW = 20
# sigma is standard deviation (finance term)
NUM_SIGMA = 2

#Standard Deviation Formula
# sigma = np.std(stock_prices[:14])

class STD_Revert_Generator:
    def __init__(self, stock_prices):
        self.money_weighted_pos = 0
        self.stock_prices = stock_prices
    def calculate_sigma_sma(self, day):
        """Calculates sigma over a 14 day period"""

        array = self.stock_prices[day - SHORT_TERM_MA_WINDOW: day]

        sigma = np.std(array)
        sma = np.mean(array)

        return sigma, sma


    def compute_position(self, day):
        """Compute position"""
        current_price = self.stock_prices[day] # price on day X
        sigma, sma = self.calculate_sigma_sma(day)
        upper_band, lower_band = self.get_upper_lower_band(sma, sigma)

        if current_price > upper_band:
            self.money_weighted_pos = -10000
            print(f"Day {day}: Price {current_price:.2f} > Upper Band {upper_band:.2f}. Sell")
        elif current_price < lower_band:
            self.money_weighted_pos = 10000
            print(f"Day {day}: Price {current_price:.2f} < Lower Band {lower_band:.2f}. Buy")


        if current_price > 0: # Avoid division by zero
            return int(self.money_weighted_pos // current_price)

        return int(self.money_weighted_pos // self.stock_prices[day])
        



    # # Create a upper band and lower band value based off of standard deviations from the short term moving average price
    def get_upper_lower_band(self, midde_band, sigma):
        upper_band = midde_band + (sigma * NUM_SIGMA)
        lower_band = midde_band - (sigma * NUM_SIGMA)

        return upper_band, lower_band



def main():
    stock_prices = data[:, 0]
    blob = STD_Revert_Generator(stock_prices=stock_prices)
    for day in range(SHORT_TERM_MA_WINDOW, len(stock_prices)):
        blob.compute_position(day)


if __name__ == "__main__":
    main()
