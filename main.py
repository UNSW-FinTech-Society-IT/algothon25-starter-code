import numpy as np
from scipy.stats import zscore
from sklearn.covariance import LedoitWolf

def getMyPosition(prices):
    nInst, nt = prices.shape
    
    # Minimum data requirement
    if nt < 40:
        return np.zeros(nInst)
    
    # Calculate daily returns
    rets = np.diff(prices) / prices[:, :-1]
    
    # Initialize positions
    positions = np.zeros(nInst)
    
    # 1. Core Trend Following (more sensitive)
    trend_positions = enhanced_trend_following(prices)
    
    # 2. Mean Reversion (more selective)
    mr_positions = strict_mean_reversion(prices, rets)
    
    # 3. Combine strategies with dynamic weighting
    combined = 0.7 * trend_positions + 0.3 * mr_positions
    
    # 4. Volatility and correlation adjustment
    final_positions = adjust_for_risk(combined, prices, rets)
    
    return final_positions.astype(int)

def enhanced_trend_following(prices):
    """More sensitive trend detection with confirmation"""
    nInst, nt = prices.shape
    positions = np.zeros(nInst)
    
    for i in range(nInst):
        # Short, medium, and long-term trends
        short_term = prices[i, -10:]  # 2 weeks
        medium_term = prices[i, -40:]  # 2 months
        long_term = prices[i, -120:] if nt >= 120 else medium_term  # 6 months
        
        # Calculate smoothed trends
        short_trend = np.mean(short_term[-5:] - short_term[:5]) / np.mean(short_term)
        medium_trend = np.mean(medium_term[-20:] - medium_term[:20]) / np.mean(medium_term)
        long_trend = np.mean(long_term[-60:] - long_term[:60]) / np.mean(long_term) if nt >= 120 else medium_trend
        
        # Position sizing based on trend strength and agreement
        if (short_trend > 0.03 and medium_trend > 0.02 and long_trend > 0.01):
            positions[i] = 0.8  # Stronger long position
        elif (short_trend < -0.03 and medium_trend < -0.02 and long_trend < -0.01):
            positions[i] = -0.8  # Stronger short position
    
    return positions

def strict_mean_reversion(prices, rets):
    """Very selective mean reversion only in range-bound markets"""
    nInst, nt = prices.shape
    positions = np.zeros(nInst)
    
    if nt < 20:
        return positions
    
    for i in range(nInst):
        # Check if instrument is range-bound
        log_prices = np.log(prices[i])
        lookback = min(40, nt-1)
        delta = log_prices[-1] - np.mean(log_prices[-lookback:])
        vol = np.std(np.diff(log_prices[-lookback:]))
        
        if vol > 0:
            z_score = delta / vol
            # Only trade if in clear mean-reversion zone (1.5σ-2.5σ)
            if 1.5 < abs(z_score) < 2.5:
                positions[i] = -0.4 * np.sign(z_score)  # Moderate mean-reversion bet
    
    return positions

def adjust_for_risk(raw_positions, prices, rets):
    """Comprehensive risk adjustment with correlation control"""
    nInst = raw_positions.shape[0]
    current_prices = prices[:, -1]
    
    # 1. Volatility scaling
    if rets.shape[1] >= 20:
        vol = np.std(rets[:, -20:], axis=1)
        vol = np.maximum(vol, 0.005)  # Minimum volatility of 0.5%
        vol_scale = 0.15 / vol
        positions = raw_positions * np.minimum(vol_scale, 2)
    else:
        positions = raw_positions
    
    # 2. Correlation adjustment (reduce correlated exposures)
    if rets.shape[1] >= 40:
        cov = LedoitWolf().fit(rets[:, -40:].T).covariance_
        port_var = positions.T @ cov @ positions
        if port_var > 0.0004:  # Max portfolio variance
            positions *= np.sqrt(0.0004 / port_var)
    
    # 3. Dollar position limits ($7k max)
    dollar_positions = positions * current_prices
    dollar_positions = np.clip(dollar_positions, -7000, 7000)
    
    # 4. Portfolio-wide exposure limit ($35k)
    portfolio_exposure = np.sum(np.abs(dollar_positions))
    if portfolio_exposure > 35000:
        dollar_positions *= 35000 / portfolio_exposure
    
    # Convert back to shares
    final_positions = dollar_positions / current_prices
    
    return np.round(final_positions).astype(int)