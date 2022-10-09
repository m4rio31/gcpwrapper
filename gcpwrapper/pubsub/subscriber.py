# Built-in
import logging
from typing import Callable, Optional

# Requirements
from google.cloud import pubsub_v1


class QueueSubscriber:
    def __init__(self,
                 project_id: str,
                 sub_id: str,
                 callback:  Callable[[pubsub_v1.subscriber.message.Message],
                                     None],
                 max_messages: int=0,
                 attach_logger: Optional[logging.Logger]=None):
        self._callback = callback
        self._max_messages = max_messages
        self._subscription = f'projects/{project_id}/subscriptions/{sub_id}'
        self._sub_id = sub_id
        self._logger = attach_logger
    
    def listen(self):
        params = {
            'subscription': self._subscription,
            'callback': self._callback
        }
        if self._max_messages:
            flow_control = pubsub_v1.types.FlowControl(
                max_messages=self._max_messages
                )
            params['flow_control']: flow_control
        with pubsub_v1.SubscriberClient() as subscriber:
            future = subscriber.subscribe(**params)
            if self._logger:
                self._logger.debug(f'Listening on subscription {self._sub_id}')
            future.result()