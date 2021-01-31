# This file is executed on every boot (including wake-boot from deepsleep)

# Run on boot
import esp, led, wifi
esp.osdebug(5)
wifi.connect('MOTOE768', 'n43mf006rh')
white_led = led.Led(25, 0)
white_led = white_led.toggle(1500)
