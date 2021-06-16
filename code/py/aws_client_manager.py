from components.cloud_aws.aws_iot_client import AWSIoTClient
import hardware_manager, temperature_monitor, utils

_SHADOW_PROPERTY_TUPLE_GETTER_INDEX: int = 0
_SHADOW_PROPERTY_TUPLE_DELTA_CB_INDEX: int = 1

_aws_client: AWSIoTClient = None

def __get_serial_number() -> str:
    # for now, just report the client ID as the serial number
    return _aws_client.get_client_id()

def __on_thresholds_mqtt(topic_name: str, payload: str) -> None:
    del topic_name, payload
    print("TODO: set new thresholds")

def __on_thresholds_job(job_id: str, job_doc: dict) -> tuple:
    import components.aws_job_execution_status as execution_status
    del job_id, job_doc
    return (execution_status.AWS_JOB_EXECUTION_IN_PROGRESS, "TODO: set new thresholds..")

def __on_high_temperature_threshold_F(property: str, new_threshold_f: int) -> None:
    del property
    hardware_manager.set_high_temperature_threshold_F(new_threshold_f)

def __on_normal_temperature_threshold_F(property: str, new_threshold_f: int) -> None:
    del property
    hardware_manager.set_normal_temperature_threshold_F(new_threshold_f)

#    property name                    value "get" function                                     delta callback function
_shadow_properties = {
    "micropython_version":            (utils.get_micropython_version,                          None),
    "serial_number":                  (__get_serial_number,                                    None),
    "mcu_temperature_f":              (hardware_manager.get_mcu_temperature_F,                 None),
    "high_temperature_threshold_f":   (temperature_monitor.get_high_temperature_threshold_F,   __on_high_temperature_threshold_F),
    "normal_temperature_threshold_f": (temperature_monitor.get_normal_temperature_threshold_F, __on_normal_temperature_threshold_F),
    "temperature_fault_active":       (temperature_monitor.get_fault_is_active,                None),
}

def __get_telemetry_prefix_str() -> str:
    assert _aws_client is not None and _aws_client != None
    return "device/micropython_example/{}".format(_aws_client.get_client_id())

def __on_shadow_delta(delta_dict: dict) -> None:
    # walk through delta dictionary
    for delta_property, delta_value in delta_dict.items():
        # if delta property (key) is a shadow property
        if delta_property in _shadow_properties:
            # get the callback function
            delta_callback = _shadow_properties[delta_property][_SHADOW_PROPERTY_TUPLE_DELTA_CB_INDEX]
            # if the callback is not None, call it
            if delta_callback is not None and delta_callback != None:
                delta_callback(delta_property, delta_value)
                shadow_update()
            else:
                print("delta property is not settable!")
        else:
            print("delta property {} is not a shadow property".format(delta_property))

async def __shadow_update_task(frequency_ms: int) -> None:
    assert frequency_ms >= 60000

    import uasyncio
    while True:
        shadow_update()
        await uasyncio.sleep_ms(frequency_ms)

def init(client_id: str, host_name: str, cert_file_path: str, key_file_path: str, shadow_update_frequency: int=120000) -> None:
    assert client_id is not None and client_id != None
    assert host_name is not None and host_name != None
    assert cert_file_path is not None and cert_file_path != None
    assert key_file_path is not None and key_file_path != None

    try:
        global _aws_client
        _aws_client = AWSIoTClient(client_id, host_name, cert_file_path, key_file_path)
        _aws_client.subscribe("$aws/things/blakes_micropython_esp32_2/thresholds", __on_thresholds_mqtt)
        _aws_client.set_shadow_delta_callback(__on_shadow_delta)
        _aws_client.aws_jobs_register_operation("set_thresholds", __on_thresholds_job)
    except Exception as error:
        print("Failed to initialize AWS IoT Client: " + str(error))
        raise

    import uasyncio
    uasyncio.create_task(_aws_client.aws_task())
    uasyncio.create_task(__shadow_update_task(shadow_update_frequency))

def shadow_update() -> None:
    shadow_property_dict = dict()
    for property, tuple_callbacks in _shadow_properties.items():
        property_getter = tuple_callbacks[_SHADOW_PROPERTY_TUPLE_GETTER_INDEX]
        if property_getter is not None:
            property_val = property_getter()
            shadow_property_dict[str(property)] = property_val

    _aws_client.update_shadow(shadow_property_dict)

def publish_temperature_fault_event_telemetry(fault_is_active: bool, current_mcu_temperature_f: int, high_temperature_threshold_f: int, normal_temperature_threshold_f: int) -> None:
    import ujson
    topic_name: str = "{}/event/temperature_fault".format(__get_telemetry_prefix_str())
    json_payload: dict = {"fault_is_active": fault_is_active, "current_mcu_temperature_f": current_mcu_temperature_f, "high_temperature_threshold_f": high_temperature_threshold_f, "normal_temperature_threshold_f": normal_temperature_threshold_f}
    json_payload_str: str = ujson.dumps(json_payload)
    _aws_client.publish(topic_name, json_payload_str)
