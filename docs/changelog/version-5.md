# Version 5

## Version 5.0.0

- Refactor a lot more.
- Remove `--keepalive` feature, this is on by default now.
- Remove `--dry-run` feature, use the `test-drive` command instead.
- Remove `--one-shot` feature, use the loop instead.

### Version 5.0.1

- Fix bug with marketplace factory function. Would emit `RuntimeError: Unsupported marketplace: <vigilant_crypto_snatch.configuration.yaml_configuration.YamlConfiguration object at 0x7f2b3a031840>`.

### Version 5.0.2

- The Telegram connector would hang during shutdown, I have fixed that again.

### Version 5.0.3

- Catch `requests.exceptions.ConnectionError`, which wasn't caught by the krakenex library. Now it will be converted into an error on the module level.

## Version 5.1.0

- Print out version number during startup.
- Add trigger option `fear_and_greed_index_below`.

## Version 5.2.0

- Fear & Greed is now included in the evaluation interface.
- More refactoring, more test coverage.
- Developer documentation includes a component diagram.

### Version 5.2.1

- Allow any log level for Telegram, including `debug`.
- Attempt withdrawal after the trade has been noted in the database. Previously, a failure during withdrawal would have dropped the trade and eventually performed it again.
- Output full exception traceback for every caught exception into the debug logging channel.
- Pause triggers for 24 hours when they have insufficient funds. This will reduce failure messages from three per 12 hours to one per 24 hours.

## Version 5.3.0

- Add a report page about user trades into the evaluation interface.
- Link to download statistics within documentation.
- Add GitHub funding.
- Connection errors are not reported all the time, instead they are just logged as debug output.
- Create `AssetPair` data structure so better structure the code internally.
- Remove usage of `Protocol` such that Python 3.7 is still supported.
- Update developer documentation a bit.
- Update Pillow for security.

### Version 5.3.1

- Fix bug in trade report with `KeyError: 'coin'`.

## Version 5.4.0

- Add optional and voluntary telemetry sending via Sentry. See the configuration for details and how to enable it, if you want to.
- Add a dark mode to the documentation.
- Split configuration documentation onto multiple pages.

### Version 5.4.1

- Remove the telemetry stuff again.
- Split usage documentation onto multiple pages.
- Restore Windows support by only adding syslog on Linux.

### Version 5.4.2

- Fix path handling to database on Windows.

### Version 5.4.3

- The database cleaning trigger would always clean all historic prices which were two hours in the past. Therefore all old prices would vanish and a lot of calls to CryptoCompare were done. This depleted the API volume needlessly.
- The Fear and Greed index sometimes doesn't deliver a value for the current day. In this case we will try the value from yesterday. If that doesn't exist as well, the failure will just be logged, without crashing the program.

### Version 5.4.4

- The `krakenex` library would sometimes also raise a `requests.exceptions.ReadTimeout`, which was not caught. The program would crash. This exception type is now caught as well.

## Version 5.5.0

- The CCXT library is now supported and gives access to more over a 100 more exchanges.
- Add an asset pair selector in the trade overview panel in the evaluation interface. Also add documentation for the trade overview.
- It is now an error when either drop percentage or delay is given, but not both at the same time. Previously this would have lead to a simple delay trigger, although the user likely wanted to have a drop trigger. The error message will make it clear that users have to update their configuration.
- The `--marketplace` command line option has been removed, the marketplace is now chosen via an entry in the configuration file.

## Version 5.6.0

- Add support for notifications via notify.run to provide an alternative to Telegram.
- Also catch `HTTPError` in the krakenex wrapper.

## Version 5.7.0

- A completely new GUI using Qt is now part of the project.
- The trigger `start` attribute used to discard the time part, if it was given. The start was always taken to start from midnight. This is fixed in this version.

## Version 5.8.0

- All triggers now need to have an explicit name set in the configuration.
- Before a trigger is executed, the balance will be checked. Only if sufficient balance is on the marketplace, an attempt to buy is made. It may still fail because there is insufficient balance depending on the way that fees are computed.
- The GUI has an improved status and about screen.
- The GUI now shows a system tray icon and can send notifications.
- Logo added to the GUI window.

### Version 5.8.1

- Allow setting a start date and time in the GUI.

## Version 5.9.0

This release features a lot of work on the GUI:

- Move some functionality into a main menu and separate windows.
- Add a separate window to see log messages.
- Add the trigger simulation functionality previously only available in the Streamlit interface.
- Use PySide6 instead of PyQt6 such that the whole project is under the MIT licence again.
- Add drop percentage to the trigger edit window.
- Add test buttons for each tab of the configuration, such that one can test each thing independently of the others.
- Add CCXT configuration to GUI.

### Version 5.9.1

- Try to support both versions of Streamlit, the one with the old `streamlit.cli` and the one with the new `streamlit.web.cli` module.