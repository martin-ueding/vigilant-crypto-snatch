# Installation

The project is [published on PyPI](https://pypi.org/project/vigilant-crypto-snatch/), so you can just install it with PIP. We have split some functionality into an *extra* such that you can install just the base trading part on a little system that is running the whole time (like a Raspberry Pi). On your main workstation you can install the full software such that you can use the evaluation interface.

To install just the base package system wide, run this:

```bash
sudo python3 -m pip install vigilant-crypto-snatch
```

The evaluation interface is included when you run this:

```bash
sudo python3 -m pip install 'vigilant-crypto-snatch[evaluation]'
```

If you don't want to install it system-wide, you can instead use `python3 -p pip install --user vigilant`. In that case you have to make sure that `~/.local/bin` is part of your `PATH` environment variable.

Once you are done with the installation, go over to the [configuration](configuration.md).

## Upgrades

If you want to upgrade use:

```bash
sudo python3 -m pip install vigilant-crypto-snatch --upgrade
```

In case you have installed it differently, you will likely also need to upgrade in the same way.

We sometimes update the configuration options a bit and don't offer an automated migration path. You will likely get some errors on startup. Please consult the documentation to see how configuration works with the current version.