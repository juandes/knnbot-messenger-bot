import os
from pymessenger.bot import Bot
from collections import defaultdict

import requests
from flask import Flask, request

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = "bot_verify"
bot = Bot(ACCESS_TOKEN)


a = defaultdict(list)


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    # the facebook ID of the person sending you the message
                    sender_id = messaging_event["sender"]["id"]
                    # the recipient's ID, which should be your page's facebook
                    # ID
                    recipient_id = messaging_event["recipient"]["id"]
                    message_text = messaging_event["message"][
                        "text"]  # the message's text
                    a[recipient_id].append(1)
                    send_message(sender_id, len(a[recipient_id]))

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                # user clicked/tapped "postback" button in earlier message
                if messaging_event.get("postback"):
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)


@app.route("/2", methods=['POST', 'GET'])
def webhook2():
    if request.method == 'POST':
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for x in messaging:
                if x.get('message'):
                    recipient_id = x['sender']['id']
                    a[recipient_id].append(1)
                    bot.send_text_message(recipient_id, len(a[recipient_id]))
    return 'Success'


if __name__ == '__main__':
    app.run(debug=True)
