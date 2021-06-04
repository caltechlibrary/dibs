# How to install Python version 3.x

The following instructions focus on getting [Python 3](https://docs.python.org/3/) running on Debian/Ubuntu Linux-based systems as well as on macOS via [MacPorts](https://www.macports.org) or [HomeBrew](https://brew.sh).

_**Tip**_: If you are running on an Intel-based computers (e.g., most Macs and Windows machines), you can use a Python distribution called [Miniconda](https://docs.conda.io/en/latest/miniconda.html).  This is often the easiest approach to getting Python on your machine.  If that's not suitable for you for any reason, continue reading!


## A note about Python version issues

It may be possible to use the default copy of Python provided by your operating system if it happens to be a version 3 edition of Python.  As of January 2021, the [oldest still-supported version of Python is 3.6](https://www.python.org/downloads/).  However, for historical reasons, many operating system distributions still ship with Python version 2.7 even today. This can be confusing, because the default `python` and `pip` commands provided on these operating systems is version 2.7 of Python; attempting to run programs written for Python version 3 with version 2.7 can result in extremely confusing errors that bear no relationship to the _actual_ problem, which is that the program is not written to run in Python 2.7.


## Installing a recent version of Python and `pip`

On some systems, version 3.x of the Python interpreter and `pip` are available using the commands `python3` and `pip3`, respectively. More often, they must be installed separately.  The following subsections describe how Python 3 can be installed either using the standard software package managers on certain popular operating systems, or using third-party software managers.


### Debian/Ubuntu

Debian-based systems still ship with older versions of Python by
default. To install a modern version of Python and the associated version of `pip`, run the following command:

```
sudo apt install python3 python3-pip
```

### macOS

The version of Python that comes with macOS through at least macOS 10.15 (Catalina) is Python 2.7.  The most convenient way to get Python 3.x and the associated version of `pip` is to use [MacPorts](https://www.macports.org) or [HomeBrew](https://brew.sh), depending on your preference.


#### _Using MacPorts_

If you are using macOS and MacPorts, the following command will install a recent version of Python 3:

```
sudo port install python3 py38-pip
```

After running the command above, you should be able to invoke the Python interpreter using the command `python3`. You can verify the version of Python and `pip` with the following commands:

```
python3 --version
python3 -m pip --version
```

#### _Using HomeBrew_

If you are using [HomeBrew](https://brew.sh), the corresponding commands are as follows:

```
brew install python3
```

HomeBrew's Python 3 package installs `pip3` by default.  Unless you configured your copy of HomeBrew to install it elsewhere, programs should end up in `/usr/local/bin` on your computer.  Look for `pip3` there (e.g., by running the command `ls /usr/local/bin/pip*` to see what gets listed).
