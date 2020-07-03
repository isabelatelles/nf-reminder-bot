import os
import datetime
import os
from slack import WebClient
from slack.errors import SlackApiError
from flask import Flask, request, make_response, Response
import json

BOT_TOKEN = os.environ["BOT_TOKEN"]

# Initialize a Web API client
client = WebClient(token=BOT_TOKEN)

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
        "value": "done_button",
        "action_id": "button"
      }
    ]
  }
]

timestamps = {}

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
    timestamps[id] = response['ts']

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
  start = datetime.datetime.now()
  delta = start + datetime.timedelta(minutes=1)
  with open("user_ids.txt") as f:
    user_ids = f.read().split(',')
  send_message("Envie a nota fiscal!")
  while user_ids:
    with open("user_ids.txt") as f:
      user_ids = f.read().split(',')
    now = datetime.datetime.now()
    if now >= delta:
      send_message("Envie a nota fiscal!")
      start = datetime.datetime.now()
      delta = start + datetime.timedelta(minutes=1)