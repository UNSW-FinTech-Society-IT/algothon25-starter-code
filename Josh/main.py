
import numpy as np

##### TODO #########################################
### IMPLEMENT 'getMyPosition' FUNCTION #############
### TO RUN, RUN 'eval.py' ##########################

nInst = 50
currentPos = np.zeros(nInst)


def getMyPosition(prcSoFar):
    global currentPos
    (nins, nt) = prcSoFar.shape

    lookback = 5

    if (nt < lookback + 1):
        return np.zeros(nins)

    performance_signal = np.log(prcSoFar[:, -1] / prcSoFar[:, -(lookback + 1)])

    ranks = np.argsort(performance_signal)


    trade_signal = np.zeros(nins)


    top_10_indices = ranks[-20:]
    trade_signal[top_10_indices] = performance_signal[top_10_indices]


    worst_performers_indices = ranks[:nins]
    short_indices = []
    for idx in worst_performers_indices:
        if len(short_indices) >= 10:
            break
        if performance_signal[idx] < 0:
            short_indices.append(idx)

    if short_indices:
        trade_signal[short_indices] = performance_signal[short_indices]


    lNorm = np.sqrt(trade_signal.dot(trade_signal))


    if lNorm == 0:
        return currentPos

    normalized_signal = trade_signal / lNorm


    rpos = np.array([int(x) for x in 5000 * normalized_signal / prcSoFar[:, -1]])
    currentPos = np.array([int(x) for x in currentPos + rpos])

    return currentPos
