# Version 5

## [5.9.3] - 2023-11-18

### Changed

- Upgrade to support Python versions from 3.9 to 3.12.
- Update dependencies completely.

### Fixed

- Fix typing issues.
- Fix duplicate Streamlit key.

## [5.9.2] - 2022-11-07

### Removed

- Remove check for `st._is_running_with_streamlit`.

## [5.9.1] - 2022-11-07

### Changed

- Try to support both versions of Streamlit, the one with the old `streamlit.cli` and the one with the new `streamlit.web.cli` module.

## [5.9.0] - 2022-06-05

### Added

- Add a separate window to see log messages in the GUI.
- Add the trigger simulation functionality to the GUI.
- Add drop percentage to the trigger edit window in the GUI.
- Add test buttons for each tab of the configuration in the GUI.
- Add CCXT configuration to GUI.

### Changed

- Move some GUI functionality into a main menu and separate windows.
- Use PySide6 instead of PyQt6 such that the whole project is under the MIT licence again.

## [5.8.1] - 2022-06-01

### Added

- Allow setting a start date and time in the GUI.

## [5.8.0] - 2022-06-01

### Added

- Logo added to the GUI window.
- The GUI now shows a system tray icon and can send notifications.

### Changed

- All triggers now need to have an explicit name set in the configuration.
- Before a trigger is executed, the balance will be checked.
- The GUI has an improved status and about screen.

## [5.7.0] - 2022-05-29

### Added

- A completely new GUI using Qt is now part of the project.

### Fixed

- The trigger `start` attribute used to discard the time part, if it was given.

## [5.6.0] - 2022-05-07

### Added

- Add support for notifications via notify.run to provide an alternative to Telegram.

### Fixed

- Also catch `HTTPError` in the krakenex wrapper.

## [5.5.0] - 2022-02-25

### Added

- The CCXT library is now supported and gives access to more over a 100 more exchanges.
- Add an asset pair selector in the trade overview panel in the evaluation interface.

### Changed

- It is now an error when either drop percentage or delay is given, but not both at the same time.
- The `--marketplace` command line option has been removed, the marketplace is now chosen via an entry in the configuration file.

## [5.4.4] - 2022-02-11

### Fixed

- The `krakenex` library would sometimes also raise a `requests.exceptions.ReadTimeout`, which was not caught.

## [5.4.3] - 2022-01-29

### Fixed

- The database cleaning trigger would always clean all historic prices which were two hours in the past.
- The Fear and Greed index sometimes doesn't deliver a value for the current day. In this case we will try the value from yesterday.

## [5.4.2] - 2022-01-16

### Fixed

- Fix path handling to database on Windows.

## [5.4.1] - 2022-01-16

### Added

- Restore Windows support by only adding syslog on Linux.

### Changed

- Split usage documentation onto multiple pages.

### Removed

- Remove the telemetry stuff again.

## [5.4.0] - 2022-01-15

### Added

- Add optional and voluntary telemetry sending via Sentry.
- Add a dark mode to the documentation.
- Split configuration documentation onto multiple pages.

## [5.3.1] - 2022-01-15

### Fixed

- Fix bug in trade report with `KeyError: 'coin'`.

## [5.3.0] - 2022-01-14

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

## [5.2.1] - 2022-01-14

### Changed

- Allow any log level for Telegram, including `debug`.
- Attempt withdrawal after the trade has been noted in the database.
- Output full exception traceback for every caught exception into the debug logging channel.
- Pause triggers for 24 hours when they have insufficient funds.

## [5.2.0] - 2021-12-22

### Added

- Fear & Greed is now included in the evaluation interface.
- Developer documentation includes a component diagram.

### Changed

- More refactoring, more test coverage.

## [5.1.0] - 2021-12-20

### Added

- Print out version number during startup.
- Add trigger option `fear_and_greed_index_below`.

## [5.0.3] - 2021-12-17

### Fixed

- Catch `requests.exceptions.ConnectionError`, which wasn't caught by the krakenex library.

## [5.0.2] - 2021-12-05

### Fixed

- The Telegram connector would hang during shutdown, I have fixed that again.

## [5.0.1] - 2021-12-03

### Fixed

- Fix bug with marketplace factory function.

## [5.0.0] - 2021-12-03

### Changed

- Refactor a lot more.

### Removed

- Remove `--keepalive` feature, this is on by default now.
- Remove `--dry-run` feature, use the `test-drive` command instead.
- Remove `--one-shot` feature, use the loop instead.
