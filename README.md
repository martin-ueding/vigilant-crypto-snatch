# Vigilant Crypto Snatch

A little program that observes the current market price for the BTC/EUR pair
and looks for drastic reductions (dips). In these cases the program will place
a buy order.

In case you wonder about the name: Dips means that the price dives. Submarines
dive. The HMS Vigilant is a submarine. But also vigilance means to observe.
Yeah …

## Dependencies

This program is written in Python 3 and needs the following third party
libraries:

- bitstamp
- requests
- sqlalchemy
- yaml

You can either install them with `apt install python3-XXX` or `pip3 install
XXX`.

## Running

You first need to copy the `sample_config.yml` from this repository to
`~/.config/vigilant-crypto-snatch.yml` and insert the API keys and your
triggers.

Then just call `./vigilant_crypto_snatch.py` in this directory and let it run.
When you want to quit press <kbd>Ctrl</kbd>+<kbd>C</kbd>.

All historical price data and performed transactions will be stored in an
SQLite database at `~/.local/share/vigilant-crypto-snatch/db.sqlite`. You can
just delete it to reset the data pool. If you want to take a look at it, try
the GUI tool `sqliteman`.
