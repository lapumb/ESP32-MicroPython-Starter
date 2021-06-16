_high_temperature_threshold_f: int = 124
_normal_temperature_threshold_f: int = 123
_temperature_fault_is_active: bool = False

def __temperature_threshold_is_valid(high_temp_threshold_f: int, normal_temp_threshold_f: int) -> bool:
    return high_temp_threshold_f > normal_temp_threshold_f

def set_high_temperature_threshold_F(high_temperature_threshold_f: int) -> None:
    global _high_temperature_threshold_f, _normal_temperature_threshold_f
    if not __temperature_threshold_is_valid(high_temperature_threshold_f, _normal_temperature_threshold_f):
        print("Invalid temperature threshold: high temperature threshold ({}) must be greater than normal temperature threshold ({})".format(high_temperature_threshold_f, _normal_temperature_threshold_f))
        return
    _high_temperature_threshold_f = high_temperature_threshold_f

def get_high_temperature_threshold_F() -> int:
    return _high_temperature_threshold_f

def set_normal_temperature_threshold_F(normal_temperature_threshold_f: int) -> None:
    global _high_temperature_threshold_f, _normal_temperature_threshold_f
    if not __temperature_threshold_is_valid(_high_temperature_threshold_f, normal_temperature_threshold_f):
        print("Invalid temperature threshold: high temperature threshold ({}) must be greater than normal temperature threshold ({})".format(_high_temperature_threshold_f, normal_temperature_threshold_f))
        return
    _normal_temperature_threshold_f = normal_temperature_threshold_f

def get_normal_temperature_threshold_F() -> int:
    return _normal_temperature_threshold_f

def get_fault_is_active() -> bool:
    return _temperature_fault_is_active

async def fault_task(on_fault_event_cb: function, delay_between_reads_ms: int = 50) -> None:
    assert delay_between_reads_ms >= 50
    assert on_fault_event_cb is not None and on_fault_event_cb != None
    global _temperature_fault_is_active, _high_temperature_threshold_f, _normal_temperature_threshold_f
    import uasyncio, hardware_manager

    _temperature_fault_is_active = False
    while True:
        temperature_fault_was_previously_active = _temperature_fault_is_active
        current_mcu_temperature_f: int = hardware_manager.get_mcu_temperature_F()

        # A temperature fault is currently active in one of two scenerios:
        # 1. The current MCU temperature reads above the high threshold
        # 2. A fault was previously active AND the current MCU temperature is greater than the normal threshold
        temperature_is_high: bool = (current_mcu_temperature_f > _high_temperature_threshold_f)
        temperature_fault_active_and_above_normal_threshold: bool = (temperature_fault_was_previously_active and (current_mcu_temperature_f > _normal_temperature_threshold_f))
        _temperature_fault_is_active = (temperature_is_high or temperature_fault_active_and_above_normal_threshold)

        new_fault_active: bool = not temperature_fault_was_previously_active and _temperature_fault_is_active
        fault_was_cleared: bool = temperature_fault_was_previously_active and not _temperature_fault_is_active
        if new_fault_active:
            print("New temperature fault! Current MCU temperature: {} degrees Fahrenheit".format(current_mcu_temperature_f))
            on_fault_event_cb(True, current_mcu_temperature_f)
        elif fault_was_cleared:
            print("Temperature fault cleared! Current MCU temperature: {} degrees Fahrenheit".format(current_mcu_temperature_f))
            on_fault_event_cb(False, current_mcu_temperature_f)
        # else: no change

        await uasyncio.sleep_ms(delay_between_reads_ms)