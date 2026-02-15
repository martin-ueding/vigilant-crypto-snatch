# Version 4

## [4.4.4] - 2021-11-16

### Added

- Add `--version` option.

### Fixed

- The Telegram sender would not shut down gracefully. I have fixed that now.

## [4.4.3] - 2021-11-15

### Fixed

- I've accidentally deleted the source code. This should be fixed now.

## [4.4.2] - 2021-11-15

### Changed

- Streamlit doesn't easily work on the Raspberry Pi due to issues with py-arrow and the ARM CPU. I have therefore reverted these dependencies to be an extra again.

## [4.4.1] - 2021-11-15

### Changed

- More refactoring. Also update the versions of various dependencies. The Streamlit interface is now part of the main dependencies.

## [4.4.0] - 2021-11-05

### Added

- Add `test-drive` command to verify configuration.

### Changed

- Major architectural change, without changes to the user.

## [4.3.5] - 2021-09-20

### Fixed

- When the balance on the marketplace is zero, withdrawals would fail and therefore crash the whole program. This is now fixed.

## [4.3.4] - 2021-08-26

### Added

- I now use the mypy static analysis and type checker, and also found a few subtle bugs with that in code paths which aren't used often.

### Fixed

- The `--dry-run` option would write buys into the database, although it would not buy anything on the market. Now the database should now be changed.

## [4.3.3] - 2021-08-12

### Fixed

- Due to an incomplete refactoring the program would crash whenever there was a non-fatal exception regarding the marketplace. This should be fixed now.

## [4.3.2] - 2021-08-02

### Changed

- Make the `marketplace` package isolated, only expose a limited set of attributes in `__init__.py`.

### Fixed

- Fix automatic detection of Telegram chat ID.
- Do not crash when there is no balance at Kraken.
- Also handle `requests.exceptions.HTTPError`.

## [4.3.1] - 2021-07-19

### Fixed

- Apparently all Kraken trades were sent in the validation mode. I have tried to fix that.

## [4.3.0] - 2021-07-16

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

## [4.2.4] - 2021-06-18

### Fixed

- Also handle `ReadTimeout` errors that can happen when the API doesn't answer before the connection breaks. These have been ignored previously, but now the error message is a bit cleaner.

## [4.2.3] - 2021-06-18

### Added

- Log output is also put into the Linux system log. In this way one can do post-mortem debugging.

### Changed

- Telegram messages are no longer directly send but stored in a send-queue. This way connection outages do not yield lost messages but rather just delay sending.
- Use a proper form instead of the plain button in Streamlit.

### Fixed

- Crashes have been reported when the Telegram message was longer than their limit of 4096 characters. Messages are now chunked to prevent this from happening.

## [4.2.2] - 2021-05-25

### Fixed

- Another warning message would use a constant that was moved to another place in the meantime. The program crashed when the message was going to be emitted. It has been removed now.

## [4.2.1] - 2021-05-23

### Fixed

- When a trigger was disabled after three consecutive failures, a message stating that would be shown every time the trigger was processed. In this way the user got the same amount of messages. This message is now removed.

## [4.2.0] - 2021-05-21

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

## [4.1.0] - 2021-05-05

### Added

- Add automatic withdrawal for currency when the amount exceeds a certain threshold determined by the fee.

### Changed

- Use `krakenex` instead of `clikraken` to communicate with Kraken. The old implementation is deprecated but retained with `--marketplace clikraken`.

## [4.0.0] - 2021-05-04

### Changed

- The trigger specification is significantly changed. Consult the documentation to learn about the new format.
