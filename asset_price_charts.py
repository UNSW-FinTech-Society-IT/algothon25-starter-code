from dataclasses import dataclass, field
import sys
from typing import List

@dataclass
class StockPrices:
    """
    Holds close price
    """
    stock_name: str
    prices: List[float] = field(init=False)
    time: List[int] = field(init=True)

with open("prices.txt") as file_pointer:
    raw_data = file_pointer.read()
    clean_data = ",".join(raw_data.split())
    # print(data)
    for line in clean_data.split(','):
        print(line)
        sys.exit(0)
    # prices = data.split(" ")
    

    # print(prices)


    # with open("prices.txt") as f:
    #     @dataclass
    #     class Stock_Prices():
    #         "Holds the Stock Prices relative to a Position in Time"

    #     Title: 

    # print(f.read())
