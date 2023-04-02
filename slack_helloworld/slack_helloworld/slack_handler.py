import os
import logging
import logging.config

import boto3
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)


ssm = boto3.client('ssm', region_name=os.environ["AWS_REGION"])
bottokenresponse = ssm.get_parameter(
    Name='/prod/chatai/slack.bot.token',
    WithDecryption=True
)
bot_token = bottokenresponse["Parameter"]["Value"]

signingsecretresponse = ssm.get_parameter(
    Name='/prod/chatai/slack.signing.secret',
    WithDecryption=True
)
signing_secret = signingsecretresponse["Parameter"]["Value"]


# process_before_response must be True when running on FaaS
app = App(process_before_response=True,
          token=bot_token,
          logger=logger,
          signing_secret=signing_secret)

@app.command("/hello")
def respond_to_slack_within_3_seconds(ack):
    logger.info("inside hello command")
    ack("Hi!")

def handler(event, context):
    logger.info("handling inbound event: %s", event)
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)