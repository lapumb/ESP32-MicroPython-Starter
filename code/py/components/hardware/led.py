from machine import Pin

class Led:
    _gpio_num: int = 0
    _pin_is_initialized: bool = False
    _led_output_pin: Pin = None

    def __valid(self, gpio_num: int) -> bool:
        from ..hardware import esp32_gpio_def
        return gpio_num in esp32_gpio_def.OUTPUT_PINS

    def __init__(self, gpio_num: int, initial_level: int=0) -> None:
        assert initial_level >= 0 and initial_level <= 1
        self._gpio_num = gpio_num

        print("Initializing switch on GPIO: {}".format(self._gpio_num))

        assert self.__valid(self._gpio_num)
        self._led_output_pin = Pin(self._gpio_num, Pin.OUT)
        assert self._led_output_pin is not None and self._led_output_pin != None

        self._pin_is_initialized = True
        self.set_gpio_level(initial_level)

    def get_gpio_num(self) -> int:
        assert self._pin_is_initialized
        return self._gpio_num

    def get_gpio_level(self) -> int:
        assert self._pin_is_initialized
        return self._led_output_pin.value()

    def set_gpio_level(self, gpio_level: int) -> None:
        assert gpio_level >= 0 and gpio_level <= 1
        assert self._pin_is_initialized

        print("Setting led (pin {0}) to level {1}".format(self._gpio_num, gpio_level))
        self._led_output_pin.value(gpio_level)
