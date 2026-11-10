# v16n-6 explorer notes (30/30 experiments used)

Seed area: equity-index-cross-asset. Screens: `--null-seeds 0 --mode dev`, stressed costs.
No 200-seed nulls, no sealed submissions (0/6 pool used by this agent).

## Falsified families (era blocks all <= 0, dev_score 0)
| family | symbol | era0 / era1 / era2 | note |
|---|---|---|---|
| equity-rates-divergence-reversion | MES+ZN | 0 / -2003 / -80146 | reversion dies in modern era |
| equity-index-leadlag-confirmation | ES+ZN | -376k / -614k / -722k | lead-lag confirm net loser |
| equity-fx-risk-barometer | ES+6E | -78k / -153k / -168k | also entry-diversity fail |
| equity-index-pair-dispersion | ES+NQ | -24k / -62k / -199k | 1m spread re-entry churn |
| opening-range-breakout | ES | -29k / -37k / -11k | costs dominate |
| equity-overnight-gap-continuation | ES | -5.2k / -1.6k / -10.3k | weak, negative |
| energy-eia-inventory-drift | CL | -6.2k / -10.6k / -32.4k | 08:30 CT release, no drift |
| tod-seasonality-allasset | HG | -59k / -65k / -54k | every era negative |
| index-pdh-pdl-sweep-revert | ES | -17.6k / -31.1k / -38.7k | sweep-and-revert fails 1m |
| ng-eia-release-impulse/reversal | NG | all negative | 3c stop too tight for release vol |
| qg-eia-release-reversal | QG | -25k / -38k / -29k | reversal dead even wide stop |
| rates-auction-post-drift/reversal | ZN | all ~-50k to -66k | both directions lose to cost |
| fx-london-fix-reversal/continuation | 6E | -101k..-33k | fix flow does not survive slippage |
| grain-usda-report-reversal/continuation | ZC | -4k..-11k | generic first-Friday proxy dead |

## Near-misses (not eligible, no nomination)
- `xasset-6e-m2k-lead-follow` (M2K/6E): dev 0.0293, era2 +1113, but era0/era1 empty (M2K pre-2019)
  and only 1 positive year.
- `xasset-6e-rty-lead-follow` (RTY/6E): dev 0.0102, era1 +5697, era2 -7380.
- `index-gapdown-buy-rth` (ES/NQ/YM): era0 +16.0k, era1 +21.4k, era2 -50.0k. Regime-fragile.
- `energy-rb-daily-momentum-filter` (RB): dev 0.0053, all eras negative post-cost.

## Conclusions for the swarm
1. 1-minute 2-leg spreads (ES/NQ, MES/ZN, ES/6E) pay 2x stressed cost per re-entry; signal must be
   slow AND state-persistent, not z-score triggered.
2. Scheduled-release direction (EIA, auction, fix, USDA) is fully priced inside the release minute.
3. Sub-era stability, not average PnL, kills candidates: gap-down buy and 6E/RTY look fine on 2 of 3
   blocks and lose the third.
