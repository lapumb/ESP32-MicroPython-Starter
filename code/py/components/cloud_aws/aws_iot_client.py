# TODO: comment explanation of the class and it"s purposes, shortcomings, etc

import ujson
import uasyncio
try:
    from umqtt.robust import MQTTClient
except ImportError:
    import upip
    upip.install("micropython-umqtt.simple")
    upip.install("micropython-umqtt.robust")
    from umqtt.robust import MQTTClient

class AWSIoTClient:

    MQTT_PORT = 8883

    cert = ""
    key = ""
    client_id = ""

    mqtt_client = None
    mqtt_client_is_connected = False

    shadow_delta_cb = None

    # a dictionary of AWS MQTT subscriptions: <"topic_name", on_topic_cb>
    subscriptions = dict()

    def __byte_array_to_string(self, byte_arr: bytearray) -> str:
        return byte_arr.decode("utf-8")

    def __get_shadow_prefix_str(self) -> str:
        return "$aws/things/{}/shadow".format(self.client_id)

    def __top_level_subscription_cb(self, topic_name: bytearray, payload: bytearray) -> None:
        topic_name_str: str = self.__byte_array_to_string(topic_name)
        payload_str: str = self.__byte_array_to_string(payload)

        try:
            callback = self.subscriptions.get(topic_name_str)
            if callback is not None:
                callback(topic_name_str, payload_str)
        except Exception as error:
            print("An error occured upon receiving subscription payload: " + str(error))

    def __setup_subscriptions(self) -> None:
        # see warnings about subscriptions here: https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.robust/example_sub_robust.py
        try:
            self.mqtt_client.set_callback(self.__top_level_subscription_cb)
        except Exception as error:
            print("Error registering subsctiption callback: " + str(error))
            raise

    def __shadow_update_accepted(self, topic_name: str, payload: str) -> None:
        del topic_name, payload
        print("Shadow update accepted")

    def __shadow_update_rejected(self, topic_name: str, payload: str) -> None:
        del topic_name, payload
        print("Shadow update rejected")

    def __shadow_update_delta(self, topic_name: str, payload: str) -> None:
        del topic_name
        parsed_delta = ujson.loads(payload)

        # the payload contains metadata, only pass the "state" object (dict)
        self.shadow_delta_cb(parsed_delta["state"])

    def __subscribe_to_shadow_topics(self) -> None:
        self.subscribe("{}/update/accepted".format(self.__get_shadow_prefix_str()), self.__shadow_update_accepted)
        self.subscribe("{}/update/rejected".format(self.__get_shadow_prefix_str()), self.__shadow_update_rejected)
        self.subscribe("{}/update/delta".format(self.__get_shadow_prefix_str()), self.__shadow_update_delta)

    def __connect_mqtt_client(self, client_id: str, host_name: str) -> None:
        print("Connecting to AWS MQTT client..")
        try:
            self.mqtt_client = MQTTClient(client_id=client_id, server=host_name, port=self.MQTT_PORT, keepalive=10000, ssl=True, ssl_params={"cert":self.cert, "key":self.key, "server_side":False})
            self.__setup_subscriptions()
            self.mqtt_client.connect()
            print("MQTT client connected successfully!")
        except Exception as error:
            print("An error occured when connecting to AWS MQTT client: " + str(error))
            raise

    def __init__(self, client_id: str, host_name: str, cert_file_path: str, key_file_path: str) -> None:
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
                self.cert = cert_file.read()

            with open(key_file_path, "r") as key_file:
                self.key = key_file.read()
        except Exception as error:
            print("An error occured when reading AWS credentials: " + str(error))
            raise

        self.__connect_mqtt_client(client_id, host_name)

        self.client_id = client_id
        self.mqtt_client_is_connected = True

        self.__subscribe_to_shadow_topics()

    def disconnect(self) -> None:
        """Disconnect the MQTT client"""
        self.mqtt_client.disconnect()

    def subscribe(self, topic_name: str, callback) -> None:
        """Subscribe to an MQTT topic.
        Parameters
        ----------
        topic_name : str
            The topic name to subscribe to
        callback : function
            Called when a payload is received at the subscribed topic_name, where the topic name and payload are passed into the function

            Note: this CANNOT be None
        """
        assert callback is not None
        if not self.mqtt_client_is_connected:
            print("Cannot subscribe to topic, AWS is not connected")
            return

        try:
            self.mqtt_client.subscribe(topic_name)
            self.subscriptions[topic_name] = callback
            print("Subscribed to topic: " + topic_name)
        except Exception as error:
            print("Failed to subscribe to topic (" + topic_name + "): " + str(error))
            raise

    def publish(self, topic_name: str, json_payload: str) -> None:
        if not self.mqtt_client_is_connected:
            print("Cannot publish telemetry, AWS is not connected")
            return

        print("publishing to " + topic_name + ": " + json_payload)

        try:
            self.mqtt_client.publish(topic_name, json_payload)
        except Exception as error:
            print("Failed to publish telemetry message: " + str(error))
            raise

    def update_shadow(self, properties: dict) -> None:
        assert properties is not None or len(properties) == 0

        shadow_update_topic = "{}/update".format(self.__get_shadow_prefix_str())

        # build JSON shadow state doc
        shadow_state_doc_json = {"state": {"reported": properties}}

        # convert JSON shadow state doc to string and publish
        shadow_state_doc_str = ujson.dumps(shadow_state_doc_json)
        self.publish(shadow_update_topic, shadow_state_doc_str)

    def set_shadow_delta_callback(self, on_shadow_delta_cb) -> None:
        """Set the callback to be called whenever a payload is received at $aws/things/{THING_NAME}/shadow/update/delta.
        Parameters
        ----------
        callback : function
            Called whenever a payload is received at $aws/things/{THING_NAME}/shadow/update/delta, where dictionary
            or "desired" properties are passed into the function.

            Note: this CANNOT be None
        """
        assert on_shadow_delta_cb is not None
        self.shadow_delta_cb = on_shadow_delta_cb

    async def task_start(self) -> None:
        """Start listening for incoming AWS IoT MQTT messages
        Note: this function listens for incoming messages asyncronously using uasyncio
            ```
            Usage:
                import uasyncio

                # Get loop
                main_loop = uasyncio.get_event_loop()

                # Create task
                uasyncio.create_task(aws_iot_client.start())

                # Start the loop
                main_loop.run_forever()
            ```
        """
        while True:
            self.mqtt_client.check_msg()
            await uasyncio.sleep_ms(500)