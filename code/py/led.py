class Led:
    # somme default pin
    pinNumber = -1

    # 0 -3 (inclusive)
    timerNum = 0
    MAX_TIMER_NUM = 3

    def __init__(self, pinNumber, timerNum):
        print('led pin: ', pinNumber)
        self.pinNumber = pinNumber
        if timerNum > self.MAX_TIMER_NUM or timerNum < 0:
            print('invalid timer number', timerNum)
            print('clipping to 0')
            self.timerNum = 0

    def toggle(self, frequency):
        from machine import Pin, Timer

        # create output pin on GPIO25
        p = Pin(self.pinNumber, Pin.OUT)

        # Create timer (see https://docs.micropython.org/en/latest/library/machine.Timer.html#machine-timer)
        tim = Timer(self.timerNum)

        # Start periodic timer to toggle LED every 2 seconds
        print('Starting LED toggle timer')
        tim.init(period=frequency, mode=Timer.PERIODIC, callback=lambda t:p.value((p.value() + 1) % 2))
