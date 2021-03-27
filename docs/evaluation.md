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

## How to evaluate?

Evaluating triggers is a two stage process for every pair you want to trade. At first you generate an overview that shows you the general performance of drops over the last 3 month. To customize that you can use the following parameters:

Hours range: X-Y --> you enter the timewindow in which you plan to place triggers

drop range: x-y --> you enter the drop range that interests you. Default is 0-35%

granularity: X --> enter the number of steps you want the drop range to have. More steps take more time to calculate (only applies to low power systems)

In the second step you set up triggers in the config file as described before. After the you use the command ..... to test this triggers on the data of the past 3 month.

The report will show you several things:

1) how much the triggers invested in total
2) the amount crypto bought 
3) a graph with indications when triggers where fired
4) how much crypto per fiat a trigger was able to buy (efficiancy measure)
5) more.....?