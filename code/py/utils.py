def print_heap_usage() -> None:
    import gc
    gc.collect()
    print("Free Heap: {}, Allocated Heap: {}".format(gc.mem_free(), gc.mem_alloc()))

def print_heap_usage_raw() -> None:
    import micropython, gc
    gc.collect()
    micropython.mem_info()

def get_micropython_version() -> str:
    import os

    # uname is a tuple containing the following:
    # (sysname="esp32", nodename="esp32", release="1.15.0", version="v1.15 on 2021-04-18", machine="ESP32 module with ESP32")
    return os.uname()[3]