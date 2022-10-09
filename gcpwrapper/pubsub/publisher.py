# Built-in
import json
import logging
from typing import Optional

# Requirements
from google import api_core
from google.cloud import pubsub_v1


class Publisher:
    def __init__(self,
                 project_id: str,
                 attach_logger: Optional[logging.Logger]=None
                 ):
        self._project_id = project_id
        self._publisher = pubsub_v1.PublisherClient()
        self._logger = attach_logger

    def publish(self, topic_id: str, data: dict) -> str:
        topic_path = self._publisher.topic_path(self._project_id,
                                                topic_id
                                                )
        future = self.__publisher.publish(topic=topic_path,
                                          data=json.dumps(data).encode("utf-8"),
                                          retry=self._custom_retry
                                          )
        if self._logger:
            self._logger.debug(f'Published message to topic {topic_id}')
        return future.result()
    
    @staticmethod
    def _custom_retry() -> api_core.retry.Retry:
        return api_core.retry.Retry(initial=0.1,
                                    maximum=60.0,
                                    multiplier=1.3,
                                    deadline=60.0,
                                    predicate=api_core.retry.if_exception_type(
                                        api_core.exceptions.Aborted,
                                        api_core.exceptions.DeadlineExceeded,
                                        api_core.exceptions.InternalServerError,
                                        api_core.exceptions.ResourceExhausted,
                                        api_core.exceptions.ServiceUnavailable,
                                        api_core.exceptions.Unknown,
                                        api_core.exceptions.Cancelled
                                        )
                                    )
