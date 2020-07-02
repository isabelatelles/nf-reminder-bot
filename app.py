import os
import datetime
import logging
import os
from slack import WebClient
from slack.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
from flask import Flask

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], "/slack/events", app)

# Initialize a Web API client
client = WebClient(token=os.environ['BOT_TOKEN'])

block_message = [
  {
    "type": "section",
    "text": {
      "type": "plain_text",
      "text": "Envie a nota fiscal :rainbow:",
      "emoji": True
    }
  },
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "<https://google.com|Prefeitura de Campinas - emissão>"
    }
  },
  {
    "type": "actions",
    "elements": [
      {
        "type": "button",
        "text": {
          "type": "plain_text",
          "text": "Enviado",
          "emoji": True
        },
        "style": "primary",
        "value": "click_me_123"
      }
    ]
  }
]

user_ids = []
timestamps = []

@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
  emoji = event_data["event"]["reaction"]
  print(emoji)

def schedule_message(message):
  now = datetime.datetime.now()
  for id in user_ids:
    response = client.chat_scheduleMessage(
      channel=id,
      blocks=block_message,
      text=message,
      post_at=(now + datetime.timedelta(minutes=2)).timestamp())

def post_message(message):
  for id in user_ids:
      response = client.chat_postMessage(
        channel=id,
        blocks=block_message,
        text=message)
      timestamps.append(response['ts'])

def send_message(message, schedule=False):
  try:
    if schedule:
      schedule_message(message)
    else:
      post_message(message)
  except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")

if __name__ == "__main__":
  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)
  logger.addHandler(logging.StreamHandler())
  send_message("Envie a nota fiscal!")
  app.run(port=8080)