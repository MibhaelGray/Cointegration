1. Initial Setup: Two-Year Data WindowApproach:

Download 2 years of daily log price data for each basket
Use the most recent 12 months (252 trading days) to estimate initial cointegrating vectors
Store the remaining year of historical data for future rolling window calculations
Rationale:

The 2-year download provides 12 months of "buffer" for monthly re-estimations without requiring fresh data downloads
Using 1 year (252 trading days) for estimation balances statistical reliability with adaptability to recent market conditions
Log prices are used because cointegration theory applies to I(1) processes, and log prices better represent proportional relationships between stocks
Implementation:

Run Johansen cointegration test (det_order=0, k_ar_diff=5) on the most recent year
Extract the first cointegrating vector (eigenvector with largest eigenvalue)
Save weights
2. Cointegration Testing ParametersJohansen Test Settings:

det_order = 0: Assumes constant-only deterministic trend (standard for equity baskets)
k_ar_diff = 5: Uses 5 lags in the VECM, capturing approximately one week of short-run dynamics
Confidence level = 95%: Uses the middle column of critical values (crit_level=1)
Why These Parameters:

det_order=0 assumes the spread oscillates around a constant mean (not trending), appropriate for mean reversion trading
k_ar_diff=5 captures weekly autocorrelation patterns in daily stock data without overfitting
95% confidence balances Type I and Type II errors for practical trading applications
3. Stability Monitoring: The Three-Status SystemThe system classifies each basket into one of three states:✅ STABLE
Criteria:

Cointegration rank ≥ original rank on recent data
Maximum weight change < 40% from original estimation
Recent 6-month test confirms cointegration still holds
Action: Safe to use for trading signals⚠️ UNSTABLE
Criteria:

Cointegration rank maintained BUT
Any single weight has changed by ≥40% from original estimation
Action: Use extreme caution. The relationship exists but is evolving. Signals may be less reliable.❌ BROKEN
Criteria:

Cointegration rank drops to 0 on recent data OR
Johansen test fails on recent 6-month window
Action: Stop trading immediately. The long-run equilibrium relationship has dissolved.4. Stability Testing ProtocolTest Window: Most recent 6 months (126 trading days)Rationale:

6. months provides sufficient observations for reliable Johansen testing (~126 data points)
Recent enough to catch regime changes quickly
Not so short that temporary volatility triggers false breakdowns
Process:

Download fresh 1-year data
Extract most recent 6 months
Run Johansen test on this subset
Compare new rank and weights to baseline
Update status accordingly
Frequency: Monthly (on the 1st of each month, or whenever user initiates check)5. Weight Re-estimation: Rolling Window ApproachWhen: Monthly, but only if basket remains STABLE or UNSTABLE (not BROKEN)Window: Rolling 1-year (252 trading days)Process:

Month 1: Estimate on most recent 12 months of the 2-year dataset
Month 2: Estimate on months 2-13 (drop month 1, add new month's data)
Month 12: Download fresh 2 years of data and restart cycle
Why Rolling vs. Expanding:

Rolling adapts to changing market regimes by discarding old data
Expanding would give excessive weight to ancient history where relationships may have been different
1-year window balances stability (enough data) with adaptability (recent enough)
Weight Change Threshold: 40%

Conservative enough to avoid false alarms from normal variation
Aggressive enough to catch meaningful relationship changes
If any single stock's weight changes by >40%, the basket is flagged UNSTABLE
6. Spread Calculation and Signal GenerationSpread Formula:
Spread(t) = w₁ × log(Stock₁) + w₂ × log(Stock₂) + ... + wₙ × log(Stockₙ)Where weights (w₁, w₂, ..., wₙ) come from the first cointegrating eigenvector.Statistical Measures (both calculated):
Z-Score (for quick reference):

Z = (Current Spread - Rolling Mean) / Rolling Std Dev
Window: 60 days (configurable)
Limitation: Assumes normal distribution (often violated in financial data)



Percentile Rank (primary signal):

Compare current spread to distribution of last 60 days
Non-parametric, robust to fat tails and skewness
Preferred for actual trading decisions


Signal Thresholds:

BUY Signal: Spread below 10th percentile (spread unusually low)
SELL Signal: Spread above 90th percentile (spread unusually high)
NEUTRAL: Between 10th-90th percentile
Why Percentiles Over Z-Scores:

Financial data has fat tails (extreme events more common than normal distribution predicts)
Percentiles make no distributional assumptions
"5th percentile" is clearer than "2 standard deviations" for non-statisticians
