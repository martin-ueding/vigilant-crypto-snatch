# General CLI Usage

This page is about invoking the program in an interactive or manual way. This is the right thing if you are just configuring it and want to test it. For production use, see the page about [deployment](../deployment.md).

The program has a hierarchical command line interface with multiple subcommands. If you have installed it system-wide, you can just directly call it. Otherwise you might have to add `~/.local/bin` to your `PATH` variable. With the `--help` option you will see an up-to-date list of options.

The general structure of a call is this:

```
vigilant-crypto-snatch [general options] subcommand [subcommand options]
```

The general options are the following:

- `--loglevel`: The program can emit a lot of status output while running. You can specify a *log level* with `--loglevel LEVEL`, where `LEVEL` can be `critical`, `error`, `warning`, `info` or `debug`. The `info` level is the default and does not fill the terminal with tons of output. You can set it to `debug` if you want to have more output and want to diagnose your triggers.

Take a look at the subcommands in the navigation sidebar. You likely want to start with the “test-drive” to verify that your installation and configuration is correct. Then you may want to use the “evaluate” interface to find optimal triggers for your taste. And finally use “watch” to start watching the market.