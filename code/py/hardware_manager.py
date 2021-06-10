from components.hardware.led import Led
from components.hardware.switch import Switch
import aws_client_manager

_switch: Switch = None
_white_led: Led = None
_red_led: Led = None
_green_led: Led = None
_blue_led: Led = None

def __on_switch_gpio_level_change(gpio_num: int, new_level: int, previous_level: int) -> None:
    set_white_led_on(True if new_level == 1 else False)
    aws_client_manager.publish_gpio_change_event_telemetry("switch", gpio_num, new_level, previous_level)

def init(switch_gpio_num: int, white_led_gpio_num: int, red_led_gpio_num: int, green_led_gpio_num: int, blue_led_gpio_num: int):
    global _switch, _white_led, _red_led, _green_led, _blue_led
    _switch = Switch(switch_gpio_num)

    switch_value: int = get_switch_value()
    _white_led = Led(white_led_gpio_num, initial_level=switch_value)

    _red_led = Led(red_led_gpio_num, initial_level=1)
    _green_led = Led(green_led_gpio_num, initial_level=1)
    _blue_led = Led(blue_led_gpio_num, initial_level=1)

    import uasyncio
    uasyncio.create_task(_switch.poll(__on_switch_gpio_level_change))

def get_switch_value() -> int:
    return _switch.get_gpio_level()

def get_white_led_on() -> bool:
    return _white_led.get_gpio_level() == 1

def set_white_led_on(is_on: bool) -> None:
    new_gpio_level: int = 1 if is_on else 0
    current_gpio_level: int = 1 if get_white_led_on() else 0
    if new_gpio_level == current_gpio_level:
        return

    aws_client_manager.publish_gpio_change_event_telemetry("white_led", _white_led.get_gpio_num(), new_gpio_level, current_gpio_level)
    _white_led.set_gpio_level(new_gpio_level)

def get_red_led_on() -> bool:
    return _red_led.get_gpio_level() == 1

def set_red_led_on(is_on: bool) -> None:
    new_gpio_level: int = 1 if is_on else 0
    current_gpio_level: int = 1 if get_red_led_on() else 0
    if new_gpio_level == current_gpio_level:
        return

    aws_client_manager.publish_gpio_change_event_telemetry("red_led", _red_led.get_gpio_num(), new_gpio_level, current_gpio_level)
    _red_led.set_gpio_level(new_gpio_level)

def get_green_led_on() -> bool:
    return _green_led.get_gpio_level() == 1

def set_green_led_on(is_on: bool) -> None:
    new_gpio_level: int = 1 if is_on else 0
    current_gpio_level: int = 1 if get_green_led_on() else 0
    if new_gpio_level == current_gpio_level:
        return

    aws_client_manager.publish_gpio_change_event_telemetry("green_led", _green_led.get_gpio_num(), new_gpio_level, current_gpio_level)
    _green_led.set_gpio_level(new_gpio_level)

def get_blue_led_on() -> bool:
    return _blue_led.get_gpio_level() == 1

def set_blue_led_on(is_on: bool) -> None:
    new_gpio_level: int = 1 if is_on else 0
    current_gpio_level: int = 1 if get_blue_led_on() else 0
    if new_gpio_level == current_gpio_level:
        return

    aws_client_manager.publish_gpio_change_event_telemetry("blue_led", _blue_led.get_gpio_num(), new_gpio_level, current_gpio_level)
    _blue_led.set_gpio_level(new_gpio_level)