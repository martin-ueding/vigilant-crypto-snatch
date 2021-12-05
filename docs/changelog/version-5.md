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

