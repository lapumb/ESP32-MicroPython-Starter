# This file is executed on every boot (including wake-boot from deep sleep)

def led_test():
    from led import Led
    white_led = Led(25, 0)
    white_led = white_led.toggle(1500)

def boot():
    import esp, wifi
    print('Running boot.py..')
    esp.osdebug(5)
    # led_test()
    # Pass your wifi SSID and passphrase to connect to wifi
    wifi.connect('MOTOE768', 'n43mf006rh')

boot()