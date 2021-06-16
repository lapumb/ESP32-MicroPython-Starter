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

    async def poll(self, gpio_value_change_cb: function, delay_ms: int = 50) -> None:
        """Poll the switch for changes in GPIO level

        Parameters
        ----------
        `gpio_value_change_cb` : function
            Called when a new level is detected on the switch GPIO

            Signature: `on_gpio_change(gpio_num: int, current_gpio_level: int, previous_gpio_level: int) -> None`

            Note: this CANNOT be None

        `delay_ms` : int
            The number of milliseconds to delay between each GPIO-level check

            Default: 50

            Note: this must be at least 50

        """
        assert gpio_value_change_cb is not None and gpio_value_change_cb != None
        assert delay_ms >= 50
        assert self._pin_is_initialized

        previous_value: int = 0
        while True:
            current_value: int = self._switch_input_pin.value()

            if current_value != previous_value:
                print("Switch is now: {}".format(current_value))
                gpio_value_change_cb(self._gpio_num, current_value, previous_value)

            previous_value = current_value
            await uasyncio.sleep_ms(delay_ms)