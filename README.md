 # Vigilant Crypto Snatch

A little program that observes the current market price for the BTC/EUR pair
and looks for drastic reductions (dips). In these cases the program will place
a buy order.

In case you wonder about the name: Dips means that the price dives. Submarines
dive. The HMS Vigilant is a submarine. But also vigilance means to observe.
Yeah …

## License

https://www.gnu.org/licenses/gpl-3.0.html

## Dependencies

This program is written in Python 3 and uses several third party libraries. To install use:

`sudo python3 -m pip install -r requirements.txt` 

## Installation

Use `git clone https://github.com/martin-ueding/vigilant-crypto-snatch` to clone the repository to your local machine.

## Running

### Setup

You first need to copy the `sample_config.yml` from this repository to `~/.config/vigilant-crypto-snatch.yml`. Open this file with a texteditor and do the following:

1) insert your Bitstamp API (take care that the API has the right permission!)
2) insert cryptocompare API key
3) create your telegram bot and chat to recive notification about buys via telegram (optional)
4) decide how long the timeinvall between each trigger run shall be
5) decide your triggers
6) choose on which currency pairs you want the skript to run

To setup the Kraken API keys do the following:

1) create the folder `clikraken` in `~/.config/`, so you get `~/.config/clikraken`. 
2) create the file `settings.ini` and insert the following:
      [clikraken])
      trading_agreement=agree
3) create file kraken.key . The first line is the API key and the second the secret. Example:

APIKEYAPIKEYAPIKEYAPIKEYAPIKEYAPIKEYAPIKEY
secretsecretsecretsecretsecretsecretsecretsecretsecretsecretsecretsecretsecretsecretsecret

### Start

Then just call `while true; do ./vigilant_crypto_snatch.py; done` in the directory in which you cloned the project (e.g. /home/pi/vigilant-crypto-snatch) and let it run.
When you want to quit press 

<kbd>Ctrl</kbd>+<kbd>C</kbd>.

All historical price data and performed transactions will be stored in an
SQLite database at `~/.local/share/vigilant-crypto-snatch/db.sqlite`. 


