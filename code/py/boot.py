# This file is executed on every boot (including wake-boot from deep sleep)

def __start_wifi() -> None:
    import components.wifi.wifi as wifi
    wifi.connect("___ssid___", "___password___")

def boot() -> None:
    import utils
    utils.print_heap_usage_raw()
    __start_wifi()

if __name__ == "__main__":
    print("Running boot.py..")

    try:
        boot()
    except KeyboardInterrupt:
        print("Killing program..")
        import sys
        sys.exit(0)