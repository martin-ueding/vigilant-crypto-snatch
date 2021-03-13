# Welcome

*Vigiliant Crypto Snatch* is a little program that observes the current market price for your choice of currency pairs, looks for drastic reductions (dips) and then places buy orders.

The basic idea is to use the [Dollar Cost Average](https://en.wikipedia.org/wiki/Dollar_cost_averaging) effect in a bit more clever way. By buying in fixed time intervals for a certain amount of fiat currency, one can profit from a sideways moving market with fluctuations. We can try to improve on this by also actively looking for reductions in the price to buy more cryptocurrency for the same fiat amount.

The project is [published on PyPI](https://pypi.org/project/vigilant-crypto-snatch/), so you can just install it with PIP. Most likely the easiest way to install is the following:

```bash
sudo python3 -m pip install vigilant-crypto-snatch
```

In case you wonder about the name: Dips means that the price dives. Submarines dive. The HMS Vigilant is a submarine of the British Navy. But also vigilance means to observe.