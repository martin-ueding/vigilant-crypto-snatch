# Vigilant Crypto Snatch

A little program that observes the current market price for your choice of currency pairs, looks for drastic reductions (dips) and then places buy orders.

## Installation

Use `git clone https://github.com/martin-ueding/vigilant-crypto-snatch/tree/docker-implementation` to clone the repository to your local machine.

Then install the python libraries that are needed to run this software. You can do so in a virtual environment if you want. The easy way is to do it system wide:

	sudo python3 -m pip install -r requirements.txt

If you are running an old version of the script, delete your old database from here: `~/.local/share/vigilant-crypto-snatch/db.sqlite` . The new format is incompatible with the old.

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

To run on Bitstamp call  

`while true; do ./vigilant_crypto_snatch.py --marketplace=bitstamp; done`  

to run on Kraken call

`while true; do ./vigilant_crypto_snatch.py --marketplace=kraken; done` 

If you want to use it with Docker, you can run the `docker-compose up -d` command. Docker is not needed to run.

in the directory in which you cloned the project (e.g. /home/pi/vigilant-crypto-snatch) and let it run.
When you want to quit press 

<kbd>Ctrl</kbd>+<kbd>C</kbd>.

All historical price data and performed transactions will be stored in a SQLite database at `~/.local/share/vigilant-crypto-snatch/db.sqlite`. 

## The Name

In case you wonder about the name: Dips means that the price dives. Submarines dive. The HMS Vigilant is a submarine of the British Navy. But also vigilance means to observe.

## License

<https://www.gnu.org/licenses/gpl-3.0.html>