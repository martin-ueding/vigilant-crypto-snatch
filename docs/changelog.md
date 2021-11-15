# Changelog

This is a list of changes, from new to older.

## 4.0 Series

### Version 4.4.1

- More refactoring. Also update the versions of various dependencies.

### Version 4.4.0

- Major architectural change, without changes to the user.
- Add `test-drive` command to verify configuration.

### Version 4.3.5

- When the balance on the marketplace is zero, withdrawals would fail and therefore crash the whole program. This is now fixed.

### Version 4.3.4

- The `--dry-run` option would write buys into the database, although it would not buy anything on the market. Now the database should now be changed. If you need to clean up your database, you might find [sqliteman](https://sourceforge.net/projects/sqliteman/) helpful for that.
- I now use the mypy static analysis and type checker, and also found a few subtle bugs with that in code paths which aren't used often.

### Version 4.3.3

Fixes:

- Due to an incomplete refactoring the program would crash whenever there was a non-fatal exception regarding the marketplace. This should be fixed now.

### Version 4.3.2

Fixes:

- Fix automatic detection of Telegram chat ID.
- Do not crash when there is no balance at Kraken.
- Also handle `requests.exceptions.HTTPError`.

Development:

- Make the `marketplace` package isolated, only expose a limited set of attributes in `__init__.py`.

### Version 4.3.1

Fixes:

- Apparently all Kraken trades were sent in the validation mode. I have tried to fix that.

### Version 4.3.0

New features:

- Add a `start` attributes to triggers.
- Add `--dry-run` option to `watch` command such that it can be tested without spending money.
- Allow specifying `delay` and `cooldown` not only in minutes as `delay_minutes` and `cooldown_minutes`, but also as `delay_hours`, `delay_days`, `cooldown_hours` and `cooldown_days`.
- Add documentation for cron to _Configuration_.

Fixes:

- Remove double reports of connection errors.
- In case that the user has no drop triggers, the database cleaning interval is set to 120 minutes.
- Handle `requests.exceptions.ConnectionError` without crashing.
- Fix `--one-shot` mode. It would previously sleep for another interval and not shut down the Telegram logger, preventing the program from a clean exit.

Development:

- Introduce a new pre-commit hook that sorts the import statements.

### Version 4.2.4

- Also handle `ReadTimeout` errors that can happen when the API doesn't answer before the connection breaks. These have been ignored previously, but now the error message is a bit cleaner.

### Version 4.2.3

- Log output is also put into the Linux system log. In this way one can do post-mortem debugging.
- Crashes have been reported when the Telegram message was longer than their limit of 4096 characters. Messages are now chunked to prevent this from happening.
- Telegram messages are no longer directly send but stored in a send-queue. This way connection outages do not yield lost messages but rather just delay sending.
- Use a proper form instead of the plain button in Streamlit.

### Version 4.2.2

- Another warning message would use a constant that was moved to another place in the meantime. The program crashed when the message was going to be emitted. It has been removed now.

### Version 4.2.1

- When a trigger was disabled after three consecutive failures, a message stating that would be shown every time the trigger was processed. In this way the user got the same amount of messages. This message is now removed. The initial errors speak for themselves, there is no need to have this additional message.

### Version 4.2.0

🧪 New features:

- Triggers can be given names in the evaluation interface.
- For the Kraken marketplace you can now specify whether the fees should be applied to base or quote currency.
- Attach a stack trace of exceptions to the Telegram message.
- In the drop survey evaluation one now also has a time range slider such that one can get a feeling for the drops. Some are one-time events, and others are regular patterns.

🔧 Improvements:

- The reported balance at startup will only contain currencies which are used in triggers. This will remove some leftover shitcoins that people might left in their account. After a trade only the balances for that currency pair will be reported to give a cleaner report.
- The legend in the trigger simulation plot is shown below the plot to allow for longer trigger names without having them cropped.
- Triggers with failures used to get deactivated completely. Once no more triggers were active, the program was shut down. Failures stemming from insufficient funds are easily recovered from by transferring more money to the marketplace. The bot would have to be restarted afterwards. In order to make this unnecessary, failed triggers are just silenced for 12 hours. Another attempt is made automatically afterwards. This keeps the number of messages relatively low.

🪲 Bug fixes:

- Historical API was broken, it now retrieves data again.
- Specifying a lower-case fiat currency and using the percentage based fiat volume strategy led to an error. This is now fixed and the fiat currency is again case-insensitive.
- Make sure that errors from the Telegram API are reported and not ignored.
- Do not use Markdown with Telegram as parsing errors prevent messages from being sent. Plain text is not as pretty, but better have it reliable no matter which names the Triggers have.
- Errors from the historical price source have been silently ignored. They now issue a warning.

⚙️ Implementation details:

- `clikraken` has been retired and we now use `krakenex` in version 2. This version is in conflice with `clikraken`, which needs `krakenex` version 1. When you upgrade, you might see this message:

    ```
    ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
clikraken 0.8.3.2 requires krakenex<1.0,>=0.1, but you have krakenex 2.1.0 which is incompatible.
    ```

    To resolve this, run `pip uninstall clikraken` or `sudo pip uninstall clikraken`, depending on whether you have installed it with `--user` in the past.

- Send Telegram messages via POST (and not GET).
- Automatically move the SQLite database into the appropriate user data directory on Windows on macOS, no change on Linux.

### Version 4.1.0

- Use [`krakenex`](https://github.com/veox/python3-krakenex) instead of [`clikraken`](https://github.com/zertrin/clikraken) to communicate with Kraken. The old implementation is deprecated but retained with `--marketplace clikraken`.
- Add automatic withdrawal for currency when the amount exceeds a certain threshold determined by the fee. See the configuration of the Kraken marketplace for details.

### Version 4.0.0

- The trigger specification is significantly changed. Consult the documentation to learn about the new format. I'm sorry for breaking your configuration, but I didn't want to provide a migration and rather deliver more new features.

## 3.0 Series

### Version 3.5.1

- Fix drop trigger with percentage such that `volume_fiat` is actually a percentage and not a ratio (between 0 and 1).

### Version 3.5.0

- Add `--one-shot` to the `watch` subcommand to only run the watch loop once.
- Update documentation and state paths to the configuration file on various platforms.
- Add `fiat_percentage: true` option to create drop triggers that use a percentage of the available fiat balance instead of a fixed volume.

### Version 3.4.0

- Reflect change from `XBT` to `BTC` coding on Kraken.
- Query balances on the marketplace at startup and after each trade. A notification is send such that you always know how much fiat money is left to trade.
- In the trigger evaluation, triggers are moved to multiple rows if there are more than three of them.
- Allow trigger evaluation on a chosen subrange of dates.
- Present trigger evaluation summary as a table.
- Make plots interactive.

### Version 3.3.0

- Emit the exchange rate in the buy notification.
- Add more documentation.
- Fix axes label in plot.
- Allow evaluation of multiple triggers at the same time.
- Add progress bars to the Streamlit interface.

### Version 3.2.0

- Add a summary table for the drop evaluation interface.

### Version 3.1.0

- Add evaluation interface powered by Streamlit.
- More documentation in general.
- Add installation instructions for the evaluation feature.

### Version 3.0.3

- Change command line argument parser back to `argparse`.
- Catch another connection exception.
- Catch connection errors in Telegram logger such that there are no endless recursive log messages which crash the program.
- Fix cool-off for 06:00 checkin.
- Fix some test code.

### Version 3.0.2

- Buxfixes.

### Version 3.0.1

- Perform evaluation with actual trigger implementations.

### Version 3.0.0

- Add Windows support.
- Move configuration file to a new location. Old configuration files are automatically moved.
- Read Telegram chat ID from configuration file if available. This way you only have to send it a message once.
- Import modules only when needed to speed up start-up.

- More documentation.
- Add donation page.
- Use the *Black* code formatter.
- Start with Pytest unittests.
- Implement command line interface with Click.

## 2.0 Series

### Version 2.1.0

- Add regular Telegram messages to let user know that the program is still running.

### Version 2.0.0

- Use logging library for colorful log messages.
- Add a nice documentation website.
- Add log messages via Telegram.
- Gracefully handle keyboard interrupt.
- Add `--keepalive` option again.
- Add automatic database cleaning.
