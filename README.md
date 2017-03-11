# FTP Client & Server

The following is an implementation of an FTP client and server in Python3 which complies with the [RFC959](https://www.ietf.org/rfc/rfc959.txt).

1. Make sure you have Python 3 installed on your machine.
2. [Getting started](#getting-started)
3. [Configurations](#configurations)
4. [Usage](#usage)

## Getting started


Open 2 separate terminal windows
On one of them, type the following to run the server

```
python3 ftp_server.py
```

On the other terminal window, type the following to run the client
```
python3 ftp_client.py
```

Login using the following credentials:

```
Username: user1
Password: pass1
```

> There are currently 5 users in the system. You can see the other users in the `users.cfg` file in the `/ftpserver/conf` folder.

Type `?` or `help` to display the list of commands that you can perform on the system.

## Configurations

### The Server Config
The server config is located in `/ftpserver/conf/sys.cfg` and has the following form:

```
FTP_ROOT ftpserver/ftproot
USER_DATA_PATH ftpserver/conf
USER_DATA_FILE /users.cfg
FTP_MODE ACTIVE
DATA_PORT_RANGE_MIN 34500
DATA_PORT_RANGE_MAX 34999
DATA_PORT_FTP_SERVER 2129
FTP_ENABLED 1
MAX_USER_SUPPORT 200
FTP_LOG_PATH ftpserver/log
FTP_LOG_FILE /ftp_client.log
SERVICE_PORT 2199
```

The program reads each line and the first element of the line is the variable and the second is the value

### The Client Config
The client is located in the root of this project, called `ftp_client.cfg` and has the following form, similar to the server's:

```
DATA_PORT_MAX 51000
DATA_PORT_MIN 50000
DEFAULT_FTP_PORT 21
DEFAULT_MODE = Active
DEFAULT_DEBUG_MODE false
DEFAULT_VERBOSE_MODE true
DEFAULT_TEST_FILE test1.txt
DEFAULT_LOG_FILE ftp_client.log
```

### The User Config
The user config is located in `/ftpserver/conf/users.cfg` and has the following form:

```
user1 pass1 admin
user2 pass2 user
user3 pass3 user
user4 pass4 notallowed
user5 pass5 locked
```
There are only 5 users in the system. If you want to create another user, then add a new line to this file with the following form:

```
username password type
```
Once you create a new user, you need to create a directory for that user under the `/ftpserver/ftproot/` folder and name it the same as the username.

## Usage
The client and server should be able to run with no arguments given. However, add `--help`, you should see the following:

```
usage: python3 ftp [-h] [-hn HN] [-u USER] [-w W] [-fp FP] [-p] [-a] [-D] [-V]
                   [-dpr DPR] [-c CONFIG] [-t T] [-T T] [-L LOG] [-LALL LALL]
                   [-LONLY LONLY] [-v] [-info]

optional arguments:
  -h, --help            show this help message and exit
  -hn HN                hostname
  -u USER, --user USER  username
  -w W                  password
  -fp FP                FTP ftpserver port
  -p, --passive         passive
  -a, --active          active
  -D, --debug           debug mode on/off
  -V, --verbose         verbose for additional output
  -dpr DPR              data port range
  -c CONFIG, --config CONFIG
                        configuration file
  -t T                  run test file
  -T T                  run default test file
  -L LOG, --log LOG     log messages
  -LALL LALL            log all output to log file and screen
  -LONLY LONLY          log all output to a log file
  -v, --version         print version number of client
  -info                 prints info about the student and FTP client
```
