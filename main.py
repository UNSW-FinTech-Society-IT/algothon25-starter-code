import numpy as np
from STLT_Moving_Avg import STLT_Position_Generator
from STLT_Exp_MA import STLT_Exp_Position_Generator
from Follow_The_Gradient import FTG_Position_Generator
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
    return compute_all_positions(prcSoFar)


# This will work for all our different strategies as long as you code your
# own init function
def compute_all_positions(prcSoFar):

    final_positions = []
    for index, stock_prices in enumerate(prcSoFar):
        pos = gen_ls[index].compute_position(
            len(stock_prices) - 1, stock_prices
        )
        final_positions.append(pos)
    return np.array(final_positions)


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
        STLT_Position_Generator(
            short_term_duration=st_dur, long_term_duration=lt_dur
        )
        for _ in range(nInst)
    ]


def init_ftg_ma():
    # Create nInst number of generator objects
    global gen_ls
    gen_ls = [FTG_Position_Generator() for _ in range(nInst)]


def init_stlt_exp_ma(st_dur, lt_dur):
    global gen_ls
    gen_ls = [
        STLT_Exp_Position_Generator(
            short_term_duration=st_dur, long_term_duration=lt_dur
        )
        for _ in range(nInst)
    ]


# Uncomment your strategy when you are using it

# 10 and 50 is good - 2.03 sharpe, meanpl at 74
# init_stlt_ma(10, 50)
init_stlt_ma(27, 31)

# init_ftg_ma()

# Best durations for exp: (16, 32)
# sharpe is 1.7 w/ comm otherwise 2.17

# With (7, 14):
# sharpe is 0.4 w/ comm otherwise 1.14
# init_stlt_exp_ma(16, 32)
