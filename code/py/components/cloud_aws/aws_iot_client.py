# TODO: comment explanation of the class and it"s purposes, shortcomings, etc

import uasyncio
from ..simple_queue.simple_queue import SimpleQueue
from .priv import aws_jobs
from .priv import aws_shadow
try:
    from umqtt.robust import MQTTClient
except ImportError:
    import upip
    upip.install("micropython-umqtt.simple")
    upip.install("micropython-umqtt.robust")
    from umqtt.robust import MQTTClient

class AWSIoTClient:

    _MQTT_PORT: int = 8883

    _cert: str = ""
    _key: str = ""
    _client_id: str = ""

    _mqtt_client: MQTTClient = None
    _mqtt_client_is_connected: bool = False

    # a dictionary of AWS MQTT subscriptions: <"topic_name", on_topic_cb>
    _mqtt_subscriptions_dict: dict = dict()

    # a queue of telemetry messages waiting to be sent
    # each message is stored at as a tuple: (topic_name, json_payload_str)
    _telemetry_queue: SimpleQueue = SimpleQueue(15)

    def __byte_array_to_string(self, byte_arr: bytearray) -> str:
        return byte_arr.decode("utf-8")

    def __top_level_subscription_cb(self, topic_name: bytearray, json_payload: bytearray) -> None:
        topic_name_str: str = self.__byte_array_to_string(topic_name)
        json_payload_str: str = self.__byte_array_to_string(json_payload)

        try:
            callback = self._mqtt_subscriptions_dict.get(topic_name_str)
            if callback is not None:
                callback(topic_name_str, json_payload_str)
        except Exception as error:
            print("An error occured upon receiving subscription payload: " + str(error))

    def __publish(self, topic_name: str, json_payload_str: str) -> None:
        if not self._mqtt_client_is_connected:
            print("Cannot publish telemetry, AWS is not connected")
            return

        print("publishing to " + topic_name + ": " + json_payload_str)

        try:
            self._mqtt_client.publish(topic_name, json_payload_str, qos=1)
        except Exception as error:
            print("Failed to publish telemetry message: " + str(error))
            raise

    def __publish_queued_messages(self) -> None:
        telemetry_data = self._telemetry_queue.dequeue()
        while telemetry_data is not None:
            topic_name: str = telemetry_data[0]
            json_payload_str: str = telemetry_data[1]
            self.__publish(topic_name, json_payload_str)

            # get the next message
            telemetry_data = self._telemetry_queue.dequeue()

    def __setup_subscriptions(self, mqtt_client: MQTTClient) -> None:
        assert mqtt_client is not None

        # see warnings about subscriptions here: https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.robust/example_sub_robust.py
        try:
            mqtt_client.set_callback(self.__top_level_subscription_cb)
        except Exception as error:
            print("Error registering subsctiption callback: " + str(error))
            raise

    def __connect_mqtt_client(self, client_id: str, host_name: str) -> None:
        print("Connecting to AWS MQTT client..")
        try:
            self._mqtt_client = MQTTClient(client_id=client_id, server=host_name, port=self._MQTT_PORT, keepalive=10000, ssl=True, ssl_params={"cert":self._cert, "key":self._key, "server_side":False})
            self.__setup_subscriptions(self._mqtt_client)
            self._mqtt_client.connect()
            print("MQTT client connected successfully!")
        except Exception as error:
            print("An error occured when connecting to AWS MQTT client: " + str(error))
            raise

    def __init__(self, client_id: str, host_name: str, cert_file_path: str, key_file_path: str) -> None:
        """Connect to AWS and subscribe to AWS Jobs and Shadow Document topics.

        Parameters
        ----------
        `client_id` : str
            The device's client ID, typically the device serial number

            Note: this CANNOT be None

        `host_name` : str
            The host name used to connect to the MQTT server

            Note: this CANNOT be None

        `cert_file_path` : str
            The local, relative path to the AWS certificate file (i.e., aws_config/cert.pem)

            Note: this CANNOT be None

        `key_file_path` : str
            The local, relative path to the private-key file (i.e., aws_config/private.key)

            Note: this CANNOT be None

        Exceptions
        ----------
        An exception will be raised if:

        1. The cert file cannot be read

        2. The key file cannot be read

        3. An MQTT connection cannot be established
        """
        assert client_id != None
        assert host_name != None
        assert cert_file_path != None
        assert key_file_path != None

        from ..wifi import wifi
        if not wifi.is_connected():
            print("Cannot initialize an AWS IoT Client if wifi is not connected")
            return

        print("---------------------------------------")
        print("client_id: " + client_id)
        print("host_name: " + host_name)
        print("cert_file_path: " + cert_file_path)
        print("key_file_path: " + key_file_path)
        print("---------------------------------------")

        try:
            with open(cert_file_path, "r") as cert_file:
                self._cert = cert_file.read()

            with open(key_file_path, "r") as key_file:
                self._key = key_file.read()
        except Exception as error:
            print("An error occured when reading AWS credentials: " + str(error))
            raise

        self.__connect_mqtt_client(client_id, host_name)

        self._client_id = client_id
        self._mqtt_client_is_connected = True

        # initialize aws_shadow module and subscribe to topics
        aws_shadow.init(self)
        aws_shadow.subscribe_to_shadow_topics()

        # initialize aws_jobs module, subscribe to topics, and check for any pending jobs
        aws_jobs.init(self)
        aws_jobs.subscribe_to_jobs_topics()
        aws_jobs.get_next_job()

    def disconnect(self) -> None:
        """Disconnect the MQTT client from AWS"""
        self._mqtt_client_is_connected = False
        self._mqtt_client.disconnect()

    def get_client_id(self) -> str:
        """Get the client ID of the MQTT client

        Returns
        -------
        str : the client ID of the MQTT client
        """
        return self._client_id

    def subscribe(self, topic_name: str, callback: function) -> None:
        """Subscribe to an MQTT topic.

        Parameters
        ----------
        `topic_name` : str
            The topic name to subscribe to

        `callback` : function
            Called when a payload is received at the subscribed topic_name, where the topic name and payload are passed into the function

            Note: this CANNOT be None
        """
        assert callback is not None
        if not self._mqtt_client_is_connected:
            print("Cannot subscribe to topic, AWS is not connected")
            return

        try:
            self._mqtt_client.subscribe(topic_name)
            self._mqtt_subscriptions_dict[topic_name] = callback
            print("Subscribed to topic: " + topic_name)
        except Exception as error:
            print("Failed to subscribe to topic (" + topic_name + "): " + str(error))
            raise

    def publish(self, topic_name: str, json_payload_str: str) -> None:
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
        assert topic_name != None and json_payload_str != None
        self._telemetry_queue.enqueue((topic_name, json_payload_str))

    def update_shadow(self, properties: dict) -> None:
        """Update the device shadow document

        Parameters
        ----------
        `properties` : dict
            A dictionary of properties to report to the devices AWS shadow document

            Note: this CANNOT be None
        """
        assert properties != None
        aws_shadow.update(properties)

    def set_shadow_delta_callback(self, on_shadow_delta_cb: function) -> None:
        """Set the callback to be called whenever a payload is received at `$aws/things/{CLIENT_ID}/shadow/update/delta`

        Parameters
        ----------
        `on_shadow_delta_cb` : function
            Called whenever a payload is received at `$aws/things/{CLIENT_ID}/shadow/update/delta`, where a dictionary
            of "desired" properties are passed into the function

            Note: this CANNOT be None
        """
        assert on_shadow_delta_cb != None
        aws_shadow.set_delta_callback(on_shadow_delta_cb)

    def aws_jobs_register_operation(self, operation_id: str, on_operation_cb: function) -> None:
        """Register a callback to be called when the "operation" token is parsed and matches the operation_id

        Parameters
        ----------
        `operation_id` : str
            string identifier compared against "operation" token value

            Note: this CANNOT be None

        `on_operation_cb` : function
            function called when operation_id matches the "operation" token

            Note: this CANNOT be None
        """
        aws_jobs.register_operation(operation_id, on_operation_cb)

    def aws_jobs_publish_update(self, job_id: str, job_execution_status: int, status_detail_str: str) -> None:
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
        assert job_id != None
        aws_jobs.publish_update(job_id, job_execution_status, status_detail_str)

    async def aws_task(self) -> None:
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
        from ..wifi import wifi
        assert wifi.is_connected()

        while True:
            # publish queued telemetry messages
            self.__publish_queued_messages()

            # check for any incoming mesages
            self._mqtt_client.check_msg()

            await uasyncio.sleep_ms(100)