#!/usr/bin/env python

import numpy as np
import pandas as pd
from main import getMyPosition as getPosition
from main import *

nInst = 0
nt = 0
# commRate = 0.0005
commRate = 0
dlrPosLimit = 10000

def loadPrices(fn):
    global nt, nInst
    df=pd.read_csv(fn, sep='\s+', header=None, index_col=None)
    (nt,nInst) = df.shape
    return (df.values).T

# pricesFile="./priceSlice_test.txt"
pricesFile="prices.txt"
prcAll = loadPrices(pricesFile)
print ("Loaded %d instruments for %d days" % (nInst, nt))

def calcPL(prcHist, numTestDays):
    cash = 0
    curPos = np.zeros(nInst)
    totDVolume = 0
    totDVolumeSignal = 0
    totDVolumeRandom = 0
    value = 0
    todayPLL = []
    (_,nt) = prcHist.shape
    startDay = nt + 1 - numTestDays
    for t in range(startDay, nt+1):
        prcHistSoFar = prcHist[:,:t]
        curPrices = prcHistSoFar[:,-1]
        if (t < nt):
            # Trading, do not do it on the very last day of the test
            newPosOrig = getPosition(prcHistSoFar)
            posLimits = np.array([int(x) for x in dlrPosLimit / curPrices])
            newPos = np.clip(newPosOrig, -posLimits, posLimits)
            deltaPos = newPos - curPos
            dvolumes = curPrices * np.abs(deltaPos)
            dvolume = np.sum(dvolumes)
            totDVolume += dvolume
            comm = dvolume * commRate
            cash -= curPrices.dot(deltaPos) + comm
        else:
            newPos = np.array(curPos)
        curPos = np.array(newPos)
        posValue = curPos.dot(curPrices)
        todayPL = cash + posValue - value
        value = cash + posValue
        ret = 0.0
        if (totDVolume > 0):
            ret = value / totDVolume
        if (t > startDay):
            # print("Day %d value: %.2lf todayPL: $%.2lf $-traded: %.0lf return: %.5lf" % (t,value, todayPL, totDVolume, ret))
            todayPLL.append(todayPL)
    pll = np.array(todayPLL)
    (plmu,plstd) = (np.mean(pll), np.std(pll))
    annSharpe = 0.0
    if (plstd > 0):
        annSharpe = np.sqrt(249) * plmu / plstd
    return (plmu, ret, plstd, annSharpe, totDVolume)

# MAX_DUR = 55
MAX_DUR = 100
sharpes = []
meanpls = []
max_sharpe = float("-inf")
max_s_info = {}
max_meanpl = float("-inf")
max_m_info = {}

# Best st 27, lt 31 for stlt ma (simple)

for st_dur in range(1, MAX_DUR, 1):
    for lt_dur in range(st_dur + 1, MAX_DUR, 1):
        print(f"st_dur: {st_dur}, lt_dur: {lt_dur}")
        init_stlt_ma(st_dur, lt_dur)
        (meanpl, ret, plstd, sharpe, dvol) = calcPL(prcAll,200)
        score = meanpl - 0.1*plstd
        print("=====")
        print("mean(PL): %.1lf" % meanpl)
        # print("return: %.5lf" % ret)
        # print("StdDev(PL): %.2lf" % plstd)
        print("annSharpe(PL): %.2lf " % sharpe)
        # print("totDvolume: %.0lf " % dvol)
        # print("Score: %.2lf" % score)
        print()

        info = {"st_dur": st_dur, "lt_dur": lt_dur}
        # sharpes.append((sharpe, info))
        commRate = 0
        meanpls.append((meanpl, info))

        if max_sharpe < sharpe:
            max_s_info = info.copy()
            max_sharpe = sharpe

        if max_meanpl < meanpl:
            max_m_info = info.copy()
            max_meanpl = meanpl

        print(f"Current max sharpe: {max_sharpe} at {max_s_info}")
        print(f"Current max meanpl: {max_meanpl} at {max_m_info}")


sharpes.sort()
meanpls.sort()

with open("sharpe_temp.txt", "w") as f:
    for sharpe_info in sharpes:
        print(f"{sharpe_info[0]}|({sharpe_info[1]['st_dur']}, {sharpe_info[1]['lt_dur']})", file=f)

