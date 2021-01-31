# ESP32 MicroPython Starter Project

This repository contains starter code and scripts to run MicroPython on the Espressif ESP32 board.

<!-- toc -->

- [Directory Structure](#directory-structure)
- [Getting Started](#getting-started)
- [Special Notes](#special-notes)
- [Helpful Links](#helpful-links)

<!-- tocstop -->

# Directory Structure

* `code`: Contains source code (.py) files and scripts to upload the python modules and open a Read Evaluate Print Loop ("REPL": an interative MicroPython prompt)
* `MicroPython`: Contains scripts to download and flash MicroPython onto the ESP32
* `tools`: Contains helper scripts

# Getting Started

### Install required system packages

Recommended to use a POSIX-like environment (MacOS, Linux, or Git-Bash for Windows)

```sh
brew install wget
```

### Clone repo

```sh
git clone git@github.com:lapumb-spindance/ESP32-MicroPython-Starter.git
```

### Install required tools, setup environment

1. `cd ESP32-MicroPython-Starter`
1. `direnv allow`: enables `.envrc` to install repository requirements

It is recommended to create a `.userenv` file in the root of the repository.
If this file exists, it will be sourced inside of the `.envrc` file.

`.userenv` defines user/system-specific variables, such as the path to
UART port that ESP tools rely on for logging and JTAG (`$ESPPORT`).

To find the specific port to communicate with the ESP32, plug in your device via USB and execute the following:

```bash
ls /dev/cu.*

# The output should look something like:
/dev/cu.Bluetooth-Incoming-Port      /dev/cu.usbserial-14330
```

Given the above, an example `.userenv` would have (at least) the following contents:

```
export ESPPORT=/dev/cu.usbserial-14330
```

### Erase Flash

In order to properly flash MicroPython to the ESP32, you will need to first erase anything already on the board. Please note, **this cannot be undone**.

```bash
cd ESP32-MicroPython-Starter
./tools/esp_erase_flash.sh
```

### Download and flash MicroPython

Execute the following to download and flash the latest stable ESP32 MicroPython firmware (version is defined in `.envrc` as `MICROPYTHON_ESP_FIRMWARE`)

```bash
cd ESP32-MicroPython-Starter
./MicroPython/download_esp_micropython.sh
./flash_micropython.sh
```

### Flash Starter-Project Code

The starter project contains logic to connect to wifi (`wifi.py`) and toggle an LED on / off on a timer (`led.py`).

```bash
cd ESP32-MicroPython-Starter/code

# upload all Python modules to the board
./upload_py_modules.sh

# open an REPL
./open_repl.sh
```

Once the REPL is opened, press `enter` and you should see:

```
>>>
```

Note: Opening the REPL does not reboot the board. To reboot the board, press the `EN` button on the ESP32.

To kill the REPL, press `control+a` then `k`.

# Special Notes

- `boot.py`: This file is executed on every reboot
- The REPL is entered using the `screen` command
- `ampy` is used to upload Python source files to the ESP32

# Helpful Links

- [Official MicroPython ESP32 Docs](https://docs.micropython.org/en/latest/esp32/general.html)
- [Help with `screen` Command](http://www.kinnetica.com/2011/05/29/using-screen-on-mac-os-x/#:~:text=Type%20Ctrl%2Da%20d%20to,back%20to%20your%20standard%20terminal.)