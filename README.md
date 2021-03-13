# Vigilant Crypto Snatch

A little program that observes the current market price for your choice of currency pairs, looks for drastic reductions (dips) and then places buy orders.

## Installation

The project is [published on PyPI](https://pypi.org/project/vigilant-crypto-snatch/), so you can just install it with PIP. Most likely the easiest way to install is the following:

```bash
sudo pip3 install vigilant-crypto-snatch
```

## Configuration

You first need to copy the `sample_config.yml` from this repository to `~/.config/vigilant-crypto-snatch.yml`.

In there you need to configure a couple of things:

- Create an API key for CryptoCompare (URL in the configuration file) such that the program can retrieve historical crypto prices. Insert the API key into the configuration file.
- Decide on triggers.
- Choose the currency pairs.
- Choose the time interval for checking your triggers.
- Configure one of the supported marketplaces, see below.
- *Optionally* set up a Telegram bot to receive notifications.

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

## Running

From this directory you can just do `poetry run vigilant-crypto-snatch [options]` to run it. You can pass additional options, if you want. With the `--help` option you will see an up-to-date list of options.

When you want to quit press 

<kbd>Ctrl</kbd>+<kbd>C</kbd>.

All historical price data and performed transactions will be stored in a SQLite database at `~/.local/share/vigilant-crypto-snatch/db.sqlite`. We sometimes change the database format between major releases. In that case it is easiest to delete the database and let the script create the new one. As there are only so few users, we don't offer proper database migrations.

## Developing

Use `git clone https://github.com/martin-ueding/vigilant-crypto-snatch/tree/docker-implementation` to clone the repository to your local machine.

Make sure that you have [Poetry](https://python-poetry.org/) installed. Once you have that, install the project with `poetry install`.

## The Name

In case you wonder about the name: Dips means that the price dives. Submarines dive. The HMS Vigilant is a submarine of the British Navy. But also vigilance means to observe.

## License

This is an [MIT license](https://opensource.org/licenses/MIT).

Copyright 2019, 2021 Dr. Martin Ueding
Copyright 2019, 2021 Christoph Hansen

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.