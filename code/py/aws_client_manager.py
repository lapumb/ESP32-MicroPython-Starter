from components.cloud_aws.aws_iot_client import AWSIoTClient
import components.utils.utils as utils

_SHADOW_PROPERTY_TUPLE_GETTER_INDEX: int = 0
_SHADOW_PROPERTY_TUPLE_DELTA_CB_INDEX: int = 1

_aws_client: AWSIoTClient = None

_dummy_delta_int: int = 0

def __get_serial_number() -> str:
    # for now, just report the client ID as the serial number
    return _aws_client.get_client_id()

def __get_dummy_delta_int() -> int:
    return _dummy_delta_int

def __on_dummy_delta_int(property: str, value: int) -> None:
    global _dummy_delta_int
    print("Setting {0} from {1} to {2}!".format(property, _dummy_delta_int, value))
    _dummy_delta_int = value

def __on_dummy_event(topic_name: str, payload: str) -> None:
    print("Topic {0} received: {1}".format(topic_name, payload))

def __on_dummy_job(job_id: str, job_doc: dict) -> tuple:
    import components.cloud_aws.aws_job_execution_status as execution_status
    del job_doc
    return (execution_status.AWS_JOB_EXECUTION_SUCCEEDED, "Successfully received job {}!".format(job_id))

#    property name          value "get" function (cannot be None)                 delta callback function (can be None)
_shadow_properties = {
    "micropython_version": (utils.get_micropython_version,                        None),
    "serial_number":       (__get_serial_number,                                  None),
    "dummy_delta_int":     (__get_dummy_delta_int,                                __on_dummy_delta_int),
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

async def __dummy_telemetry_publish_task() -> None:
    import uasyncio, ujson
    publish_count: int = 0
    topic_name: str = "{}/client/event/dummy".format(__get_telemetry_prefix_str())
    json_payload: dict = {"event_name": "client_dummy_event"}

    while True:
        publish_count += 1
        json_payload["publish_count"] = publish_count
        json_payload_str: str = ujson.dumps(json_payload)
        _aws_client.publish(topic_name, json_payload_str)
        await uasyncio.sleep_ms(60_000)

def init(client_id: str, host_name: str, cert_file_path: str, key_file_path: str, shadow_update_frequency: int=120000) -> None:
    assert client_id is not None and client_id != None
    assert host_name is not None and host_name != None
    assert cert_file_path is not None and cert_file_path != None
    assert key_file_path is not None and key_file_path != None

    try:
        global _aws_client
        _aws_client = AWSIoTClient(client_id, host_name, cert_file_path, key_file_path)
    except Exception as error:
        print("Failed to initialize AWS IoT Client: " + str(error))
        raise

    _aws_client.set_shadow_delta_callback(__on_shadow_delta)

    dummy_topic_name: str = "{}/server/event/dummy".format(__get_telemetry_prefix_str())
    _aws_client.subscribe(dummy_topic_name, __on_dummy_event)
    _aws_client.aws_jobs_register_operation("dummy", __on_dummy_job)

    import uasyncio
    uasyncio.create_task(_aws_client.aws_task())
    uasyncio.create_task(__shadow_update_task(shadow_update_frequency))
    uasyncio.create_task(__dummy_telemetry_publish_task())

def shadow_update() -> None:
    shadow_property_dict = dict()
    for property, tuple_callbacks in _shadow_properties.items():
        property_getter = tuple_callbacks[_SHADOW_PROPERTY_TUPLE_GETTER_INDEX]
        if property_getter is not None:
            property_val = property_getter()
            shadow_property_dict[str(property)] = property_val

    _aws_client.update_shadow(shadow_property_dict)
