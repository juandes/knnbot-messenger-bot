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


@app.route("/", methods=['POST', 'GET'])
def webhook():
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
