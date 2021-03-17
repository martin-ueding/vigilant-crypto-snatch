# Evaluation

It is not inherently clear how triggers should be set. There are multiple variables that have to be tuned for *each* trigger:

- Time delay
- Cooloff (currently the same as time delay)
- Drop percentage
- Fiat volume

We can try to verify a given strategy using historical data. Most historic data sources only provide one number per day, whereas Cryptocompare provides it much more fine grained via the free API:

Resolution | Window | Ticks
--- | --- | ---:
Minute | 1 day | 1440
Hourly | 3 months | 2232
Daily | Full | ∞

Using a higher tier would allow longer windows for a given resolution. The number of ticks is rather low, this is something that we can sensibly download into the database.

Then we just simulate the given triggers and see how they perform.