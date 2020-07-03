import os
import datetime
import hmac, hashlib
import logging
import os
from slack import WebClient
from slack.errors import SlackApiError
from flask import Flask, request, make_response, Response
import json

BOT_TOKEN = os.environ["BOT_TOKEN"]
SIGNING_SECRET = os.environ["SIGNING_SECRET"].encode('utf-8')

# Initialize a Flask app to host the events adapter
app = Flask(__name__)

# Helper for verifying that requests came from Slack
def verify(request, secret):
  body = request.get_data()
  timestamp = request.headers['X-Slack-Request-Timestamp']
  sig_basestring = 'v0:%s:%s' % (timestamp, body.decode('utf-8'))
  computed_sha = hmac.new(secret, sig_basestring.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
  my_sig = 'v0=%s' % (computed_sha,)
  slack_sig = request.headers['X-Slack-Signature']
  if my_sig != slack_sig:
      raise Exception("my_sig %s does not equal slack_sig %s" % (my_sig, slack_sig))

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

user_ids = []
timestamps = []

@app.route("/slack/events", methods=["POST"])
def handle_event():
  # Verify that the request came from Slack
  verify(request, SIGNING_SECRET)
  payload = json.loads(request.form["payload"])
  event_type = payload["type"]
  if event_type == 'block_actions':
    return update_message(request, payload)
  else:
    raise Exception("unable to handle event type: %s" % (event_type,))

def update_message(request, payload):
  timestamp = payload["container"]["message_ts"]
  id = payload["container"]["channel_id"]
  res = client.chat_update(
    channel=id,
    ts=timestamp,
    text="Deu certo",
    blocks=None)
  return

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