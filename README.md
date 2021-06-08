# ESP32 MicroPython Starter Project

This repository contains scripts to use MicroPython on the ESP32, along with a small example project that toggles an LED (GPIO25) and listens to the `INPUT` value from a switch (GPIO15) for 15s before entering a `Read Evaluate Print Loop` ("REPL": an interative MicroPython prompt).

<!-- toc -->

- [Directory Structure](#directory-structure)
- [Getting Started](#getting-started)
- [Special Notes](#special-notes)
- [Helpful Links](#helpful-links)

<!-- tocstop -->

# Directory Structure

* `code`: Contains source code (.py) files, a script to upload the python modules in `/py`, and a script to open a serial connection to interact with the ESP32.
* `MicroPython`: Contains scripts to download and flash MicroPython onto the ESP32
* `tools`: Contains helper scripts

# Getting Started

### Install required system packages

Recommended to use a POSIX-like environment (MacOS, Linux, or Git-Bash for Windows)

```sh
brew install wget
brew install picocom
```

### Clone repo

```sh
git clone git@github.com:spindance/ESP32-MicroPython-Starter.git
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
./MicroPython/flash_micropython.sh
```

### Flash Starter-Project Code

The starter project contains logic to connect to wifi (`wifi.py`) and toggle an LED on / off on a timer (`led.py`).

```bash
cd code

# upload all Python modules to the board
./upload_py_modules.sh

# connect to the ESP32
./connect_to_board.sh
```

Once the script is finished running, one of two things will happen:

1. You will see a blank screen. If this is the case, press `enter` to open the Python prompt (you should see `>>>`)
2. You will see output from the currently-running program

Note: Connecting to the board does not reboot the board. To reboot the board, press the `EN` button on the ESP32. When the board reboots, `boot.py` will be run, followed by `main.py`.

To kill the connection, press `control+a` then `k`, then `y` to confirm killing the prompt.

# Special Notes

- `boot.py`: This file is executed on every boot
- `main.py`: This file is executed _after_ `boot.py` on every boot
- The connection is made using the `screen` command. See [Helpful Links](#helpful-links) for help using `screen`
- `ampy` is used to upload Python source files to the ESP32.
>Note: `ampy` can also be used to remove files, list files, etcetera. Execute `ampy --help` for further information.

# Helpful Links

- [Official MicroPython ESP32 Docs](https://docs.micropython.org/en/latest/esp32/general.html)
- [MicroPython Libraries Documentation](https://docs.micropython.org/en/latest/library/index.html)
- [Help with `screen` Command](http://www.kinnetica.com/2011/05/29/using-screen-on-mac-os-x/#:~:text=Type%20Ctrl%2Da%20d%20to,back%20to%20your%20standard%20terminal.)