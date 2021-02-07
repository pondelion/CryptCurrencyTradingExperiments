import boto3


_aws_session = boto3.session.Session()

SQS = _aws_session.resource('sqs')
