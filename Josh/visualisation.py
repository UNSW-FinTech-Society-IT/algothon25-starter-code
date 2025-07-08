from eval import loadPrices
import matplotlib.pyplot as plt
import numpy as np

pricesFile="prices.txt"
prcAll = loadPrices(pricesFile)

plt.figure(figsize=(12, 6))

for i in range(50):
    plt.plot(prcAll[i], label=f'Instrument {i+1}')


plt.title("Price Action of 50 Instruments Overlay")
plt.xlabel("Time Steps")
plt.ylabel("Price")
plt.legend(loc="upper left", bbox_to_anchor=(1, 1), ncol=2)
plt.grid(True)
plt.tight_layout()
plt.show()