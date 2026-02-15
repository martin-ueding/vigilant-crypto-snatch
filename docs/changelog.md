# Changelog

This is a log of all changes made to the project. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- 
Types of changes

    *Added* for new features.
    *Changed* for changes in existing functionality.
    *Deprecated* for soon-to-be removed features.
    *Removed* for now removed features.
    *Fixed* for any bug fixes.
    *Security* in case of vulnerabilities.
-->

## Unreleased

### Changed

- Update dependencies completely.
- Restructure the changelog according to [Keep a Changelog](https://keepachangelog.com/).

## 5.9.3 - 2023-11-18

### Changed

- Upgrade to support Python versions from 3.9 to 3.12.

### Fixed

- Fix typing issues.
- Fix duplicate Streamlit key.

## 5.9.2 - 2022-11-07

### Removed

- Remove check for `st._is_running_with_streamlit`.

## 5.9.1 - 2022-11-07

### Changed

- Try to support both versions of Streamlit, the one with the old `streamlit.cli` and the one with the new `streamlit.web.cli` module.

## 5.9.0 - 2022-06-05

### Added

- Add a separate window to see log messages in the GUI.
- Add the trigger simulation functionality to the GUI.
- Add drop percentage to the trigger edit window in the GUI.
- Add test buttons for each tab of the configuration in the GUI.
- Add CCXT configuration to GUI.

### Changed

- Move some GUI functionality into a main menu and separate windows.
- Use PySide6 instead of PyQt6 such that the whole project is under the MIT licence again.

## 5.8.1 - 2022-06-01

### Added

- Allow setting a start date and time in the GUI.

## 5.8.0 - 2022-06-01

### Added

- Logo added to the GUI window.
- The GUI now shows a system tray icon and can send notifications.

### Changed

- All triggers now need to have an explicit name set in the configuration.
- Before a trigger is executed, the balance will be checked.
- The GUI has an improved status and about screen.

## 5.7.0 - 2022-05-29

### Added

- A completely new GUI using Qt is now part of the project.

### Fixed

- The trigger `start` attribute used to discard the time part, if it was given.

## 5.6.0 - 2022-05-07

### Added

- Add support for notifications via notify.run to provide an alternative to Telegram.

### Fixed

- Also catch `HTTPError` in the krakenex wrapper.

## 5.5.0 - 2022-02-25

### Added

- The CCXT library is now supported and gives access to more over a 100 more exchanges.
- Add an asset pair selector in the trade overview panel in the evaluation interface.

### Changed

- It is now an error when either drop percentage or delay is given, but not both at the same time.
- The `--marketplace` command line option has been removed, the marketplace is now chosen via an entry in the configuration file.

## 5.4.4 - 2022-02-11

### Fixed

- The `krakenex` library would sometimes also raise a `requests.exceptions.ReadTimeout`, which was not caught.

## 5.4.3 - 2022-01-29

### Fixed

- The database cleaning trigger would always clean all historic prices which were two hours in the past.
- The Fear and Greed index sometimes doesn't deliver a value for the current day. In this case we will try the value from yesterday.

## 5.4.2 - 2022-01-16

### Fixed

- Fix path handling to database on Windows.

## 5.4.1 - 2022-01-16

### Added

- Restore Windows support by only adding syslog on Linux.

### Changed

- Split usage documentation onto multiple pages.

### Removed

- Remove the telemetry stuff again.

## 5.4.0 - 2022-01-15

### Added

- Add optional and voluntary telemetry sending via Sentry.
- Add a dark mode to the documentation.
- Split configuration documentation onto multiple pages.

## 5.3.1 - 2022-01-15

### Fixed

- Fix bug in trade report with `KeyError: 'coin'`.

## 5.3.0 - 2022-01-14

### Added

- Add a report page about user trades into the evaluation interface.
- Link to download statistics within documentation.
- Add GitHub funding.

### Changed

- Connection errors are not reported all the time, instead they are just logged as debug output.
- Create `AssetPair` data structure so better structure the code internally.
- Update developer documentation a bit.
- Update Pillow for security.

### Removed

- Remove usage of `Protocol` such that Python 3.7 is still supported.

## 5.2.1 - 2022-01-14

### Changed

- Allow any log level for Telegram, including `debug`.
- Attempt withdrawal after the trade has been noted in the database.
- Output full exception traceback for every caught exception into the debug logging channel.
- Pause triggers for 24 hours when they have insufficient funds.

## 5.2.0 - 2021-12-22

### Added

- Fear & Greed is now included in the evaluation interface.
- Developer documentation includes a component diagram.

### Changed

- More refactoring, more test coverage.

## 5.1.0 - 2021-12-20

### Added

- Print out version number during startup.
- Add trigger option `fear_and_greed_index_below`.

## 5.0.3 - 2021-12-17

### Fixed

- Catch `requests.exceptions.ConnectionError`, which wasn't caught by the krakenex library.

## 5.0.2 - 2021-12-05

### Fixed

- The Telegram connector would hang during shutdown, I have fixed that again.

## 5.0.1 - 2021-12-03

### Fixed

- Fix bug with marketplace factory function.

## 5.0.0 - 2021-12-03

### Changed

- Refactor a lot more.

### Removed

- Remove `--keepalive` feature, this is on by default now.
- Remove `--dry-run` feature, use the `test-drive` command instead.
- Remove `--one-shot` feature, use the loop instead.

## 4.4.4 - 2021-11-16

### Added

- Add `--version` option.

### Fixed

- The Telegram sender would not shut down gracefully. I have fixed that now.

## 4.4.3 - 2021-11-15

### Fixed

- I've accidentally deleted the source code. This should be fixed now.

## 4.4.2 - 2021-11-15

### Changed

- Streamlit doesn't easily work on the Raspberry Pi due to issues with py-arrow and the ARM CPU. I have therefore reverted these dependencies to be an extra again.

## 4.4.1 - 2021-11-15

### Changed

- More refactoring. Also update the versions of various dependencies. The Streamlit interface is now part of the main dependencies.

## 4.4.0 - 2021-11-05

### Added

- Add `test-drive` command to verify configuration.

### Changed

- Major architectural change, without changes to the user.

## 4.3.5 - 2021-09-20

### Fixed

- When the balance on the marketplace is zero, withdrawals would fail and therefore crash the whole program. This is now fixed.

## 4.3.4 - 2021-08-26

### Added

- I now use the mypy static analysis and type checker, and also found a few subtle bugs with that in code paths which aren't used often.

### Fixed

- The `--dry-run` option would write buys into the database, although it would not buy anything on the market. Now the database should now be changed.

## 4.3.3 - 2021-08-12

### Fixed

- Due to an incomplete refactoring the program would crash whenever there was a non-fatal exception regarding the marketplace. This should be fixed now.

## 4.3.2 - 2021-08-02

### Changed

- Make the `marketplace` package isolated, only expose a limited set of attributes in `__init__.py`.

### Fixed

- Fix automatic detection of Telegram chat ID.
- Do not crash when there is no balance at Kraken.
- Also handle `requests.exceptions.HTTPError`.

## 4.3.1 - 2021-07-19

### Fixed

- Apparently all Kraken trades were sent in the validation mode. I have tried to fix that.

## 4.3.0 - 2021-07-16

### Added

- Add a `start` attributes to triggers.
- Add `--dry-run` option to `watch` command such that it can be tested without spending money.
- Allow specifying `delay` and `cooldown` not only in minutes as `delay_minutes` and `cooldown_minutes`, but also as `delay_hours`, `delay_days`, `cooldown_hours` and `cooldown_days`.
- Add documentation for cron to _Configuration_.
- Introduce a new pre-commit hook that sorts the import statements.

### Fixed

- Remove double reports of connection errors.
- In case that the user has no drop triggers, the database cleaning interval is set to 120 minutes.
- Handle `requests.exceptions.ConnectionError` without crashing.
- Fix `--one-shot` mode. It would previously sleep for another interval and not shut down the Telegram logger, preventing the program from a clean exit.

## 4.2.4 - 2021-06-18

### Fixed

- Also handle `ReadTimeout` errors that can happen when the API doesn't answer before the connection breaks. These have been ignored previously, but now the error message is a bit cleaner.

## 4.2.3 - 2021-06-18

### Added

- Log output is also put into the Linux system log. In this way one can do post-mortem debugging.

### Changed

- Telegram messages are no longer directly send but stored in a send-queue. This way connection outages do not yield lost messages but rather just delay sending.
- Use a proper form instead of the plain button in Streamlit.

### Fixed

- Crashes have been reported when the Telegram message was longer than their limit of 4096 characters. Messages are now chunked to prevent this from happening.

## 4.2.2 - 2021-05-25

### Fixed

- Another warning message would use a constant that was moved to another place in the meantime. The program crashed when the message was going to be emitted. It has been removed now.

## 4.2.1 - 2021-05-23

### Fixed

- When a trigger was disabled after three consecutive failures, a message stating that would be shown every time the trigger was processed. In this way the user got the same amount of messages. This message is now removed.

## 4.2.0 - 2021-05-21

### Added

- Triggers can be given names in the evaluation interface.
- For the Kraken marketplace you can now specify whether the fees should be applied to base or quote currency.
- Attach a stack trace of exceptions to the Telegram message.
- In the drop survey evaluation one now also has a time range slider such that one can get a feeling for the drops.

### Changed

- The reported balance at startup will only contain currencies which are used in triggers.
- The legend in the trigger simulation plot is shown below the plot to allow for longer trigger names without having them cropped.
- Failed triggers are just silenced for 12 hours. Another attempt is made automatically afterwards.
- `clikraken` has been retired and we now use `krakenex` in version 2.
- Send Telegram messages via POST (and not GET).
- Automatically move the SQLite database into the appropriate user data directory on Windows on macOS, no change on Linux.

### Fixed

- Historical API was broken, it now retrieves data again.
- Specifying a lower-case fiat currency and using the percentage based fiat volume strategy led to an error.
- Make sure that errors from the Telegram API are reported and not ignored.
- Do not use Markdown with Telegram as parsing errors prevent messages from being sent.
- Errors from the historical price source have been silently ignored. They now issue a warning.

## 4.1.0 - 2021-05-05

### Added

- Add automatic withdrawal for currency when the amount exceeds a certain threshold determined by the fee.

### Changed

- Use `krakenex` instead of `clikraken` to communicate with Kraken. The old implementation is deprecated but retained with `--marketplace clikraken`.

## 4.0.0 - 2021-05-04

### Changed

- The trigger specification is significantly changed. Consult the documentation to learn about the new format.

## 3.5.1 - 2021-05-03

### Fixed

- Fix drop trigger with percentage such that `volume_fiat` is actually a percentage and not a ratio (between 0 and 1).

## 3.5.0 - 2021-05-03

### Added

- Add `--one-shot` to the `watch` subcommand to only run the watch loop once.
- Add `fiat_percentage: true` option to create drop triggers that use a percentage of the available fiat balance instead of a fixed volume.

### Changed

- Update documentation and state paths to the configuration file on various platforms.

## 3.4.0 - 2021-04-27

### Added

- Query balances on the marketplace at startup and after each trade. A notification is send such that you always know how much fiat money is left to trade.
- Allow trigger evaluation on a chosen subrange of dates.
- Make plots interactive.

### Changed

- Reflect change from `XBT` to `BTC` coding on Kraken.
- In the trigger evaluation, triggers are moved to multiple rows if there are more than three of them.
- Present trigger evaluation summary as a table.

## 3.3.0 - 2021-04-23

### Added

- Emit the exchange rate in the buy notification.
- Add more documentation.
- Allow evaluation of multiple triggers at the same time.
- Add progress bars to the Streamlit interface.

### Fixed

- Fix axes label in plot.

## 3.2.0 - 2021-04-22

### Added

- Add a summary table for the drop evaluation interface.

## 3.1.0 - 2021-04-19

### Added

- Add evaluation interface powered by Streamlit.
- More documentation in general.
- Add installation instructions for the evaluation feature.

## 3.0.3 - 2021-04-05

### Changed

- Change command line argument parser back to `argparse`.

### Fixed

- Catch another connection exception.
- Catch connection errors in Telegram logger such that there are no endless recursive log messages which crash the program.
- Fix cool-off for 06:00 checkin.
- Fix some test code.

## 3.0.2 - 2021-04-01

### Fixed

- Buxfixes.

## 3.0.1 - 2021-03-28

### Added

- Perform evaluation with actual trigger implementations.

## 3.0.0 - 2021-03-27

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

## 2.1.0 - 2021-03-13

### Added

- Add regular Telegram messages to let user know that the program is still running.

## 2.0.0 - 2021-03-13

### Added

- Add a nice documentation website.
- Add log messages via Telegram.
- Add `--keepalive` option again.
- Add automatic database cleaning.

### Changed

- Use logging library for colorful log messages.
- Gracefully handle keyboard interrupt.