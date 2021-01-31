class Led:
    # valid output pins
    OUTPUT_PINS = [2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33]

    # 0 -3 (inclusive)
    MAX_TIMER_NUM = 3

    timerNumber = 0
    pinNumber = -1

    def __init__(self, pinNumber, timerNumber):
        self.pinNumber = pinNumber
        self.timerNumber = timerNumber
        print('using pin: ', self.pinNumber)
        print('using timer number: ', self.timerNumber)

    def __valid(self):
        if self.pinNumber not in self.OUTPUT_PINS:
            print('Specified pin number does not support output')
            return False

        if self.timerNumber < 0 or self.timerNumber > self.MAX_TIMER_NUM:
            print('invalid timer number', self.timerNumber)
            return False

        return True

    def toggle(self, frequencyMilliseconds):
        from machine import Pin, Timer

        if not self.__valid():
            return

        # create output pin
        p = Pin(self.pinNumber, Pin.OUT)

        # Create timer (see https://docs.micropython.org/en/latest/library/machine.Timer.html#machine-timer)
        tim = Timer(self.timerNumber)

        # Start periodic timer to toggle LED every 'frequencyMilliseconds' milliseconds
        print('Starting LED toggle timer')
        tim.init(period=frequencyMilliseconds, mode=Timer.PERIODIC, callback=lambda t:p.value((p.value() + 1) % 2))
