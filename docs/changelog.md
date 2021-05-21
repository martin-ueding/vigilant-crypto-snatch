# Changelog

This is a list of changes, from new to older.

## 4.0 Series

### Version 4.2.0 (Upcoming)

- Triggers can be given names in the evaluation interface.
- The legend in the trigger simulation plot is shown below the plot to allow for longer trigger names without having them cropped.
- Historical API was broken, it now retrieves data again.
- `clikraken` has been retired and we now use `krakenex` in version 2.
- For the Kraken marketplace you can now specify whether the fees should be applied to base or quote currency.
- Specifying a lower-case fiat currency and using the percentage based fiat volume strategy led to an error. This is now fixed and the fiat currency is again case-insensitive.

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