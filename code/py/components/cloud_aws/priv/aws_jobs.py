from ..aws_job_execution_status import *

# a dictionary of operation subscriptions: <"operation", on_operation_cb>,
# where on_operation_cb has the signature: on_operation_cb(job_id: str, job_document: dict) -> (AWS_JOB_EXECUTION_*: int, status_str: str)
_operation_subscriptions: dict = dict()

# status string and status detail string dictionary: <aws_job_execution_status: int, ("statusDetail", "STATUS"): tuple>
_job_status_defs: dict = {
    AWS_JOB_EXECUTION_IN_PROGRESS: ("inProgressDetail", "IN_PROGRESS"),
    AWS_JOB_EXECUTION_FAILED: ("failDetail", "FAILED"),
    AWS_JOB_EXECUTION_SUCCEEDED: ("successDetail", "SUCCEEDED"),
    AWS_JOB_EXECUTION_REJECTED: ("rejectedDetail", "REJECTED")
}

def __get_jobs_prefix_str(client_id: str) -> str:
    return "$aws/things/{}/jobs".format(client_id)

def __aws_job_execution_status_to_detail_token_str(aws_job_execution_status: int) -> str:
    if aws_job_execution_status in _job_status_defs:
        return _job_status_defs[aws_job_execution_status][0]
    return "statusDetail"

def __aws_job_execution_to_str(aws_job_execution_status: int) -> str:
    if aws_job_execution_status in _job_status_defs:
        return _job_status_defs[aws_job_execution_status][1]
    return "UNKNOWN"

def __on_jobs_notify(topic_name: str, json_payload: dict) -> None:
    del topic_name
    print("on_jobs_notify: {}".format(str(json_payload)))
    get_next_job()

def __on_jobs_get_next_accepted(topic_name: str, json_payload: dict) -> None:
    del topic_name

    # try to get the execution. If it fails, return (we can't update the job without the job id)
    try:
        # Get the "execution" object. If it doesn"t exist, then there is no job to process
        execution: dict = json_payload["execution"]
    except Exception as error:
        return

    # try to get the job id. If it fails, return (we can't update the job without the job id)
    try:
        # Get the job ID from "execution" object
        job_id: str = execution["jobId"]
        print("job id: {}".format(job_id))
    except Exception as error:
        print("ERROR - Failed to parse JSON: {}".format(str(error)))
        return

    # try to get the job document and the operation. If either fails, REJECT the job
    try:
        # Get the job document
        job_document: dict = execution["jobDocument"]

        # Get the "operation" from the job document
        operation: str = job_document["operation"]
        print("opertaion: {}".format(operation))
    except Exception as error:
        publish_update(job_id, AWS_JOB_EXECUTION_REJECTED, "Failed to parse expected JSON object: {}".format(str(error)))
        return

    # get callback for operation
    try:
        operation_cb = _operation_subscriptions[operation]
    except Exception:
        publish_update(job_id, AWS_JOB_EXECUTION_REJECTED, "Operation {} not registered".format(operation))
        return

    # returned tuple: (AWS_JOB_EXECUTION_*: int, status_str: str)
    result_tuple = operation_cb(job_id, job_document)
    assert result_tuple is not None

    publish_update(job_id, result_tuple[0], result_tuple[1])

def __on_jobs_get_next_rejected(topic_name: str, json_payload: dict) -> None:
    del topic_name
    print("on_jobs_next_get_rejected: {}".format(str(json_payload)))

def subscribe_to_jobs_topics() -> None:
    from ..aws_iot_client import subscribe as aws_subscribe, get_thing_name as aws_get_thing_name

    client_id: str = aws_get_thing_name()
    aws_subscribe("{}/notify".format(__get_jobs_prefix_str(client_id)), __on_jobs_notify)
    aws_subscribe("{}/$next/get/accepted".format(__get_jobs_prefix_str(client_id)), __on_jobs_get_next_accepted)
    aws_subscribe("{}/$next/get/rejected".format(__get_jobs_prefix_str(client_id)), __on_jobs_get_next_rejected)

def get_next_job() -> None:
    from ..aws_iot_client import get_thing_name as aws_get_thing_name, publish as aws_publish
    aws_publish("{}/$next/get".format(__get_jobs_prefix_str(aws_get_thing_name())), "{}")

def publish_update(job_id: str, job_execution_status: int, status_detail_str: str) -> None:
    from ..aws_iot_client import get_thing_name as aws_get_thing_name, publish as aws_publish
    import ujson
    
    client_id: str = aws_get_thing_name()
    job_topic: str = "$aws/things/{0}/jobs/{1}/update".format(client_id, job_id)
    job_update_json = {"status": __aws_job_execution_to_str(job_execution_status), "statusDetails": {__aws_job_execution_status_to_detail_token_str(job_execution_status): status_detail_str}, "clientToken": client_id}
    job_update_json_str: str = ujson.dumps(job_update_json)
    aws_publish(job_topic, job_update_json_str)

def register_operation(operation: str, on_operation_cb: function) -> None:
    if operation in _operation_subscriptions:
        print("Operation {} is already registered!".format(operation))
        return
    _operation_subscriptions[operation] = on_operation_cb