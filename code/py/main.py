# This file is executed on every boot (including wake-boot from deepsleep) AFTER boot.py (if applicable)

# listen for input from a switch (GPIO 15) for 15 seconds
def switch_test():
    from switch import Switch
    switch_in = Switch(15)
    switch_in.listen(15000, 250)

# print heap usage
def print_heap_usage():
    import gc
    print('Free Heap: {}, Allocated Heap: {}'.format(gc.mem_free(), gc.mem_alloc()))
    # could also use: import micropython; micropython.mem_info()

def main():
    print('Running main.py..')
    print_heap_usage()
    # switch_test()

main()