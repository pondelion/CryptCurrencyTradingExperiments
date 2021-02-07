from enum import Enum
from typing import Dict, Union
from dataclasses import dataclass
import json

from ..aws_resource import SQS


class SQSQueueName(Enum):
    DEFAULT = 'finapp'


class Target(Enum):
    SLACK = 'slack'
    TWITTER = 'twitter'


@dataclass
class SlackMessage:
    channel: str
    message: str
    media_url: str = None
    target: Target = Target.SLACK

    def to_json(self):
        data = {
            'target': self.target.value,
            'channel': self.channel,
            'message': self.message,
        }
        if self.media_url is not None:
            data['media_url'] = self.media_url
        return data


@dataclass
class TwitterMessage:
    message: str
    media_url: str = None
    target: Target = Target.TWITTER

    def to_json(self):
        data = {
            'target': self.target.value,
            'message': self.message,
        }
        if self.media_url is not None:
            data['media_url'] = self.media_url
        return data


class SQSPolling:

    def __init__(
        self,
        boto_sqs_clint = SQS,
    ):
        self._sqs_clint = boto_sqs_clint

    def push_message(
        self,
        message: Union[SlackMessage, TwitterMessage],
        queue_name: SQSQueueName = SQSQueueName.DEFAULT,
    ):
        queue = self._sqs_clint.get_queue_by_name(QueueName=queue_name.value)
        msg_json = message.to_json()
        res = queue.send_message(
            MessageBody=json.dumps(msg_json),
        )
        return res
