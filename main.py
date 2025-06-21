import numpy as np
from STLT_Moving_Avg import Position_Generator
import sys

##### TODO #########################################
### IMPLEMENT 'getMyPosition' FUNCTION #############
### TO RUN, RUN 'eval.py' ##########################

# Number of instruments (stocks)
nInst = 50
# Array of zeros of length instruments
currentPos = np.zeros(nInst)


# prcSoFar is a 2d array of prices given for each stock so far
# Each row in the array are prices for a certain stock, stocks organised by rows
def getMyPosition(prcSoFar):
    return stlt_ma(prcSoFar)


def og(prcSoFar):
    global currentPos
    # nins is number of instruments, nt is days passed
    (nins, nt) = prcSoFar.shape
    if nt < 2:
        return np.zeros(nins)
    # What is goign on bro
    lastRet = np.log(prcSoFar[:, -1] / prcSoFar[:, -2])
    lNorm = np.sqrt(lastRet.dot(lastRet))
    lastRet /= lNorm
    rpos = np.array([int(x) for x in 5000 * lastRet / prcSoFar[:, -1]])
    currentPos = np.array([int(x) for x in currentPos + rpos])
    return currentPos


def init_stlt_ma(st_dur, lt_dur):
    global gen_ls
    gen_ls = [
        Position_Generator(
            short_term_duration=st_dur, long_term_duration=lt_dur
        )
        for _ in range(nInst)
    ]


# Uncomment when doing it for real
# 10 and 50 is good - 2.03 sharpe, meanpl at 74
# init_stlt_ma(10, 50)
init_stlt_ma(27, 31)


def stlt_ma(prcSoFar):
    # Create nInst number of generator objects
    final_positions = []
    for index, stock_prices in enumerate(prcSoFar):
        pos = gen_ls[index].compute_position(
            len(stock_prices) - 1, stock_prices
        )
        final_positions.append(pos)
    return np.array(final_positions)
