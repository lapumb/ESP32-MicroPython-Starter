# see https://docs.micropython.org/en/latest/library/uasyncio.html
import uasyncio

class Switch:
    # valid input pins (GPIO)
    INPUT_PINS = [2, 4, 5, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33, 34, 35, 36, 39]

    gpio_num = -1

    def __init__(self, gpio_num):
        self.gpio_num = gpio_num

    def __valid(self):
        if self.gpio_num not in self.INPUT_PINS:
            print('Specified switch GPIO number (', self.gpio_num, ') does not support input')
            return False
        return True

    async def __listen(self, switch_instance, total_length_ms, delay_ms):
        current_value = 'off'
        previous_value = ''
        listen_length_ms = 0

        while listen_length_ms <= total_length_ms:
            if switch_instance.value() == 0:
                current_value = 'off'
            else:
                current_value = 'on'

            if current_value is not previous_value:
                print('Switch is now:', current_value)

            listen_length_ms += delay_ms
            previous_value = current_value
            await uasyncio.sleep_ms(delay_ms)

        print('Done listening to switch input')

    def listen(self, total_listen_length_ms, delay_ms):
        from machine import Pin

        if not self.__valid():
            return

        switch_instance = Pin(self.gpio_num, Pin.IN)
        uasyncio.run(self.__listen(switch_instance, total_listen_length_ms, delay_ms))

