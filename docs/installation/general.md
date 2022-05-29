# Installation

The project is [published on PyPI](https://pypi.org/project/vigilant-crypto-snatch/), so you can just install it with PIP. We have split some functionality into an *extra* such that you can install just the base trading part on a little system that is running the whole time (like a Raspberry Pi). On your main workstation you can install the full software such that you can use the evaluation interface.

To install just the base package system wide, run this:

```bash
sudo python3 -m pip install vigilant-crypto-snatch
```

If you are not running on a Raspberry Pi with 32 bit Linux, you can also install the evaluation interface and/or the GUI with the following square bracket syntax, where you can either include `evaluation`, `gui` or `evaluation,gui`.

```bash
sudo python3 -m pip install 'vigilant-crypto-snatch[evaluation,gui]'
```

If you don't want to install it system-wide, you can instead use `python3 -p pip install --user vigilant`. In that case you have to make sure that `~/.local/bin` is part of your `PATH` environment variable.

Once you are done with the installation, go over to the [configuration](../configuration/general.md).

## Virtualenv

Maybe you want to install the software and all its dependencies into a virtual environment. For this first create a virtual environment:

```console
$ virtualenv /tmp/vigilant-crypto-snatch-5-2-0
created virtual environment CPython3.10.1.final.0-64 in 485ms
```

Choose a directory that makes sense for you, like `~/.local/share/virtualenvs/vigilant-crypto-snatch`.

Then activate the virtual environment:

```console
$ source /tmo/vigilant-crypto-snatch-5-2-0/bin/activate
```

And now you can install it via pip, as usual:

```console
$ pip install --upgrade vigilant-crypto-snatch
```

Whenever you want to use it, you will first need to activate the environment and then you can just call `vigilant-crypto-snatch`.


## Upgrades

If you want to upgrade use:

```bash
sudo python3 -m pip install vigilant-crypto-snatch --upgrade
```

In case you have installed it differently, you will likely also need to upgrade in the same way.

We sometimes update the configuration options a bit and don't offer an automated migration path. You will likely get some errors on startup. Please consult the documentation to see how configuration works with the current version.