_shadow_delta_cb: function = None

def __get_shadow_prefix_str(client_id: str) -> str:
    return "$aws/things/{}/shadow".format(client_id)

def __on_shadow_update_accepted(topic_name: str, json_payload: dict) -> None:
    del topic_name, json_payload
    print("Shadow update accepted")

def __on_shadow_update_rejected(topic_name: str, json_payload: dict) -> None:
    del topic_name, json_payload
    print("Shadow update rejected")

def __on_shadow_update_delta(topic_name: str, json_payload: dict) -> None:
    del topic_name

    if _shadow_delta_cb is None or _shadow_delta_cb == None:
        # shadow delta callback is not defined
        return

    # the payload contains metadata, only pass the "state" object (dict)
    _shadow_delta_cb(json_payload["state"])

def subscribe_to_shadow_topics() -> None:
    from ..aws_iot_client import subscribe as aws_subscribe, get_thing_name as aws_get_thing_name

    client_id: str = aws_get_thing_name()
    aws_subscribe("{}/update/accepted".format(__get_shadow_prefix_str(client_id)), __on_shadow_update_accepted)
    aws_subscribe("{}/update/rejected".format(__get_shadow_prefix_str(client_id)), __on_shadow_update_rejected)
    aws_subscribe("{}/update/delta".format(__get_shadow_prefix_str(client_id)), __on_shadow_update_delta)

def update(properties: dict) -> None:
    from ..aws_iot_client import get_thing_name as aws_get_thing_name, publish as aws_publish
    import ujson

    client_id: str = aws_get_thing_name()
    shadow_update_topic = "{}/update".format(__get_shadow_prefix_str(client_id))

    # build JSON shadow state doc
    shadow_state_doc_json = {"state": {"reported": properties}}

    # convert JSON shadow state doc to string and publish
    shadow_state_doc_str = ujson.dumps(shadow_state_doc_json)
    aws_publish(shadow_update_topic, shadow_state_doc_str)

def set_delta_callback(on_shadow_delta_cb: function) -> None:
    global _shadow_delta_cb
    _shadow_delta_cb = on_shadow_delta_cb