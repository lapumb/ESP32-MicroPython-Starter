# ESP32 MicroPython Starter Project

This repository contains scripts to use MicroPython on the ESP32, along with a small example project that connects to AWS and utilizes several AWS IoT services.

<!-- toc -->

- [Directory Structure](#directory-structure)
- [Getting Started](#getting-started)
- [AWS Client Example](#aws-client-example)
- [Special Notes](#special-notes)
- [Helpful Links](#helpful-links)

<!-- tocstop -->

# Directory Structure

* `code`: Contains source code (.py) files, a script to upload the python modules in `/py`, and a script to open a serial connection to interact with the ESP32.
* `MicroPython`: Contains scripts to download and flash MicroPython onto the ESP32
* `tools`: Contains helper scripts

# Getting Started

### Install Required System Packages

Recommended to use a POSIX-like environment (MacOS, Linux, or Git-Bash for Windows)

```sh
brew install wget
brew install picocom
brew install direnv
```

If you use `bash`, add the following to `~/.bashrc`:

```
eval "$(direnv hook bash)"
```

If you use `zsh`, add the following to `~/.zshrc`:

```
eval "$(direnv hook zsh)"
```

### Clone Repo

```sh
git clone git@github.com:spindance/ESP32-MicroPython-Starter.git
```

### Install Required Tools, Setup Environment

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

### Download and Flash MicroPython

Execute the following to download and flash the latest stable ESP32 MicroPython firmware (version is defined in `.envrc` as `MICROPYTHON_ESP_FIRMWARE`)

```bash
./MicroPython/download_esp_micropython.sh
./MicroPython/flash_micropython.sh
```

### Get Started with MicroPython and the REPL

Now that MicroPython has been flashed to the ESP32 successfully, you are ready to start utilizing the REPL. To connect to the board, execute the following:

```bash
cd code
./connect_to_board.sh
```

Once you are connected to the board, press the `return` key and you should see the prompt (`>>>`) appear and you can start writing MicroPython:

```
✗ ./connect_to_board.sh
Executing 'picocom' command to connect to the ESP32 on port /dev/cu.usbserial-14330
picocom v3.1

port is        : /dev/cu.usbserial-14330
flowcontrol    : none
baudrate is    : 115200
parity is      : none
databits are   : 8
stopbits are   : 1
escape is      : C-a
local echo is  : no
noinit is      : no
noreset is     : no
hangup is      : no
nolock is      : no
send_cmd is    : sz -vv
receive_cmd is : rz -vv -E
imap is        :
omap is        :
emap is        : crcrlf,delbs,
logfile is     : none
initstring     : none
exit_after is  : not set
exit is        : no

Type [C-a] [C-h] to see available commands
Terminal ready

>>> print("Hello, world!")
Hello, world!
>>>
```

# AWS Client Example

This repository houses an example project that shows how to use the `cloud_aws` component to:

- Connect to AWS
- Update the device shadow document
- Receive `desired` shadow properties
- Subscribe to MQTT topics
- Publish to MQTT topics
- Listen for incoming AWS Jobs
- Publish AWS Jobs updates

### Download the AWS Configuration and Upload it to ESP32

1. Create an AWS IoT `thing`
    1. Sign into the [AWS Console](https://console.aws.amazon.com/console/home?region=us-east-1#) and navigate to the `IoT Core` service
    2. Under `Manage`, select `Things` and click `Create`
    3. Select `Create a single thing` and fill out the fields as you desire (all that is neccessary for this example is the `Name`), then click `Next`
    4. Select option 1 (`Create certificate`) and click `Next`
    5. Download the `certificate` (`*-certificate.pem.crt`) and the `private` key (`*-private.pem.key`), then click `Activate` under the root-CA download link
    6. Attach a policy with wide-open permissions (see below) and click `Register Thing`:

    ```json
    {
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Action": "iot:*",
        "Resource": "*"
        }
    ]
    }
    ```

2. Create a folder `aws_config` in the repositories root directory and add the `private` key and `certificate`

3. Upload the AWS configuration to the ESP32 by executing:

    ```bash
    cd $REPO_ROOT
    ./tools/upload_aws_config.sh
    ```

>Note: the `upload_aws_config.sh` script assumes the certificate and private key are in the folder `$REPO_ROOT/aws_config`

4. Open `code/py/boot.py` and fill in "YOUR_SSID" and "YOUR_PASSWORD" in `__start_wifi` so WiFi can be connected when the board boots

5. Open `code/py/main.py` and fill your info in for the call to `aws_client_manager.init`, where:
    - `"thing_name"` is your devices AWS Thing name
    - `"host_name"` is the HTTPS endpoint to communicate with your AWS Thing
        - The host name can be found by going to: `AWS IoT` -> `Manage` -> `Things` -> `YOUR_THING_NAME` -> `Interact`
    - `"aws_config/cert_file_path"` is the relative path to your AWS certificate file (`aws_config/CERT_FILE_NAME`)
    - `"aws_config/private_key_file_path"` is the relative path to your private-key file (`aws_config/PRIVATE_KEY_FILE_NAME`)

### Upload Example Code and Connect to ESP32

```bash
cd code

# upload `py` modules to the board
./upload_py_modules.sh

# connect to the ESP32
./connect_to_board.sh
```

Once the scripts are finished running, one of two things will happen:

1. You will not see any output from the ESP32. If this is the case, press `enter` to open the Python prompt (you should see `>>>`)
2. You will see output from the currently-running program

Note: Connecting to the board does not reboot the board. To reboot the board, press the `EN` button on the ESP32. When the board reboots, `boot.py` will be run, followed by `main.py`.

### Killing the Program

To kill the program in execution, press `control+c`.

Remember: `boot.py` and `main.py` are both unique programs. If you kill the program execution while `boot.py` is running, `main.py` will still be executed. Once `main.py` is killed, the REPL will appear.

### Killing the Serial Connection

To kill the connection, press `control+a` then `control+x`.

# Special Notes

- `boot.py`: This file is executed on every boot
- `main.py`: This file is executed _after_ `boot.py` on every boot
- The connection is made using the `picocom` command. See [Helpful Links](#helpful-links) for help using `picocom`
- `ampy` is used to upload Python source files to the ESP32.
>Note: `ampy` can also be used to remove files, list files, etcetera. Execute `ampy --help` for further information.

# Helpful Links

- [Official MicroPython ESP32 Docs](https://docs.micropython.org/en/latest/esp32/general.html)
- [MicroPython Libraries Documentation](https://docs.micropython.org/en/latest/library/index.html)
- [picocom Man Page](https://linux.die.net/man/8/picocom)