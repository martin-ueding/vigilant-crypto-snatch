# Running

From this directory you can just do `poetry run vigilant-crypto-snatch [options]` to run it. You can pass additional options, if you want. With the `--help` option you will see an up-to-date list of options.

When you want to quit press 

<kbd>Ctrl</kbd>+<kbd>C</kbd>.

All historical price data and performed transactions will be stored in a SQLite database at `~/.local/share/vigilant-crypto-snatch/db.sqlite`. We sometimes change the database format between major releases. In that case it is easiest to delete the database and let the script create the new one. As there are only so few users, we don't offer proper database migrations.