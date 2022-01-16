# Installation on Windows

If you want to use the program on Windows, you will first have to install Python.

## Installing Python

Go to the [Python website](https://www.python.org/downloads/windows/):

![](windows-01.png)

Then download the Windows Installer for 64-Bit:

![](windows-02.png)

Launch the installer, and add Python to the PATH. This will make it easier later on.

![](windows-03.png)

Then just press “Install Now”.

After the setup has gone through, it will allow you to extend the command line limit. This might be necessary, I would just do that.

![](windows-04.png)

Then you are finished and have Python installed on your system.

## Installing the program

Then open a command line by pressing <kbd>Windows</kbd> and type “cmd” to launch the command line. You will see a window like this:

![](windows-06.png)

Then type `pip install vigilant-crypto-snatch` and press <kbd>Enter</kbd>. It will start to download the latest version of the program:

![](windows-07.png)

Eventually it will finish and show you the command line again:

![](windows-08.png)

You should be able to start `vigilant-crypto-snatch` without arguments by typing that now:

![](windows-09.png)

If you get this help screen, then everything is installed correctly.

## Creating the config file

Next you will need to go through the configuration. We first need to create the directory for that. Open the Explorer and navigate to your user directory:

![](windows-11.png)

Then click into the address bar such that you can change the path. Append an `AppData` to it, like this:

![](windows-12.png)

After pressing <kbd>Enter</kbd>, you will see `Local`, `LocalLow` and `Roaming`. Double-click on `Roaming`. Then you should find various directories from applications that you use.

![](windows-13.png)

Create a new directory `Martin Ueding` and then inside that create another called `vigilant-crypto-snatch`. Go into that directory:

![](windows-14.png)

Then right-click to create a new “text file” called `config.yml`. You can edit that configuration file using the “Notepad” editor from Windows. Alternatively you can download a programmer's editor like [Atom](https://atom.io/) or [Notepad++](https://notepad-plus-plus.org/). Fill in the configuration as described in the [configuration documentation](../configuration/general.md).

After adding all the configuration, this is how the test-drive will look like:

![](windows-15.png)