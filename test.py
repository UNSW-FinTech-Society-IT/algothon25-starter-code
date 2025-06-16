import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt('prices.txt')

num_cols = len(data[0])
print(num_cols)

for i in range(num_cols):
    plt.figure()
    plt.plot(data[:, i])
    plt.title(f'{i}th Column Values from prices.txt')
    plt.xlabel('Time')
    plt.ylabel('Price Value')
    plt.grid(True)

plt.show()