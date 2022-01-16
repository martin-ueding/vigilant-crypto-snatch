# Subcommand test-drive

In order to check your configuration, use the `test-drive` subcommand. It will accept this option:

- `--marketplace MARKETPLACE`: We support two marketplaces, you can select either `bitstamp` or `kraken`.

It will test the following things:

- Can the database be loaded?
- Can we receive the balance from your marketplace? This verifies whether you have set up your private keys.
- Can we retrieve a historical price?
- Can your triggers be constructed?
- Can a message be sent via Telegram, if you have set it up?

If that runs through, you have a working configuration.

