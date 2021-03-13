# Running

If you have installed it system-wide, you can just execute `vigilant-crypto-snatch [options]` to run it. You can pass additional options, if you want. With the `--help` option you will see an up-to-date list of options.

When you want to quit, just press <kbd>Ctrl</kbd>+<kbd>C</kbd>.

All historical price data and performed transactions will be stored in a SQLite database at `~/.local/share/vigilant-crypto-snatch/db.sqlite`. We sometimes change the database format between major releases. In that case it is easiest to delete the database and let the script create the new one. As there are only so few users, we don't offer proper database migrations.

## Notifications

The program can emit a lot of status output while running. You can specify a *log level* with `--loglevel LEVEL`, where `LEVEL` can be `critical`, `error`, `warning`, `info` or `debug`. The `info` level is the default and does not fill the terminal with tons of output. You can set it to `debug` if you want to have more output and want to diagnose your triggers.

### Telegram

If the Telegram bot token is set up correctly, you will receive messages like this:

> ![](telegram-output.png)

The severity of messages is color-coded with an emoji according to this mapping:

Symbol | Severity
:---: | :---
🔴 | Critical
🟠 | Error
🟡 | Warning
🟢 | Info
🔵 | Debug

The logging level is set to *Info* by default. You must not set it to *Debug* as sending a Telegram message will produce more debug messages. The program will crash with an infinite recursion.

## Keepalive mode

We have tried to handle various error conditions that can happen. For instance the API of the marketplace could reject the query. During development we have tried to trigger various errors and handle them. From production runs we know that sometimes there API outages, internet connection glitches and the like. In these cases exception types that we haven't handled yet are raised. These crash normally crash the program, and we would like to ask you to [file a bug report](https://github.com/martin-ueding/vigilant-crypto-snatch/issues) then.

In order to have it stay running in production you can use the `--keepalive` flag. It will just catch *all* exception types. This may hide some actual errors. So please still report these errors as tickets.

## Nonce rejections with Kraken

If you happen to get nonce errors with the Kraken marketplace, consider using less triggers for it, or modifying your API key according to [their guide](https://support.kraken.com/hc/en-us/articles/360001148063-Why-am-I-getting-Invalid-Nonce-Errors-)