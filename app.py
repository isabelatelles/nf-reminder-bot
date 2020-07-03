import os
import datetime
import hmac, hashlib
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
with open("user_ids.txt") as f:
  user_ids = f.read().split(',')

@app.route("/slack/events", methods=["POST"])
def handle_event():
  # Verify that the request came from Slack
  verify(request, SIGNING_SECRET)
  payload = json.loads(request.form["payload"])
  event_type = payload["type"]
  print(event_type)
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
  user_ids.remove(payload["user"]["id"])
  with open("user_ids.txt", "w") as f:
    f.write(','.join(user_ids))
  return ""

if __name__ == "__main__":
  app.run(port=8080)