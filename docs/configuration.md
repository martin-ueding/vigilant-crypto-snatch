# Configuration

You first need to copy the `sample_config.yml` from this repository to `~/.config/vigilant-crypto-snatch.yml`.

In there you need to configure a couple of things. All steps are detailed below.

- Create an API key for CryptoCompare such that the program can retrieve historical crypto prices.
- Decide on triggers.
- Choose the time interval for checking your triggers.
- Configure a marketplace.
- *Optionally* set up a Telegram bot to receive notifications.

## Historic price API

## Marketplaces

### Bitstamp

In order to use Bitstamp, you need to set up an API key with them that has the correct permissions to trade with. Put this API key into the configuration file.

### Kraken

The Kraken API has it's own configuration files. First you have to create a file at `~/.config/clikraken/settings.ini` and insert the following there:

```ini
[clikraken]
trading_agreement=agree
```

Then on the website create an API key which has the permission to trade. You will have an API key and an associated secret. In the file `~/.config/clikraken/settings.ini` you have two lines, the first will be API key and the second will be the secret, like this:

	APIKEY 
	secret

## Triggers

### Drop triggers

### Timers

## Telegram notifications