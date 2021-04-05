# Usage

The program has a hierarchical command line interface with multiple subcommands. If you have installed it system-wide, you can just directly call it. Otherwise you might have to add `~/.local/bin` to your `PATH` variable. With the `--help` option you will see an up-to-date list of options.

The general structure of a call is this:

```
vigilant-crypto-snatch [genereal options] subcommand [subcommand options]
```

The general options are the following:

- `--loglevel`: The program can emit a lot of status output while running. You can specify a *log level* with `--loglevel LEVEL`, where `LEVEL` can be `critical`, `error`, `warning`, `info` or `debug`. The `info` level is the default and does not fill the terminal with tons of output. You can set it to `debug` if you want to have more output and want to diagnose your triggers.

## Subcommand watch

The main command is `watch`.  It will monitor the market and place buy orders.

There are a couple of command line options:

- `--marketplace MARKETPLACE`: We support two marketplaces, you can select either `bitstamp` or `kraken`.
- `--keepalive`: The program handles various error cases. Sometimes there are exceptions that we haven't encountered yet. When you use the watch subcommand in production, you can specify this option. It will catch *any* exception and just report it. Please [open a ticket](https://github.com/martin-ueding/vigilant-crypto-snatch/issues) when you encounter a new exception type.

When you want to quit, just press <kbd>Ctrl</kbd>+<kbd>C</kbd>.

All historical price data and performed transactions will be stored in a SQLite database at `~/.local/share/vigilant-crypto-snatch/db.sqlite`. We sometimes change the database format between major releases. In that case it is easiest to delete the database and let the script create the new one. As there are only so few users, we don't offer proper database migrations.

An example for running the script with log level info on Kraken:

```
vigilant-crypto-snatch --loglevel info watch --marketplace kraken --keepalive
```

### Nonce rejections with Kraken

If you happen to get nonce errors with the Kraken marketplace, consider using less triggers for it, or modifying your API key according to [their guide](https://support.kraken.com/hc/en-us/articles/360001148063-Why-am-I-getting-Invalid-Nonce-Errors-)

## Subcommand evaluate

It is not inherently clear how triggers should be set. There are multiple variables that have to be tuned for *each* trigger:

- Time delay
- Cooloff (currently the same as time delay)
- Drop percentage
- Fiat volume

We can try to verify a given strategy using historical data. We can also use the historical data to get an idea of a good strategy.

Then we just simulate the given triggers and see how they perform.

### How to evaluate?

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