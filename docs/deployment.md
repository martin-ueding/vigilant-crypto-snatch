# Deployment

Using the other pages, you should have already [configured](configuration.md) the program and [tried to use](usage.md) it. It should log into the marketplace, report your balance and load the triggers. Then you can start it and have it run, but you likely want a proper deployment.

Most users seem to have a Raspberry Pi, which is an affordable miniature server. It is perfectly suited to run this little Python program. You can also run it on a larger server, if you want.

We will introduce a couple ways that you can deploy this program.

## Screen session

If you log into your Linux server via SSH and start a program, it will run on the server. But when you disconnect, the program will be shut shown. This is not what we want, we want to have the service running the whole time. Therefore a simple SSH connection is not appropriate.

Fortunately there are *terminal multiplexers*, namely *screen* and *tmux*. For our purposes both are just perfectly fine. The idea is that you have a persistent terminal on the server, and you just attach to see it, and detach from viewing it. It is still there, even if you don't see it.

For that start a new screen session, and perhaps already give it a name (we use `vigilant` here, but you are free to choose):

```console
$ screen -S vigilant
```

Not much will change, you will get a fresh screen. Then start the program as documented in the [usage](usage.md) page. It should start up.

Then you can <kbd>Ctrl</kbd>+<kbd>A</kbd>, then <kbd>D</kbd>. This will *detach* the session. Use `screen -ls` to see a list of all sessions that are open. This can look like this:

```console
$ screen -ls
There is a screen on:
        445439.vigilant (Detached)
1 Socket in /run/screen/S-mu.
```

Now you can logout via SSH, and the program will still run. Later you can log back in and use `screen -r vigilant` to *reattach* the session and control it or look at the log output.

## Team Viewer

You might have set up your Raspberry Pi with a graphical user interface and a running session. In that case you log into that session using Team Viewer or any other remote administration tool. Just open a terminal window and start the program. It will keep running when you disconnect from Team Viewer.

## Systemd unit

A very modern approach for continuous running is to use systemd. That is the program which starts all the other programs on a modern Linux system. It needs to have a definition of the service. It is a text file which looks like this:

```ini
[Unit]
Description=Vigilant Crypto Snatch Service (watch)
StartLimitIntervalSec=500
StartLimitBurst=5
After=network.target

[Service]
User=USERNAME
ExecStart=/usr/local/bin/vigilant-crypto-snatch watch --marketplace kraken --keepalive
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Create a text file at `/etc/systemd/system/vigilant-crypto-snatch.service` and put that content into it, making these changes:

-   Be sure to replace the placeholder `USERNAME` with the one where you have put the config. On a Raspberry Pi that is usually just the username `pi`. You can find out like this:

    ```console
    $ echo $USER
    mu
    ```

-   You also need to change the path, which you can find out by executing `type vigilant-crypto-snatch` on the command line.

-   The command line flags might not be the ones you want, perhaps you want a different market place.

Once you have that unit in place, you can query systemd to show you this unit:

```console
$ sudo systemctl status vigilant-crypto-snatch
○ vigilant-crypto-snatch.service - Vigilant Crypto Snatch Service (watch)
     Loaded: loaded (/etc/systemd/system/vigilant-crypto-snatch.service; disabled; vendor preset: disabled)
     Active: inactive (dead)
```

If you want to have this unit started on system startup, you need to *enable* it with `sudo systemctl enable vigilant-crypto-snatch`. To start the unit, you use `sudo systemctl start vigilant-crypto-snatch`. Using the above `status` command you can check whether it has started or crashed and also get the latest error messages.