# This file is executed on every boot (including wake-boot from deepsleep) AFTER boot.py (if applicable)

def main():
    from switch import Switch
    print('Running main.py..')
    switch_in = Switch(15)
    switch_in.listen(15000, 250)

main()