from ..simple_queue.simple_queue import SimpleQueue
try:
    from umqtt.robust import MQTTClient
except ImportError:
    import upip
    # umqtt.robust depends on umqtt.simple, so we need to install both
    upip.install("micropython-umqtt.simple")
    upip.install("micropython-umqtt.robust")
    from umqtt.robust import MQTTClient

_MQTT_PORT: int = 8883

_thing_name: str = ""
_mqtt_client: MQTTClient = None
_mqtt_client_is_connected: bool = False
_initialized: bool = False

# a dictionary of AWS MQTT subscriptions: <"topic_name", on_topic_cb>
_mqtt_subscriptions_dict: dict = dict()

# a queue of telemetry messages waiting to be sent
# each message is stored at as a tuple: (topic_name, json_payload_str)
_telemetry_queue: SimpleQueue = None

def __byte_array_to_string(byte_arr: bytearray) -> str:
    return byte_arr.decode("utf-8")

def __top_level_subscription_cb(topic_name: bytearray, json_payload: bytearray) -> None:
    import ujson
    global _mqtt_subscriptions_dict

    topic_name_str: str = __byte_array_to_string(topic_name)
    json_payload_str: str = __byte_array_to_string(json_payload)
    json_payload_dict: dict = ujson.loads(json_payload_str)

    try:
        callback = _mqtt_subscriptions_dict.get(topic_name_str)
        if callback is not None and callback != None:
            callback(topic_name_str, json_payload_dict)
    except Exception as error:
        print("Topic {0}: An error occured upon receiving subscription payload: {1}".format(topic_name_str, str(error)))

def __publish(topic_name: str, json_payload_str: str) -> None:
    global _initialized, _mqtt_client_is_connected, _mqtt_client

    assert _initialized
    assert _mqtt_client_is_connected

    print("publishing to " + topic_name + ": " + json_payload_str)

    try:
        _mqtt_client.publish(topic_name, json_payload_str, qos=1)
    except Exception as error:
        print("Failed to publish telemetry message: " + str(error))
        raise

def __publish_queued_messages() -> None:
    global _telemetry_queue
    telemetry_data = _telemetry_queue.dequeue()
    while telemetry_data is not None:
        topic_name: str = telemetry_data[0]
        json_payload_str: str = telemetry_data[1]
        __publish(topic_name, json_payload_str)

        # get the next message
        telemetry_data = _telemetry_queue.dequeue()

def __setup_subscriptions(mqtt_client: MQTTClient) -> None:
    assert mqtt_client is not None and mqtt_client != None

    # see warnings about subscriptions here: https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.robust/example_sub_robust.py
    try:
        mqtt_client.set_callback(__top_level_subscription_cb)
    except Exception as error:
        print("Error registering subsctiption callback: " + str(error))
        raise

def __connect_mqtt_client(thing_name: str, host_name: str, cert: str, private_key: str) -> None:
    global _mqtt_client

    try:
        print("Connecting to AWS MQTT client..")
        _mqtt_client = MQTTClient(client_id=thing_name, server=host_name, port=_MQTT_PORT, keepalive=10000, ssl=True, ssl_params={"cert":cert, "key":private_key, "server_side":False})
        __setup_subscriptions(_mqtt_client)
        _mqtt_client.connect()
        assert _mqtt_client is not None and _mqtt_client != None
        print("MQTT client connected successfully!")
    except Exception as error:
        print("An error occured when connecting to AWS MQTT client: " + str(error))
        raise

def init(thing_name: str, host_name: str, cert_file_path: str, private_key_file_path: str, telemetry_queue_size: int = 15) -> None:
    """Connect to AWS and subscribe to AWS Jobs and Shadow Document topics.

    Parameters
    ----------
    `thing_name` : str
        The device's AWS Thing name, typically the device serial number

        Note: this CANNOT be None

    `host_name` : str
        The host name used to connect to the MQTT server

        Note: this CANNOT be None

    `cert_file_path` : str
        The relative path to the AWS certificate file (i.e., aws_config/cert.pem)

        Note: this CANNOT be None

    `private_key_file_path` : str
        The relative path to the private-key file (i.e., aws_config/private.key)

        Note: this CANNOT be None

    `telemetry_queue_size` : int
        The size of the telemetry queue. The telemetry queue is appended to whenever `publish` is called. The queued telemetry (MQTT)
        messages are published as soon as possible.

        Default: 15

        Note: this must be at least 2

    Exceptions
    ----------
    An exception will be raised if:

    1. The cert file cannot be read

    2. The key file cannot be read

    3. An MQTT connection cannot be established
    """
    assert thing_name is not None and thing_name != None
    assert host_name is not None and host_name != None
    assert cert_file_path is not None and cert_file_path != None
    assert private_key_file_path is not None and private_key_file_path != None
    assert telemetry_queue_size is not None and telemetry_queue_size >= 2

    from ..wifi import wifi
    if not wifi.is_connected():
        print("Cannot initialize an AWS IoT Client if wifi is not connected")
        return

    print("---------------------------------------")
    print("thing_name: " + thing_name)
    print("host_name: " + host_name)
    print("cert_file_path: " + cert_file_path)
    print("private_key_file_path: " + private_key_file_path)
    print("telemetry_queue_size: " + str(telemetry_queue_size))
    print("---------------------------------------")

    global _telemetry_queue, _thing_name, _mqtt_client_is_connected, _initialized

    _telemetry_queue = SimpleQueue(telemetry_queue_size)

    try:
        with open(cert_file_path, "r") as cert_file:
            certificate: str = cert_file.read()

        with open(private_key_file_path, "r") as private_key_file:
            private_key: str = private_key_file.read()
    except Exception as error:
        print("An error occured when reading AWS credentials: " + str(error))
        raise

    __connect_mqtt_client(thing_name, host_name, certificate, private_key)

    _thing_name = thing_name
    _mqtt_client_is_connected = True
    _initialized = True

    # subscribe to topics shadow topics
    from .priv import aws_shadow
    aws_shadow.subscribe_to_shadow_topics()

    # subscribe to jobs topics and check for pending jobs
    from .priv import aws_jobs
    aws_jobs.subscribe_to_jobs_topics()
    aws_jobs.get_next_job()

def disconnect() -> None:
    """Disconnect the MQTT client from AWS"""
    global _mqtt_client_is_connected, _initialized
    assert _initialized
    _mqtt_client_is_connected = False
    _mqtt_client.disconnect()

def get_thing_name() -> str:
    """Get the devices AWS Thing name"""
    global _initialized, _thing_name
    assert _initialized
    return _thing_name

def subscribe(topic_name: str, callback: function) -> None:
    """Subscribe to an MQTT topic.

    Parameters
    ----------
    `topic_name` : str
        The topic name to subscribe to

        Note: this CANNOT be None

    `callback` : function
        Called when a payload is received at the subscribed topic_name, where the topic name (string) and json payload (dict) are passed into the function

        Signature: `on_subscription_cb(topic_name: str, json_payload: dict) -> None`

        Note: this CANNOT be None
    """
    global _initialized, _mqtt_client_is_connected, _mqtt_client, _mqtt_subscriptions_dict
    assert topic_name is not None and topic_name != None
    assert callback is not None and callback != None
    assert _initialized
    assert _mqtt_client_is_connected

    try:
        _mqtt_client.subscribe(topic_name)
        _mqtt_subscriptions_dict[topic_name] = callback
        print("Subscribed to topic: " + topic_name)
    except Exception as error:
        print("Failed to subscribe to topic (" + topic_name + "): " + str(error))
        raise

def publish(topic_name: str, json_payload_str: str) -> None:
    """Append a telemetry message to the telemetry queue to be published as soon as possible in start_task

    Parameters
    ----------
    `topic_name` : str
        The topic name to publish the json_payload_str to

        Note: this CANNOT be None

    `json_payload_str` : str
        The JSON payload, as a string, to publlish to topic_name

        Note: this CANNOT be None
    """
    global _initialized, _telemetry_queue
    assert _initialized
    assert topic_name is not None and topic_name != None
    assert json_payload_str is not None and json_payload_str != None
    _telemetry_queue.enqueue((topic_name, json_payload_str))

def update_shadow(properties: dict) -> None:
    """Update the device shadow document

    Parameters
    ----------
    `properties` : dict
        A dictionary of properties to report to the devices AWS shadow document

        Note: this CANNOT be None
    """
    global _initialized
    assert _initialized
    assert properties is not None and len(properties) != 0

    from .priv import aws_shadow
    aws_shadow.update(properties)

def set_shadow_delta_callback(on_shadow_delta_cb: function) -> None:
    """Set the callback to be called whenever a payload is received at `$aws/things/{CLIENT_ID}/shadow/update/delta`

    Parameters
    ----------
    `on_shadow_delta_cb` : function
        Called whenever a payload is received at `$aws/things/{CLIENT_ID}/shadow/update/delta`, where a dictionary
        of "desired" properties are passed into the function

        Signature: `on_shadow_delta(delta_properties: dict) -> None`

        Note: this CANNOT be None
    """
    global _initialized
    assert _initialized
    assert on_shadow_delta_cb is not None and on_shadow_delta_cb != None

    from .priv import aws_shadow
    aws_shadow.set_delta_callback(on_shadow_delta_cb)

def aws_jobs_register_operation(operation_id: str, on_operation_cb: function) -> None:
    """Register a callback to be called when the "operation" token is parsed and matches the operation_id

    Parameters
    ----------
    `operation_id` : str
        string identifier compared against "operation" token value

        Note: this CANNOT be None

    `on_operation_cb` : function
        function called when operation_id matches the "operation" token, where the job ID (str)
        and job document (dict) are passed

        Signature: `on_operation(job_id: str, job_document: dict) -> tuple`, where the returned tuple contains
        (AWS_JOB_EXECUTION_*: int, status_str: str)

        Note: this CANNOT be None
    """
    global _initialized
    assert _initialized
    assert operation_id is not None and operation_id != None
    assert on_operation_cb is not None and on_operation_cb != None

    from .priv import aws_jobs
    aws_jobs.register_operation(operation_id, on_operation_cb)

def aws_jobs_publish_update(job_id: str, job_execution_status: int, status_detail_str: str) -> None:
    """Append a telemetry message to the telemetry queue to be published as soon as possible in start_task

    Parameters
    ----------
    `job_id` : str
        The identification of the AWS Job to update

        Note: this CANNOT be None

    `job_execution_status` : int
        The status of the job execution (use `aws_job_execution_status.AWS_JOB_EXECUTION_*`)

    `status_detail_str` : str
        Details about the job execution status (i.e., "Job completed successfully!")
    """
    global _initialized
    assert _initialized
    assert job_id is not None and job_id != None

    from .priv import aws_jobs
    aws_jobs.publish_update(job_id, job_execution_status, status_detail_str)

async def aws_task() -> None:
    """The task to asyncronously publish queued messages and check for incoming messages

    Usage
    -----
    ```python
    import uasyncio
    main_loop = uasyncio.get_event_loop()
    aws_client = AWSIoTClient(client_id, host_name, cert_file_path, key_file_path)
    uasyncio.create_task(aws_client.aws_task())
    main_loop.run_forever()
    ```
    """
    global _initialized, _mqtt_client_is_connected, _mqtt_client
    import uasyncio
    from ..wifi import wifi
    assert wifi.is_connected()
    assert _initialized
    assert _mqtt_client_is_connected

    while True:
        # publish queued telemetry messages
        __publish_queued_messages()

        # check for any incoming mesages
        _mqtt_client.check_msg()

        await uasyncio.sleep_ms(100)