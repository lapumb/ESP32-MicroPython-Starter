from components.cloud_aws.aws_iot_client import AWSIoTClient
import hardware_manager, utils

SHADOW_PROPERTY_TUPLE_GETTER_INDEX: int = 0
SHADOW_PROPERTY_TUPLE_DELTA_CB_INDEX: int = 1

_aws_client: AWSIoTClient = None

def __on_red_led_on(property: str, new_led_status: bool) -> None:
    del property
    hardware_manager.set_red_led_on(new_led_status)

def __on_green_led_on(property: str, new_led_status: bool) -> None:
    del property
    hardware_manager.set_green_led_on(new_led_status)

def __on_blue_led_on(property: str, new_led_status: bool) -> None:
    del property
    hardware_manager.set_blue_led_on(new_led_status)

#    property name          value "get" function               delta callback function
_shadow_properties = {
    "micropython_version": (utils.get_micropython_version,     None),
    "switch_gpio_level":   (hardware_manager.get_switch_value, None),
    "white_led_on":        (hardware_manager.get_white_led_on, None),
    "red_led_on":          (hardware_manager.get_red_led_on,   __on_red_led_on),
    "green_led_on":        (hardware_manager.get_green_led_on, __on_green_led_on),
    "blue_led_on":         (hardware_manager.get_blue_led_on,  __on_blue_led_on)
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
            delta_callback = _shadow_properties[delta_property][SHADOW_PROPERTY_TUPLE_DELTA_CB_INDEX]
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
        # _aws_client.subscribe("$aws/things/blakes_micropython_esp32/bulb", None)
        _aws_client.set_shadow_delta_callback(__on_shadow_delta)
    except Exception as error:
        print("Failed to initialize AWS IoT Client: " + str(error))
        raise

    import uasyncio
    uasyncio.create_task(_aws_client.aws_task())
    uasyncio.create_task(__shadow_update_task(shadow_update_frequency))

def shadow_update() -> None:
    shadow_property_dict = dict()
    for property, tuple_callbacks in _shadow_properties.items():
        property_getter = tuple_callbacks[SHADOW_PROPERTY_TUPLE_GETTER_INDEX]
        if property_getter is not None:
            property_val = property_getter()
            shadow_property_dict[str(property)] = property_val

    _aws_client.update_shadow(shadow_property_dict)

def publish_gpio_change_event_telemetry(gpio_id: str, gpio_number: int, current_gpio_level: int, previous_gpio_level: int) -> None:
    import ujson
    topic_name: str = "{}/event/gpio_change".format(__get_telemetry_prefix_str())
    json_payload: dict = {"gpio_id": gpio_id, "gpio_number": gpio_number, "current_gpio_level": current_gpio_level, "previous_gpio_level": previous_gpio_level}
    json_payload_str: str = ujson.dumps(json_payload)
    _aws_client.publish(topic_name, json_payload_str)
