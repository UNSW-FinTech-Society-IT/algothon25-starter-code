'''
Current version: 1.0

import numpy as np

# number of instruments (stocks)
nInst = 50

# global variables to track current positions and how long we’ve held them
currentPos = np.zeros(nInst)
hold_days = np.zeros(nInst)

def getMyPosition(prcSoFar):
    global currentPos, hold_days
    n, t = prcSoFar.shape

    # if we don’t have enough data (less than 1 year), don’t trade
    if t < 252:
        currentPos = np.zeros(n)
        hold_days = np.zeros(n)
        return currentPos

    # === 1. check if the market is in an uptrend ===
    # we calculate the average price of all instruments
    market_prices = prcSoFar.mean(axis=0)
    # check the 21-day market return (approx. 1 trading month)
    market_return = np.log(market_prices[-1] / market_prices[-21])

    # if the market is falling, we sit out (no trades)
    if market_return <= 0:
        currentPos = np.zeros(n)
        hold_days = np.zeros(n)
        return currentPos

    # === 2. Calculate daily log returns ===
    returns = np.diff(np.log(prcSoFar), axis=1)

    # === 3. use PCA to remove the shared market effect ===
    X = returns[:, -252:]  # Use past 252 days (1 year)
    X -= X.mean(axis=1, keepdims=True)  # Demean each stock's return series
    cov = np.cov(X)  # Covariance matrix
    _, eigvecs = np.linalg.eigh(cov)  # Eigen decomposition(i, ignore the first value)
    market_pc = eigvecs[:, -1].reshape(-1, 1)  # First principal component (market direction)
    market_component = market_pc @ (market_pc.T @ X)  # Project market factor out
    residuals = X - market_component  # Leftover = unique stock behavior

    # === 4. Calculate momentum from residuals ===
    # Momentum = average residual return over past 20 days
    momentum = residuals[:, -20:].mean(axis=1)

    # === 5. Apply Z-score filtering to only keep strong momentum stocks ===
    z = (momentum - momentum.mean()) / (momentum.std() + 1e-6)
    momentum[z <= 0.4] = 0  # Filter out weak signals

    # === 6. Calculate 60-day EWMA volatility ===
    lam = 0.94  # Smoothing factor
    ewma_weights = np.power(lam, np.arange(60)[::-1])  # Higher weight to recent days
    ewma_weights /= ewma_weights.sum()
    ewma_vol = np.sqrt(np.sum((residuals[:, -60:] ** 2) * ewma_weights, axis=1) + 1e-8)

    # === 7. Filter out the most volatile stocks (top 15%) ===
    vol_cutoff = np.percentile(ewma_vol, 85)
    momentum[ewma_vol >= vol_cutoff] = 0  # Don’t trade these
    ewma_vol[ewma_vol >= vol_cutoff] = 1e6  # Prevent them from getting capital

    # === 8. Rank the momentum signals and choose top/bottom 5 ===
    ranked = np.argsort(momentum)
    longs = [i for i in ranked[::-1] if momentum[i] > 0][:5]  # Top 5
    shorts = [i for i in ranked if momentum[i] < 0][:5]       # Bottom 5

    # === 9. Allocate positions ===
    pos = np.zeros(n)
    capital = 1_000_000  # Total capital
    max_dollars = 10_000  # Max per stock

    for i in range(n):
        # === Keep current position for 1 more day if it's not in new long/short ===
        if currentPos[i] != 0 and i not in longs + shorts:
            if hold_days[i] < 2:  # If held for less than 2 days, keep it
                pos[i] = currentPos[i]
                hold_days[i] += 1
            else:
                hold_days[i] = 0  # Exit
        # === Allocate new long positions ===
        elif i in longs:
            total_inv = sum(1 / ewma_vol[j] for j in longs)
            weight = capital / (2 * total_inv)
            dollars = min(weight / ewma_vol[i], max_dollars)
            pos[i] = dollars / prcSoFar[i, -1]
            hold_days[i] = 0
        # === Allocate new short positions ===
        elif i in shorts:
            total_inv = sum(1 / ewma_vol[j] for j in shorts)
            weight = capital / (2 * total_inv)
            dollars = min(weight / ewma_vol[i], max_dollars)
            pos[i] = -dollars / prcSoFar[i, -1]
            hold_days[i] = 0
        else:
            hold_days[i] = 0  # If doing nothing, reset hold count

    # === 10. Clip and return final positions ===
    currentPos = np.clip(np.round(pos), -1000, 1000)
    return currentPos
'''

# Test

import numpy as np

# number of instruments (stocks)
nInst = 50

# global variables to track current positions and how long we’ve held them
currentPos = np.zeros(nInst)
hold_days = np.zeros(nInst)

def getMyPosition(prcSoFar):
    global currentPos, hold_days
    n, t = prcSoFar.shape

    # if we don’t have enough data (less than 1 year), don’t trade
    if t < 252:
        currentPos = np.zeros(n)
        hold_days = np.zeros(n)
        return currentPos

    # === 1. check if the market is in an uptrend ===
    # we calculate the average price of all instruments
    market_prices = prcSoFar.mean(axis=0)
    # check the 21-day market return (approx. 1 trading month)
    market_return = np.log(market_prices[-1] / market_prices[-21])

    # if the market is falling, we sit out (no trades)
    if market_return <= 0 or np.std(market_prices[-21:]) > np.std(market_prices[-252:]):
        currentPos = np.zeros(n)
        hold_days = np.zeros(n)
        return currentPos

    # === 2. Calculate daily log returns ===
    returns = np.diff(np.log(prcSoFar), axis=1)

    # === 3. use PCA to remove the shared market effect ===
    X = returns[:, -252:]  # Use past 252 days (1 year)
    X -= X.mean(axis=1, keepdims=True)  # Demean each stock's return series
    cov = np.cov(X)  # Covariance matrix
    _, eigvecs = np.linalg.eigh(cov)  # Eigen decomposition(i, ignore the first value)
    market_pc = eigvecs[:, -1].reshape(-1, 1)  # First principal component (market direction)
    market_component = market_pc @ (market_pc.T @ X)  # Project market factor out
    residuals = X - market_component  # Leftover = unique stock behavior

    # === 4. Calculate momentum from residuals ===
    # Momentum = average residual return over past 20 days
    momentum = residuals[:, -20:].mean(axis=1)

    # === 5. Apply Z-score filtering to only keep strong momentum stocks ===
    z = (momentum - momentum.mean()) / (momentum.std() + 1e-6)

    # Changed to 1 to filter out weak signals
    momentum[z <= 1.1] = 0  # Filter out weak signals

    # === 6. Calculate 60-day EWMA volatility ===
    lam = 0.94  # Smoothing factor
    ewma_weights = np.power(lam, np.arange(60)[::-1])  # Higher weight to recent days
    ewma_weights /= ewma_weights.sum()
    ewma_vol = np.sqrt(np.sum((residuals[:, -60:] ** 2) * ewma_weights, axis=1) + 1e-8)

    # === 7. Filter out the most volatile stocks (top 15%) ===
    vol_cutoff = np.percentile(ewma_vol, 85)
    momentum[ewma_vol >= vol_cutoff] = 0  # Don’t trade these
    ewma_vol[ewma_vol >= vol_cutoff] = 1e6  # Prevent them from getting capital

    # === 8. Rank the momentum signals and choose top/bottom 5 ===
    ranked = np.argsort(momentum)
    longs = [i for i in ranked[::-1] if momentum[i] > 0][:5]  # Top 5
    shorts = [i for i in ranked if momentum[i] < 0][:5]       # Bottom 5

    # === 9. Allocate positions ===
    pos = np.zeros(n)
    capital = 1_000_000  # Total capital
    max_dollars = 10_000  # Max per stock

    for i in range(n):
        # === Keep current position for 1 more day if it's not in new long/short ===
        if currentPos[i] != 0 and i not in longs + shorts:
            if hold_days[i] < 2:  # If held for less than 2 days, keep it
                pos[i] = currentPos[i]
                hold_days[i] += 1
            else:
                hold_days[i] = 0  # Exit
        # === Allocate new long positions ===
        elif i in longs:
            total_inv = sum(1 / ewma_vol[j] for j in longs)
            weight = capital / (2 * total_inv)
            dollars = min(weight / ewma_vol[i], max_dollars)
            pos[i] = dollars / prcSoFar[i, -1]
            hold_days[i] = 0
        # === Allocate new short positions ===
        elif i in shorts:
            total_inv = sum(1 / ewma_vol[j] for j in shorts)
            weight = capital / (2 * total_inv)
            dollars = min(weight / ewma_vol[i], max_dollars)
            pos[i] = -dollars / prcSoFar[i, -1]
            hold_days[i] = 0
        else:
            hold_days[i] = 0  # If doing nothing, reset hold count

    # === 10. Clip and return final positions ===
    currentPos = np.clip(np.round(pos), -1000, 1000)
    
    return currentPos

# =====
# mean(PL): 25.3
# return: 0.00419
# StdDev(PL): 168.70
# annSharpe(PL): 2.37
# totDvolume: 1201250
# Score: 8.44