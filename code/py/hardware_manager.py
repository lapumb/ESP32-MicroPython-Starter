def __on_temperature_fault_event(fault_active: bool, current_mcu_temperature_F) -> None:
    import aws_client_manager, temperature_monitor
    high_temperature_threshold_f: int = temperature_monitor.get_high_temperature_threshold_F()
    normal_temperature_threshold_f: int = temperature_monitor.get_normal_temperature_threshold_F()
    aws_client_manager.publish_temperature_fault_event_telemetry(fault_active, current_mcu_temperature_F, high_temperature_threshold_f, normal_temperature_threshold_f)

def get_mcu_temperature_F() -> int:
    import esp32
    return esp32.raw_temperature()

def init() -> None:
    import uasyncio, temperature_monitor
    uasyncio.create_task(temperature_monitor.fault_task(__on_temperature_fault_event, delay_between_reads_ms=1000))