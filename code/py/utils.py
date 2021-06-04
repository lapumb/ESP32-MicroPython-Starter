def print_heap_usage() -> None:
    import gc
    gc.collect()
    print("Free Heap: {}, Allocated Heap: {}".format(gc.mem_free(), gc.mem_alloc()))

def print_heap_usage_raw() -> None:
    import micropython, gc
    gc.collect()
    micropython.mem_info()