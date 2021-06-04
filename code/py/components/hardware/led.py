from machine import Pin

class Led:
    gpio_num: int = 0
    pin_is_initialized: bool = False
    led_output_pin: Pin = None

    def __valid(self, gpio_num: int) -> bool:
        from ..hardware import esp32_gpio_def
        return gpio_num in esp32_gpio_def.OUTPUT_PINS

    def __init__(self, gpio_num: int, initial_level: int=0) -> None:
        assert initial_level >= 0 and initial_level <= 1
        self.gpio_num = gpio_num

        print("Initializing switch on GPIO: {}".format(self.gpio_num))

        if not self.__valid(self.gpio_num):
            print("Invalid GPIO number: pin is not output compatible")
            return

        self.led_output_pin = Pin(self.gpio_num, Pin.OUT)

        if self.led_output_pin is None:
            print("failed to set LED pin")
            return

        self.pin_is_initialized = True
        self.set_gpio_level(initial_level)

    def get_is_on(self) -> bool:
        if not self.pin_is_initialized:
            print("led pin {} not initialized".format(self.gpio_num))
            return False

        return True if self.get_gpio_level() == 1 else False

    def get_gpio_level(self) -> int:
        if not self.pin_is_initialized:
            print("led pin {} not initialized".format(self.gpio_num))
            return -1

        return self.led_output_pin.value()

    def set_is_on(self, is_on: bool) -> None:
        if not self.pin_is_initialized:
            print("led pin {} not initialized".format(self.gpio_num))
            return

        self.set_gpio_level(1 if is_on else 0)

    def set_gpio_level(self, gpio_level: int) -> None:
        assert gpio_level >= 0 and gpio_level <= 1

        if not self.pin_is_initialized:
            print("led pin {} not initialized".format(self.gpio_num))
            return

        print("Setting led (pin {0}) to level {1}".format(self.gpio_num, gpio_level))
        self.led_output_pin.value(gpio_level)
