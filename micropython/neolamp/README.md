
Neolamp is a set of software for the ESP8266 that drives a set of NeoPixel (WS2812B) LEDs to function as a lamp, for nightlight or other applications.  In some ways, this turns your ESP8266 into something like a Phillips Hue light bulb, though with likely far fewer lumens (and very little in the way of QA, but hey, this is a Maker/DIY project).  Instead of paying upwards of $50 per bulb, you can get away with building a lamp for a few dollars in kit.  And you can impress your friends with your Maker prowess.

The software is designed to be installed and run on an ESP8266 and driven via a REST-based API.  Users may control the color of the LEDs, and control a simple scheduler so that, for example, the lamp will turn on with a specific color at a given time of the day (say, early morning), and then shut off after some period.  You could use this to wake up gently in the morning when it's dark outside.  You can even use to to spice up a party at night!

Currently, the REST-based API can be drived via CURL or via a python3 command-line interface, which you can drive from a laptop or desktop computer.

# Features

Neolamp includes the features described below.

## Color Management

Neopixels are cool little chips, each of which contains 3 colored LEDs (red, green, and blue) internally.  The Micropython neopixel driver allows you to control each RGB magnitude of each pixel individually, where each RGB color can be in the range `[0..255]`.  This allows a single neopixel LED to be in any one of `2^24` (16777216) states, at any given time.

Setting and controlling color magnitudes is certainly interesting and useful, but Neolamp is also designed to periodically fluctuate each RGB color over time, so that each neopixel behaves much like one of those old lava lamps from the 1970s.  Groovy.

Neolamp does this by allowing you to specify a color as a set not just of RGB magnitudes, but as a set of RGB 4-tuples, corresponding to the color's magnitude (a value in `[0..255]`), amplitude (variation off the magnitide), period (in seconds), and offset (off an arbitrary point in time, usually when the neolamp starts).  For example, the following JSON represents a color who's red value fluctuates by between 59 and 69 over a period of 10 seconds, who's green value fluctuates between 6 and 26 every 10 seconds, and who's green value fluctuates between 12 and 42 every 100 seconds:

    {
        "r": {"m": 64, "a":  5, "p": 10,  "o": 0},
        "g": {"m": 16, "a": 10, "p": 10,  "o": 0},
        "b": {"m": 32, "a": 20, "p": 100, "o": 0}
    }    

We call the above JSON expression a "color specificiation", or colorspec, for short.

The value of color at a given time x (expressed as the number of milliseconds since an arbitrary start point, usually when the Neolamp starts) is computed using the magnitude (`m`), amplitude (`a`), period (`p`), and offset (`o`) values for a colorspec, using the `sin` function as follows:

    m + a * sin(o + x * 1/p * 2π)

Graphically, you can view the above colorspec as follows:

![purple_haze](/esp8266/micropython/neolamp/doc/images/purple_haze.png)

Colorspecs are named in Neolamp, and the administrative tools described below allow you to create, update, read, and delete colorspec entries.

## Schedule Management

Neolamp can be configured to change colorspecs on a scheduled basis.  For example, user can configure a Neolamp to come on at 5:00 AM with a specific colorspec, to transition to another colorspec at 6:00 AM, and then to turn off at 6:30 AM.  Schedules may be configured for specific days of the week, so that one schedule can be set for Mondays, Tuesdays, and Wednesdays, and another for Thursdays and Fridays.

Transitions between color specs are semi-gradual, transitioning in a linear fashion over roughly one second.

Schedules can be created, viewed, updated, and deleted via the REST API.

## Neolamp Modes

A Neolamp can be in one of the following three modes:

* `lamp` -- The Neolamp "plays" a specific colorspec
* `schedule` -- The Neolamp follows a configured schedule to automatically transition colorspecs on a scheduled basis
* `off` -- The Neolamp turns off (set all neopixels to black)

The Neomap mode can be configured via the REST API.

## NTP support

Neolamp contains an NTP client which will periodically syncronize the ESP clock with an NTP server (by default, every 15 minutes).

The NTP server and update period are configurable via the REST API.

> Note. configuration via REST is still a WIP

## Timezone suppport

Neolamp contains a web client which will periodically obtain the timezone in which the ESP device is located using the `timezoneapi.io` REST API (by default, every 3 hours).

The update period is configurable via the REST API.

> Note. configuration via REST is still a WIP

## Periodic garbage collection

Neolamp will periodically run the garbage collector (by default, every 5 seconds).

The garbage collection interval is configurable via the REST API.

> Note. configuration via REST is still a WIP

## Logging

Certain events are logged to the ESP console, such as NTP updates, Timezone updates, and any errors that occur in the REST API.

The logging subsystem may optionally be configured to publish logs via MQTT to an MQTT message broker.  (See below)

## Statistics

Neolamp supports a set of statistics accessible through the REST API, including:

* Number of successful/failed NTP updates
* Number of successful/failed timezone updates
* Number of successful/failed garbage collections
* Amount of free/allocated memory (in bytes)

## MQTT Publishing

Logging and statistics may optionally be published to an MQTT message broker.

Log messages use the MQTT topic named 'log'.

Statistic messages use the MQTT topic named 'stat'.

> Node.  This feature is a WIP.  Fill in details once implementation stabilizes.

# Limitations

Neolamp has the following limitations

* Neolamp contains a lot of software, and memory in the ESP9266 is quite limited.  The number of colors is schedules that can be managed is therefore quite small.
* There is currently no support for pre-built images; you will need to build Neolamp per the instructions below.

# Requirements

Neolamp reuires the following hardware and software.

## Hardware

You will need an ESP8266, as well as a set of (at least one) Neopixel (WS2812B) LEDs.  I bought an array of 100 of these on Amazon (many solders required!), but you can usually find rings or strips of these for more money.

I am using an ESP-01 on a breadboard for development, running the LEDs off GPIO2.  Because I have less than 10 LEDs, and because the WS2812Bs require minimal votage difference between the power supply and data lines, I am running the LEDs straight off 3.3v, instead of the 5v line.  I need to use a wallwart to power the ESP-01, however, as amperage from the USB port on the laptop is unsufficient to drive the LEDs.

## Software

This software is written in micropython (https://github.com/micropython/micropython), and therefore requires the micropython runtime in order to run.  At the time of writing, you will need to check out and build version 1.9.3 of the micropython runtime.

This software makes use of several libraries, including

* `uasyncio` (https://github.com/micropython/micropython-lib/usasyncio) 
* `uhttpd` (https://github.com/fadushin/esp8266/tree/master/micropython/uhttpd)
* `http` (https://github.com/fadushin/esp8266/tree/master/micropython/http)
* `core` (https://github.com/fadushin/esp8266/tree/master/micropython/core)
* `logging` https://github.com/micropython/micropython-lib/logging
    * alternatively, `ulog` (https://github.com/fadushin/esp8266/tree/master/micropython/ulog)
* Optionally, `umqtt` (https://github.com/micropython/micropython-lib/umqtt.simple)

You will need to incorporate these libraries into your micropython build (see below).

# Installation Instructions

Because Neolamp makes use of many libraries, and because memory is tightly constrained on ESP8266 devices, you will need to burn all of the Neolamp libraries and (cimpiled) source code into frozen bytecode.

Instructions for building micropython from source code are outside of the scope of this document, but you can consult the instructions on the [micropython](https://github.com/micropython/micropython) web site.

Instructions for building frozen bytecode vary, but I typically just create symlinks to the corresponding source tree locations of the dependent libraries and source code, e.g.,

    core@ -> /work/src/github/fadushin/esp8266/micropython/core/core
    http@ -> /work/src/github/fadushin/esp8266/micropython/http-client/http
    logging.py@ -> /work/src/github/fadushin/esp8266/micropython/ulog/logging.py
    neolamp@ -> /work/src/github/fadushin/esp8266/micropython/neolamp/neolamp
    uasyncio/__init__.py@ -> /work/src/github/micropython/micropython-lib/uasyncio/uasyncio/__init__.py
    uasyncio/core.py@ -> /work/src/github/micropython/micropython-lib/uasyncio.core/uasyncio/core.py
    uhttpd@ -> /work/src/github/fadushin/esp8266/micropython/uhttpd/uhttpd
    ulog@ -> /work/src/github/fadushin/esp8266/micropython/ulog/ulog
    umqtt@ -> /work/src/github/micropython/micropython-lib/umqtt.simple/umqtt

Refer to the [micropython](https://github.com/micropython/micropython) build instructions for building and deploying an image onto your ESP device.

# Command-line Interface

Neolamp includes a simple python3 application for managing a Neolamp instance remotely, without requiring a UART connection to the device.  This CLI makes use of the Neolamp REST API for most operations.

To start the Neolamp CLI, run the `neolamp-cli` script from the bin directory of this project.  You may issue the `--help` flag to print the options for the CLI command:

    shell$ neolamp-cli --help
    Usage: neolamp-cli.py [options]
    
    Options:
      -h, --help   show this help message and exit
      --host=HOST  ESP host (192.168.4.1)
      --port=PORT  ESP port (80)

You should specify the host IP address of the ESP device, to connect to.  This will print the top level menu, which provides a list of sub-menus to select:

    shell$ neolamp-cli --host=192.168.1.218
    ------------
        [n] -- Manage Neopixel
        [c] -- Manage Colors
        [l] -- Manage Lamp
        [s] -- Manage Scheduler
        [m] -- Manage Mode
        [d] -- Manage Device
        [q] -- Quit
    ------------
    neolamp> 

> Note.  You may also set the `ESP_IP_ADDRESS` environment variable in lieu of the `--host` flag:

    shell$ ESP_IP_ADDRESS=192.168.1.218
    shell$ export ESP_IP_ADDRESS
    shell$ neolamp-cli
    ...

The sub-menus are described in the following sections.

## Manage Neopixel Menu

From the top level menu, enter `n` to enter the Manage Neopixel menu:

    neolamp> n
    ------------
        [l] -- List neopixel properties
        [p] -- Set neopixel pin
        [n] -- Set num_pixels
        [q] -- Quit
        [u] -- Return to previous menu
    ------------

From this menu, you may:

* List the GPIO pin and number of neopixels attached to the GPIO pin;
* Set the GPIO pin connected to the array of neopixels;
* Set the number of neopixels attached to the GPIO pin.

### Example

    neolamp> l
    pin: 2
    num_pixels: 1
    ------------
        [l] -- List neopixel properties
        [p] -- Set neopixel pin
        [n] -- Set num_pixels
        [q] -- Quit
        [u] -- Return to previous menu
    ------------
    neolamp> n
    Enter num_pixels: 9
    ------------
        [l] -- List neopixel properties
        [p] -- Set neopixel pin
        [n] -- Set num_pixels
        [q] -- Quit
        [u] -- Return to previous menu
    ------------

## Manage Colors Menu

From the top level menu, enter `c` to enter the Manage Colors menu:

    neolamp> c
    ------------
        [l] -- List colors
        [g] -- Get color
        [s] -- Set color
        [d] -- Delete color
        [q] -- Quit
        [u] -- Return to previous menu
    ------------

From this menu, you may:

* List the color (names) configured on this device;
* Print the properties of a given color (by name);
* Set (create or update) a color;
* Delete a color.

### Example

    neolamp> l
    colors: ["wakeup", "black", "purple_haze"]
    ------------
        [l] -- List colors
        [g] -- Get color
        [s] -- Set color
        [d] -- Delete color
        [q] -- Quit
        [u] -- Return to previous menu
    ------------
    neolamp> g
    Enter color ["wakeup", "black", "purple_haze"]: purple_haze
    RED     magnitude:  64   period:  10   amplitude:   5
    BLUE    magnitude:  16   period:  10   amplitude:  10
    GREEN   magnitude:  32   period: 100   amplitude:  20
    ------------
        [l] -- List colors
        [g] -- Get color
        [s] -- Set color
        [d] -- Delete color
        [q] -- Quit
        [u] -- Return to previous menu
    ------------

> Note TODO fix `set` menu

## Manage Lamp Menu

From the top level menu, enter `l` to enter the Manage Lamp menu:

    neolamp> l
    ------------
        [g] -- Get colorspec
        [s] -- Set colorspec
        [q] -- Quit
        [u] -- Return to previous menu
    ------------

From this menu, you may:

* Get the colorspec (name) configured for "lamp" mode;
* Set the colorspec (name) configured for "lamp" mode.

When the Neolamp mode is set to `lamp`, the specified color will be

### Example

    neolamp> g
    colorspec: black
    ------------
        [g] -- Get colorspec
        [s] -- Set colorspec
        [q] -- Quit
        [u] -- Return to previous menu
    ------------
    neolamp> s
    Enter colorspec ["wakeup", "black", "purple_haze"]: black
    ------------
        [g] -- Get colorspec
        [s] -- Set colorspec
        [q] -- Quit
        [u] -- Return to previous menu
    ------------
    neolamp> g
    colorspec: purple_haze


## Manage Scheduler Menu

From the top level menu, enter `s` to enter the Manage Scheduler menu:

    TODO Currently unimplemented

## Manage Mode Menu

From the top level menu, enter `m` to enter the Manage Mode menu:

    neolamp> m
    ------------
        [g] -- Get mode
        [s] -- Set mode
        [q] -- Quit
        [u] -- Return to previous menu
    ------------

From this menu, you may:

* Get the Neolamp "mode";
* Set the Neolamp "mode" (to one of `off|lamp|scheduler`).

### Example

    neolamp> g
    mode: off
    ------------
        [g] -- Get mode
        [s] -- Set mode
        [q] -- Quit
        [u] -- Return to previous menu
    ------------
    neolamp> s
    Enter mode [off|lamp|scheduler]: lamp
    ------------
        [g] -- Get mode
        [s] -- Set mode
        [q] -- Quit
        [u] -- Return to previous menu
    ------------

## Manage Device Menu

From the top level menu, enter `d` to enter the Manage Device menu:

    neolamp> d
    ------------
        [s] -- Get stats
        [r] -- Reboot
        [t] -- Reset
        [q] -- Quit
        [u] -- Return to previous menu
    ------------

From this menu, you may:

* Get statistics about the devide;
* Reboot the device;
* Reset the device (warning -- this will destroy any previous configuration!).

### Example:

    neolamp> s
    ~~~
    GC task (calls failures avg_ms/call): 11568 0 12
    NTP task (calls failures avg_ms/call): 67 2 187
    Lamp task (calls failures avg_ms/call): 264336 0 7
    Scheduler task (calls failures avg_ms/call): 21688 0 3
    ~~~
    GC stats: max: 3744 min: 80 avg: 971
    Memory: allocated: 30656 bytes free: 5312 bytes (85%)
    Uptime: 0d 16h 7m 7.177s
    ~~~
    ------------
        [s] -- Get stats
        [r] -- Reboot
        [t] -- Reset
        [q] -- Quit
        [u] -- Return to previous menu
    ------------
    neolamp> r
    ------------
        [s] -- Get stats
        [r] -- Reboot
        [t] -- Reset
        [q] -- Quit
        [u] -- Return to previous menu
    ------------


# Web Interface

> TODO in the future

# REST API

TODO describe, once it is stabilized

# Implementation Architecture

TODO describe, once it is stabilized

