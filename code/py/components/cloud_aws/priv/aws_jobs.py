from ..aws_iot_client import *
from ..aws_job_execution_status import *

class AWSJobsClient:
    aws_client: AWSIoTClient = None

    # a dictionary of operation subscriptions: <"operation", on_operation_cb>,
    # where on_operation_cb has the following signature: on_operation_cb(job_id: str, job_document: dict) - > (AWS_JOB_EXECUTION_*: int, status_str: str)
    operation_subscriptions: dict = dict()

    # status string and status detail string dictionary: <aws_job_execution_status: int, ("statusDetail", "STATUS")
    job_status_defs: dict = {
        AWS_JOB_EXECUTION_IN_PROGRESS: ("inProgressDetail", "IN_PROGRESS"),
        AWS_JOB_EXECUTION_FAILED: ("failDetail", "FAILED"),
        AWS_JOB_EXECUTION_SUCCEEDED: ("successDetail", "SUCCEEDED"),
        AWS_JOB_EXECUTION_REJECTED: ("rejectedDetail", "REJECTED")
    }

    def __get_jobs_prefix_str(self) -> str:
        return "$aws/things/{}/jobs".format(self.aws_client.client_id)

    def __aws_job_execution_status_to_detail_token_str(self, aws_job_execution_status: int) -> str:
        if aws_job_execution_status in self.job_status_defs:
            return self.job_status_defs[aws_job_execution_status][0]
        return "statusDetail"

    def __aws_job_execution_to_str(self, aws_job_execution_status: int) -> str:
        if aws_job_execution_status in self.job_status_defs:
            return self.job_status_defs[aws_job_execution_status][1]
        return "UNKNOWN"

    def __on_jobs_notify(self, topic_name: str, payload: str) -> None:
        del topic_name
        print("on_jobs_notify: {}".format(payload))
        self.jobs_get_next()

    def __on_jobs_get_next_accepted(self, topic_name: str, payload: str) -> None:
        import ujson
        del topic_name

        # convert payload string to a JSON object
        payload_json: dict = ujson.loads(payload)

        # try to get the execution. If it fails, return (we can't update the job without the job id)
        try:
            # Get the "execution" object. If it doesn"t exist, then there is no job to process
            execution: dict = payload_json["execution"]
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
        except Exception:
            self.publish_update(job_id, AWS_JOB_EXECUTION_REJECTED, "Failed to parse expected JSON object: {}".format(str(error)))
            return

        # get callback for operation
        try:
            operation_cb = self.operation_subscriptions[operation]
        except Exception:
            self.publish_update(job_id, AWS_JOB_EXECUTION_REJECTED, "Operation {} not registered".format(operation))
            return

        # returned tuple: (AWS_JOB_EXECUTION_*: int, status_str: str)
        result_tuple = operation_cb(job_id, job_document)
        assert result_tuple is not None

        self.publish_update(job_id, result_tuple[0], result_tuple[1])

    def __on_jobs_get_next_rejected(self, topic_name: str, payload: str) -> None:
        del topic_name
        print("on_jobs_next_get_rejected: {}".format(payload))

    def __subscribe_to_jobs_topics(self) -> None:
        self.aws_client.subscribe("{}/notify".format(self.__get_jobs_prefix_str()), self.__on_jobs_notify)
        self.aws_client.subscribe("{}/$next/get/accepted".format(self.__get_jobs_prefix_str()), self.__on_jobs_get_next_accepted)
        self.aws_client.subscribe("{}/$next/get/rejected".format(self.__get_jobs_prefix_str()), self.__on_jobs_get_next_rejected)

    def __init__(self, aws_client: AWSIoTClient) -> None:
        assert aws_client is not None

        self.aws_client = aws_client
        self.__subscribe_to_jobs_topics()

        # check for any pending AWS Jobs
        self.jobs_get_next()

    def jobs_get_next(self) -> None:
        self.aws_client.publish("{}/$next/get".format(self.__get_jobs_prefix_str()), "{}")

    def publish_update(self, job_id: str, job_execution_status: int, status_detail_str: str) -> None:
        assert job_id is not None

        import ujson
        job_topic: str = "$aws/things/{0}/jobs/{1}/update".format(self.aws_client.client_id, job_id)
        job_update_json = {"status": self.__aws_job_execution_to_str(job_execution_status), "statusDetails": {self.__aws_job_execution_status_to_detail_token_str(job_execution_status): status_detail_str}, "clientToken": self.aws_client.client_id}
        job_update_json_str: str = ujson.dumps(job_update_json)
        self.aws_client.publish(job_topic, job_update_json_str)

    def register_operation(self, operation: str, on_operation_cb: function) -> None:
        assert operation is not None
        assert on_operation_cb is not None

        if operation in self.operation_subscriptions:
            print("Operation {} is already registered!".format(operation))
            return
        self.operation_subscriptions[operation] = on_operation_cb