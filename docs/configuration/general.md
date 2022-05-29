# General Configuration

Unfortunately we need to configure a few things before you can start automatic trading with this software. Most configuration is done in a [YAML](https://yaml.org/) file. It is a syntax for hierarchical data and relies on indentation to show the hierarchy. Since version 5.7.0 we also [have a graphical user interface](../usage/gui.md) which will help you to configure the program. You can also directly use the graphical user interface along this guide.

The configuration file needs to be created with a (programmer's) text editor. We will talk you through the necessary steps and show snippets to put into. Depending on your platform, the path should be this:

| Platform | Location |
| --- | --- |
| Linux | `~/.config/vigilant-crypto-snatch/config.yml` |
| Windows | `C:\Users\<User>\Application Data\Martin Ueding\vigilant-crypto-snatch\config.yml` |
| macOS | `~/Library/Application Support/vigilant-crypto-snatch/config.yml`

This page does not contain all the necessary configuration steps, see the navigation for further pages on _marketplaces_, _triggers_ and _notifications_.

## Polling interval

First you should set the polling interval that the main loop should use. It will wait this many seconds before checking again. For testing we found that 5 seconds is a good value, for production use it doesn't need to be that fine grained. Many people use 60 seconds, but one can also use a whole hour.

```yaml
sleep: 60
```

## Historic price API

In order to find a drop in the price, we need to know the historic price at a given point. We use Crypto Compare for that as they provide a free API. Go to [their website](https://min-api.cryptocompare.com/pricing) and create an API key.

> ![](screenshot-cryptocompare-plans.png)

And retrieve your API key:

> ![](screenshot-cryptocompare-api-key.png)

In the configuration file then add the following:

```yaml
cryptocompare:
  api_key: "your API key here"
```