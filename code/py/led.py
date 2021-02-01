class Led:
    # valid output pins (GPIO)
    OUTPUT_PINS = [2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33]

    # 0 -3 (inclusive)
    MAX_TIMER_NUM = 3

    timer_number = 0
    gpio_num = -1

    def __init__(self, gpio_num, timer_number):
        self.gpio_num = gpio_num
        self.timer_number = timer_number
        print('LED pin:', self.gpio_num)
        print('LED timer number:', self.timer_number)

    def __valid(self):
        if self.gpio_num not in self.OUTPUT_PINS:
            print('Specified LED GPIO number', self.gpio_num, 'does not support output')
            return False

        if self.timer_number < 0 or self.timer_number > self.MAX_TIMER_NUM:
            print('Invalid LED timer number', self.timer_number, '... Timer number must be between 0 -', self.MAX_TIMER_NUM)
            return False

        return True

    def toggle(self, frequency_ms):
        from machine import Pin, Timer

        if not self.__valid():
            return

        # create output pin
        output_pin = Pin(self.gpio_num, Pin.OUT)

        # Create timer (see https://docs.micropython.org/en/latest/library/machine.Timer.html#machine-timer)
        timer = Timer(self.timer_number)

        # Start periodic timer to toggle LED every 'frequency_ms' milliseconds
        print('Starting LED toggle timer', self.timer_number)
        timer.init(period=frequency_ms, mode=Timer.PERIODIC, callback=lambda t:output_pin.value((output_pin.value() + 1) % 2))
