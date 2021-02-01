# This file is executed on every boot (including wake-boot from deepsleep)

def boot():
    import esp, wifi
    from led import Led
    print('Running boot.py..')
    esp.osdebug(5)
    white_led = Led(25, 0)
    white_led = white_led.toggle(1500)
    # Pass your wifi SSID and passphrase to connect to wifi
    # wifi.connect('ssid', 'passphrase')

boot()