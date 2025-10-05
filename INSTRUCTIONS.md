The Definitive Strategy: A Phased Approach
Based on everything we've discussed, here's what I believe is the optimal path forward. This combines statistical rigor with practical tradability.

Phase 1: Basket Construction (Week 1)
Use Domain Knowledge, Not Clustering
Create 6-8 sector baskets based on business model similarity, not statistical clustering:
Examples:

GPU/AI Compute: AMD, NVDA, AVGO (tight group)
Cloud Infrastructure: SNOW, NET, DDOG, CFLT, ESTC, GTLB
Cybersecurity: CRWD, ZS, PANW, OKTA, FTNT
Enterprise SaaS: CRM, NOW, WDAY, TEAM, HUBS
Traditional Semiconductors: INTC, TXN, QCOM, MRVL, ADI
Memory/Foundry: MU, TSM
Digital Advertising: TTD, TRADE, ROKU, META
Payments: PYPL, SQ, ADBE (payment processing angle)

Key principles:

Keep baskets focused (5-10 stocks each, not 30)
Shared economic drivers matter more than price correlation
Some stocks can appear in multiple baskets (MSFT could be in both cloud and enterprise)
Don't force every stock into a basket - some don't belong anywhere

Why This Works
Companies with similar business models are more likely to be cointegrated because:

They respond to the same fundamental drivers
Market re-ratings affect them similarly
Their long-term growth trajectories are linked
Institutional investors view them as substitutes

This is the intellectual foundation that clustering cannot provide.

Phase 2: Validation with Johansen (Week 1-2)
For Each Basket, Run Johansen Test
This is your reality check, not your trading methodology.
What you're looking for:

Rank ≥ 1: Confirms cointegration exists in this group
Rank = 0: Basket is flawed, stocks don't share long-run equilibrium
The first cointegrating vector: Shows you which stocks are most tightly linked

Actionable insights:
If you test your "Cloud Infrastructure" basket (SNOW, NET, DDOG, CFLT, ESTC, GTLB) and Johansen says:

Rank = 3: Great! Strong cointegration structure
Look at Vector 1: Maybe it heavily weights SNOW, NET, DDOG with large coefficients
Conclusion: These 3 are the "core" of the basket

If Johansen says rank = 0:

Your basket is wrong
These stocks don't share equilibrium relationships
Restructure or abandon this group

Key Decision Point
After Johansen, you might discover:

Some baskets have strong cointegration (rank = 2-4)
Some have weak/no cointegration (rank = 0-1)
Only proceed with baskets that show rank ≥ 1

You might start with 8 baskets and end with 5 viable ones. That's good - you've filtered out noise.

Phase 3: Individual Stock Testing (Week 2)
For Each Viable Basket, Test Each Stock vs. Basket
This is where you build your actual trading universe.
The process:
For the Cloud Infrastructure basket with stocks [SNOW, NET, DDOG, CFLT, ESTC, GTLB]:
Test SNOW:

Create basket excluding SNOW: equal-weighted average of log(NET, DDOG, CFLT, ESTC, GTLB)
Run Engle-Granger cointegration test: SNOW vs. Basket_excluding_SNOW
Record: p-value, cointegration coefficient (beta), half-life of mean reversion

Test NET:

Create basket excluding NET: equal-weighted average of log(SNOW, DDOG, CFLT, ESTC, GTLB)
Run test: NET vs. Basket_excluding_NET
Record statistics

Repeat for all stocks in all baskets.
Why Exclude the Stock Being Tested?
Critical for avoiding spurious results:

If SNOW is 50% of your basket, you're testing SNOW vs. (50% SNOW + 50% others)
This creates mechanical correlation and inflates your statistics
Excluding ensures you're testing against truly independent variation

Multiple Testing Correction
If you test 60 stocks across all baskets:

With p = 0.05, you'd expect 3 false positives by chance
Use Bonferroni correction: adjusted p-value = 0.05 / 60 = 0.00083
Or use False Discovery Rate (FDR) for less conservative filtering
Only keep stocks where corrected p-value indicates cointegration

You might end up with 30-40 stocks that pass. Good. These are your tradeable universe.

Phase 4: Spread Construction & Characterization (Week 3)
For Each Cointegrated Stock-Basket Pair
Now you need to understand the equilibrium relationship deeply.
Calculate the spread:
Spread = Stock_price - β * Basket_price
Where β comes from your cointegration test (the hedge ratio).
Analyze Each Spread's Properties
1. Stationarity verification:

Run ADF test on the spread itself
Should be stationary (p < 0.01)
If not, the cointegration is weak - consider dropping

2. Half-life of mean reversion:

How long does it take for spread to return to mean?
Calculate using AR(1) model on the spread
Critical metric: tells you expected holding period
Half-life of 5 days = fast mean reversion, tradeable
Half-life of 50 days = slow, might not be practical

3. Spread volatility:

Standard deviation of the spread
This determines your position sizing
Higher volatility = smaller positions

4. Historical z-score distribution:

Calculate rolling z-scores: (spread - mean) / std
Look at the distribution
This tells you what's "normal" vs. "divergent"

Build a Profile for Each Stock
You should end up with a spreadsheet like:
StockBasketBetap-valueHalf-lifeSpread StdMax Z-score (2y)SNOWCloud1.230.00038 days2.503.2NETCloud0.870.00016 days1.802.8CRWDSecurity1.150.000512 days3.104.1
This becomes your trading database.

Phase 5: Define Divergence Criteria (Week 3-4)
What Constitutes a "Divergence Signal"?
This is where strategy meets statistics. You need clear rules.
Option 1: Simple Z-score Threshold

Signal when |z-score| > 2.0
More conservative: > 2.5
This assumes normal distribution

Option 2: Percentile-based

Signal when spread exceeds 95th percentile (or falls below 5th)
Better for non-normal distributions
Use historical percentiles from your 2-year lookback

Option 3: Bollinger Band Style

Upper/lower bands at ±2 standard deviations
Signal when spread crosses bands
Recalculate bands on rolling 60-day window

Option 4: Multi-factor Confirmation

Z-score > 2.0 AND
Spread moved >1.5 std in last 3 days AND
Stock-specific news/catalyst (qualitative overlay)

My recommendation: Start with Option 2 (percentile-based)

More robust to fat tails and outliers
Easier to backtest
Can layer on additional filters later

Direction Matters
When SNOW diverges upward (z-score = +2.5):

SNOW has run ahead of its basket
This is a fade signal (expect mean reversion downward)
Not necessarily a short signal - could just avoid/reduce longs

When SNOW diverges downward (z-score = -2.5):

SNOW has lagged its basket
This is a potential long (expect catch-up)

Holding Period Logic
Based on half-life:

If half-life = 8 days, expect mean reversion within 8-16 days
Set maximum holding period = 2-3x half-life
If no reversion by then, exit regardless (relationship may have broken)


Phase 6: Backtesting Framework (Week 4-6)
Before You Trade Real Money
You need to validate this actually works historically.
Out-of-sample testing approach:

Estimate cointegration relationships on 2020-2022 data
Test signals on 2023-2024 data
Did the relationships hold? Did divergences revert?

Walk-forward analysis:

Re-estimate cointegration every 6 months
Test if relationships are stable
If a stock-basket pair breaks cointegration (p-value rises), stop trading it

Key metrics to track:

Hit rate: % of divergence signals that mean-revert within 2x half-life
Average reversion magnitude: How much spread closes on winners
Max drawdown per signal: Worst case before reversion
False signals: Divergences that keep diverging (relationship broke)

Expected Reality Check
Don't expect:

80% win rate
Immediate mean reversion
Every signal to work

Do expect:

55-65% hit rate if you're doing this well
Some large losses when relationships permanently break
Long periods of no signals

If backtesting shows < 50% hit rate or negative expectancy, your baskets are wrong.

Phase 7: Operational Setup (Week 6-8)
Daily Monitoring System
You need automation here. Manual tracking of 30-40 spreads daily is not sustainable.
What to track each day:

Update basket prices (recalculate equal-weighted log price for each basket)
Update all spreads (stock - β*basket for each pair)
Calculate current z-scores
Flag new divergences (crossed threshold)
Monitor existing positions (has spread reverted? Exit?)

Position Management Rules
Entry:

Wait for confirmation (z-score > threshold for 2 consecutive days)
Avoids whipsaws from intraday noise

Sizing:

Smaller positions for higher volatility spreads
Inverse relationship: position_size ∝ 1 / spread_volatility

Exit:

Spread reverts to ±0.5 z-score (take profit)
OR 3x half-life passes (stop loss on time)
OR cointegration relationship breaks in rolling test (emergency exit)

Risk management:

Max 5-10 positions at once (diversification across baskets)
No more than 2 positions in same basket (correlated risk)
Daily stop-loss per position (if spread moves another 1 std against you)


Phase 8: Rolling Validation (Ongoing)
Cointegration Relationships Are Not Permanent
This is the most important operational point: you must continuously verify relationships haven't broken.
Monthly tasks:

Re-run cointegration tests on trailing 2-year window
Check if p-values still indicate cointegration
Flag any pairs where p-value > 0.05

Quarterly tasks:

Re-run full Johansen tests on baskets
See if rank has changed
Adjust baskets if necessary (drop stocks, add new ones)

Annual tasks:

Complete restructuring
Evaluate if sector definitions still make sense
Add new IPOs or newly liquid stocks
Remove stocks that have fundamentally changed

Warning Signs a Relationship Has Broken

P-value rises above 0.05 in rolling test
Half-life extends beyond 30 days (mean reversion too slow)
Multiple failed signals (divergences that don't revert)
Fundamental change (merger, business model pivot)

When this happens: stop trading that pair immediately.