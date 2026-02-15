# Version 3

## [3.5.1] - 2021-05-03

### Fixed

- Fix drop trigger with percentage such that `volume_fiat` is actually a percentage and not a ratio (between 0 and 1).

## [3.5.0] - 2021-05-03

### Added

- Add `--one-shot` to the `watch` subcommand to only run the watch loop once.
- Add `fiat_percentage: true` option to create drop triggers that use a percentage of the available fiat balance instead of a fixed volume.

### Changed

- Update documentation and state paths to the configuration file on various platforms.

## [3.4.0] - 2021-04-27

### Added

- Query balances on the marketplace at startup and after each trade. A notification is send such that you always know how much fiat money is left to trade.
- Allow trigger evaluation on a chosen subrange of dates.
- Make plots interactive.

### Changed

- Reflect change from `XBT` to `BTC` coding on Kraken.
- In the trigger evaluation, triggers are moved to multiple rows if there are more than three of them.
- Present trigger evaluation summary as a table.

## [3.3.0] - 2021-04-23

### Added

- Emit the exchange rate in the buy notification.
- Add more documentation.
- Allow evaluation of multiple triggers at the same time.
- Add progress bars to the Streamlit interface.

### Fixed

- Fix axes label in plot.

## [3.2.0] - 2021-04-22

### Added

- Add a summary table for the drop evaluation interface.

## [3.1.0] - 2021-04-19

### Added

- Add evaluation interface powered by Streamlit.
- More documentation in general.
- Add installation instructions for the evaluation feature.

## [3.0.3] - 2021-04-05

### Changed

- Change command line argument parser back to `argparse`.

### Fixed

- Catch another connection exception.
- Catch connection errors in Telegram logger such that there are no endless recursive log messages which crash the program.
- Fix cool-off for 06:00 checkin.
- Fix some test code.

## [3.0.2] - 2021-04-01

### Fixed

- Buxfixes.

## [3.0.1] - 2021-03-28

### Added

- Perform evaluation with actual trigger implementations.

## [3.0.0] - 2021-03-27

### Added

- Add Windows support.
- Read Telegram chat ID from configuration file if available. This way you only have to send it a message once.
- More documentation.
- Add donation page.
- Start with Pytest unittests.

### Changed

- Move configuration file to a new location. Old configuration files are automatically moved.
- Import modules only when needed to speed up start-up.
- Use the *Black* code formatter.
- Implement command line interface with Click.
