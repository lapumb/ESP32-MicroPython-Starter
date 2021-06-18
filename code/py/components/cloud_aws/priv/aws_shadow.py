from ..aws_iot_client import *

_initialized: bool = False
_aws_client: AWSIoTClient = None
_shadow_delta_cb: function = None

def __get_shadow_prefix_str(client_id: str) -> str:
    return "$aws/things/{}/shadow".format(client_id)

def __shadow_update_accepted(topic_name: str, json_payload: dict) -> None:
    del topic_name, json_payload
    print("Shadow update accepted")

def __shadow_update_rejected(topic_name: str, json_payload: dict) -> None:
    del topic_name, json_payload
    print("Shadow update rejected")

def __shadow_update_delta(topic_name: str, json_payload: dict) -> None:
    del topic_name

    if _shadow_delta_cb is None or _shadow_delta_cb == None:
        # shadow delta callback is not defined
        return

    # the payload contains metadata, only pass the "state" object (dict)
    _shadow_delta_cb(json_payload["state"])

def init(aws_client: AWSIoTClient) -> None:
    assert aws_client is not None and aws_client != None

    global _aws_client, _initialized
    _aws_client = aws_client
    _initialized = True

def subscribe_to_shadow_topics() -> None:
    assert _aws_client is not None and _aws_client != None
    assert _initialized

    client_id: str = _aws_client.get_thing_name()
    _aws_client.subscribe("{}/update/accepted".format(__get_shadow_prefix_str(client_id)), __shadow_update_accepted)
    _aws_client.subscribe("{}/update/rejected".format(__get_shadow_prefix_str(client_id)), __shadow_update_rejected)
    _aws_client.subscribe("{}/update/delta".format(__get_shadow_prefix_str(client_id)), __shadow_update_delta)

def update(properties: dict) -> None:
    assert _aws_client is not None and _aws_client != None
    assert properties is not None and len(properties) != 0
    assert _initialized

    import ujson

    client_id: str = _aws_client.get_thing_name()
    shadow_update_topic = "{}/update".format(__get_shadow_prefix_str(client_id))

    # build JSON shadow state doc
    shadow_state_doc_json = {"state": {"reported": properties}}

    # convert JSON shadow state doc to string and publish
    shadow_state_doc_str = ujson.dumps(shadow_state_doc_json)
    _aws_client.publish(shadow_update_topic, shadow_state_doc_str)

def set_delta_callback(on_shadow_delta_cb: function) -> None:
    assert on_shadow_delta_cb is not None and on_shadow_delta_cb != None
    global _shadow_delta_cb
    _shadow_delta_cb = on_shadow_delta_cb