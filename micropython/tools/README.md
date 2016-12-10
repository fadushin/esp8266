# Tools

This repository contains (possibly) useful tools for development on the ESP8266.

## `ush`

The `ush` tool is a very primitive command-line shell for traversing and manipulating the Micropython file system.

Start `ush` via the `run` function:

    >>> import ush
    >>> ush.run()
    Welcome to ussh pre-0.1.  Type 'help' for help
    [/] ush$ help
    cat     <file> Catenate a file.
    cd      [<pattern>] Change directory.  No pattern changes to '/'
    date    [-s secs] [-r] Print (or set) the date (-r to print raw time in secs).
    df      Print disk usage statistics.
    dump    <file> Dump a file in hex.
    gc      Run the garbage collector.
    help    Print this help.
    ll      [<pattern>] List files or directories.  No pattern lists all files in the CWD.
    ls      [<pattern>] List files or directories.  No pattern lists all files in the CWD.
    mem     [-i] Print memory statistics.
    mkdir   <dirname> Make a directory.
    mkfile  <file> Make a file.
    mv      <src> <tgt> Move a file or directory.
    ntp     [-s] [-r] Print (or set) the date via NTP (-r to print raw time in secs).  Requires network access
    pwd     Print the CWD.
    reboot  Reboot the device.
    rm      [-r] <file> Remove a file (-r to recursively remove a directory).
    rmdir   <dirname> Remove an empty directory
    tree    [<path>] Print the directory tree from <path>, or CWD if unspecified.


### Manipulating Files

Commands for manipulating files and directories should be comfortable to most UNIX-like OS users:

    [/] ush$ ll
        -rwxrwxrwxx 160             boot.py
        -rwxrwxrwxx 598             main.py
        -rwxrwxrwxx 13873           ush.mpy
        -rwxrwxrwxx 15              webrepl_cfg.py
    [/] ush$ mkdir www
    [/] ush$ cd www
    [/www] ush$ pwd
    /www
    [/www] ush$ mkfile index.html
    Enter '.' on an empty line to terminate
    <html><body>Hello World!</body></html>
    .
    [/www] ush$ ls
        -rwxrwxrwxx 39              index.html
    [/www] ush$ cat index.html
    <html><body>Hello World!</body></html>
    [/www] ush$ 

You can use the `tree` command to view the directory tree hierarchy.

    [/www] ush$ cd
    [/] ush$ tree
    .
    ./boot.py
    ./main.py
    ./ush.mpy
    ./webrepl_cfg.py
    ./www
    ./www/index.html

Some commands support globbing.  Only wildcard matching (`*`) is supported.

    [/] ush$ ls *.py
        -rwxrwxrwxx 160             boot.py
        -rwxrwxrwxx 598             main.py
        -rwxrwxrwxx 15              webrepl_cfg.py


### Memory and Disk statistics

The `ush` tools comes with some useful commands for getting disk and memory statistics, and for running the Micropython garbage collector:

    [/www] ush$ df
        mount    capacity   free    usage
        /        413696     364544  11%
    [/www] ush$ mem
        capacity    free    usage
        36288       10032   72%
    [/www] ush$ gc
    [/www] ush$ mem
        capacity    free    usage
        36288       11520   68%


### Date and time

Use the `date` command to get and set the current date and time (use -r to get the raw date in seconds since the ESP8266 epoch):

    [/] ush$ date
    2000-01-01T01:12:03.005
    [/] ush$ date -r
    4328
    [/] ush$ date -s 534176862
    2016-12-04T14:27:42.006

You can use the `ntp` command to get and set the current date and time based using NTP.  This of course requires network access.

    [/] ush$ date
    2000-01-01T00:00:02.005
    [/] ush$ ntp
    2016-12-04T14:27:42.006
    [/] ush$ date
    2000-01-01T00:00:08.005
    [/] ush$ ntp -s
    2016-12-04T14:27:48.004
    [/] ush$ date
    2016-12-04T14:27:49.006


### Misc

You can reboot the device from the `ush` prompt:

    [/] ush$ reboot
    ...
