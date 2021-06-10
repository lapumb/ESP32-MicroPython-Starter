# see https://docs.micropython.org/en/latest/library/uasyncio.html
import uasyncio
from machine import Pin

class Switch:

    _gpio_num: int = 0
    _pin_is_initialized: bool = False
    _switch_input_pin: Pin = None

    def __valid(self, gpio_num: int) -> bool:
        from ..hardware import esp32_gpio_def
        return gpio_num in esp32_gpio_def.INPUT_PINS

    def __init__(self, gpio_num: int) -> None:
        self._gpio_num = gpio_num

        print("Initializing switch on GPIO: {}".format(self._gpio_num))

        assert self.__valid(self._gpio_num)

        self._switch_input_pin = Pin(self._gpio_num, Pin.IN)
        assert self._switch_input_pin is not None and self._switch_input_pin != None
        self._pin_is_initialized = True

    def get_gpio_level(self) -> int:
        assert self._pin_is_initialized
        return self._switch_input_pin.value()

    async def poll(self, gpio_value_change_cb: function, delay_ms: int=50) -> None:
        assert gpio_value_change_cb is not None and gpio_value_change_cb != None
        assert self._pin_is_initialized

        previous_value: int = 0
        while True:
            current_value: int = self._switch_input_pin.value()

            if current_value != previous_value:
                print("Switch is now: {}".format(current_value))
                gpio_value_change_cb(self._gpio_num, current_value, previous_value)

            previous_value = current_value
            await uasyncio.sleep_ms(delay_ms)