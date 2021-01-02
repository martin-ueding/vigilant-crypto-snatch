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

This program is written in Python 3 and needs the following third party
libraries:

- BitstampClient
- requests
- sqlalchemy
- pyyaml

You can either install them with `apt install python3-XXX` or `pip3 install
XXX`.

## Running

You first need to copy the `sample_config.yml` from this repository to
`~/.config/vigilant-crypto-snatch.yml` and insert the API keys and your
triggers. It is suggested to have the main skript also in this `~/.config/vigilant-crypto-snatch.yml` directory. You don't have to edit pathes then.

Then just call `while true; do ./vigilant_crypto_snatch.py; done` in this directory and let it run.
When you want to quit press <kbd>Ctrl</kbd>+<kbd>C</kbd>.

All historical price data and performed transactions will be stored in an
SQLite database at `~/.local/share/vigilant-crypto-snatch/db.sqlite`. 

## Telegram Bot

Check the config for a tutorial on how to set up the bot.
!!Currently you have to go into the main skript and put in your values there. It's planed to move those also into the config file!!!
