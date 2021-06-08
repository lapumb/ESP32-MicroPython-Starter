# see https://docs.micropython.org/en/latest/library/uasyncio.html
import uasyncio
from machine import Pin

class Switch:
    ON: str = "on"
    OFF: str = "off"
    UNKNOWN: str = "unknown"

    gpio_num: int = 0
    pin_is_initialized: bool = False
    switch_input_pin: Pin = None

    def __valid(self, gpio_num: int) -> bool:
        from ..hardware import esp32_gpio_def
        return gpio_num in esp32_gpio_def.INPUT_PINS

    def __init__(self, gpio_num: int) -> None:
        self.gpio_num = gpio_num

        print("Initializing switch on GPIO: {}".format(self.gpio_num))

        if not self.__valid(self.gpio_num):
            print("Invalid switch configuration")
            return

        self.switch_input_pin = Pin(self.gpio_num, Pin.IN)
        self.pin_is_initialized = True

    def get_switch_status(self) -> str:
        if not self.pin_is_initialized:
            print("switch pin {} not initialized".format(self.gpio_num))
            return self.UNKNOWN

        return self.ON if self.switch_input_pin.value() == 1 else self.OFF

    async def poll(self, gpio_value_change_cb: function, delay_ms: int=50) -> None:
        assert gpio_value_change_cb is not None

        if not self.pin_is_initialized:
            print("switch pin {} not initialized".format(self.gpio_num))
            return

        current_value = self.OFF
        previous_value = ""
        while True:
            if self.switch_input_pin.value() == 0:
                current_value = self.OFF
            else:
                current_value = self.ON

            if current_value is not previous_value:
                print("Switch is now: {}".format(current_value))
                gpio_value_change_cb(self.gpio_num, current_value)

            previous_value = current_value
            await uasyncio.sleep_ms(delay_ms)