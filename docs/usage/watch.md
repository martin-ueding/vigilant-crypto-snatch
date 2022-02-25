# Subcommand watch

The main command is `watch`.  It will monitor the market and place buy orders.

When you want to quit, just press <kbd>Ctrl</kbd>+<kbd>C</kbd>.

All historical price data and performed transactions will be stored in a SQLite database at `~/.local/share/vigilant-crypto-snatch/db.sqlite` (elsewhere on Windows). We sometimes change the database format between major releases. In that case it is easiest to delete the database and let the script create the new one. As there are only so few users, we don't offer proper database migrations.

An example for running the script with log level “info”:

```
vigilant-crypto-snatch --loglevel info watch
```

## Nonce rejections with Kraken

If you happen to get nonce errors with the Kraken marketplace, consider using less triggers for it, or modifying your API key according to [their guide](https://support.kraken.com/hc/en-us/articles/360001148063-Why-am-I-getting-Invalid-Nonce-Errors-).

