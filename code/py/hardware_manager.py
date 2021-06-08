from components.hardware.led import Led
from components.hardware.switch import Switch

_switch: Switch = None
_white_led: Led = None
_red_led: Led = None
_green_led: Led = None
_blue_led: Led = None

def __on_switch_gpio_level_change(gpio_num: int, new_level: str) -> None:
    del gpio_num
    set_white_led_on(True if new_level == "on" else False)

def init(switch_gpio_num: int, white_led_gpio_num: int, red_led_gpio_num: int, green_led_gpio_num: int, blue_led_gpio_num: int):
    global _switch, _white_led, _red_led, _green_led, _blue_led
    _switch = Switch(switch_gpio_num)

    switch_status: str =_switch.get_switch_status()
    _white_led = Led(white_led_gpio_num, initial_level=1 if switch_status == "on" else 0)

    _red_led = Led(red_led_gpio_num, initial_level=1)
    _green_led = Led(green_led_gpio_num, initial_level=1)
    _blue_led = Led(blue_led_gpio_num, initial_level=1)

    import uasyncio
    uasyncio.create_task(_switch.poll(__on_switch_gpio_level_change))

def get_switch_status() -> str:
    return _switch.get_switch_status()

def get_white_led_on() -> bool:
    return _white_led.get_is_on()

def set_white_led_on(is_on: bool) -> None:
    _white_led.set_is_on(is_on)

def get_red_led_on() -> bool:
    return _red_led.get_is_on()

def set_red_led_on(is_on: bool) -> None:
    _red_led.set_is_on(is_on)

def get_green_led_on() -> bool:
    return _green_led.get_is_on()

def set_green_led_on(is_on: bool) -> None:
    _green_led.set_is_on(is_on)

def get_blue_led_on() -> bool:
    return _blue_led.get_is_on()

def set_blue_led_on(is_on: bool) -> None:
    _blue_led.set_is_on(is_on)