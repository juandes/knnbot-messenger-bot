import numpy as np
import os
from knn import get_neighbors, get_majority_vote
from pymessenger.bot import Bot
from collections import defaultdict

import requests
from flask import Flask, request

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = "bot_verify"
bot = Bot(ACCESS_TOKEN)

k = 3


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


def main():
    predictions = []
    train = []

    while True:
        name = raw_input("input: ")
        input = name.split(',')
        t = ((int(input[0]), int(input[1])), int(input[2]))
        train.append(t)

        if len(train) > k + 0:
            train_to_fit = np.array(train)

            name = raw_input("Input to predict: ")   # Python 2.x
            input = name.split(',')
            to_predict = [(int(input[0]), int(input[1]))]
            to_predict = np.array(to_predict)

            # for each testing instance
            for x in range(len(to_predict)):
                neighbors = get_neighbors(
                    training_set=train_to_fit, test_instance=to_predict[x], k=k)
                majority_vote = get_majority_vote(neighbors)
                predictions.append(majority_vote)
                print 'Predicted label=' + str(majority_vote) + ', Actual label=' + str(to_predict[x])


@app.route("/")
def landing():
    return 'Hi.'


training_set = []
train = defaultdict(list)

a = []


@app.route("/", methods=['POST'])
def webhook():
    if request.method == 'POST':
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for x in messaging:
                if x.get('message'):
                    recipient_id = x['sender']['id']
                    a.append(1)
                    bot.send_text_message(recipient_id, len(a))
    return 'Success'


@app.route("/2", methods=['POST', 'GET'])
def webhook2():
    if request.method == 'GET':
        print('GET received')
        print(request.args)

    if request.method == 'POST':
        output = request.get_json()
        print("POST received: {}".format(output))
        # for every event
        for event in output['entry']:
            messaging = event['messaging']
            # for every messaging event
            for x in messaging:
                # Check if it is a message event, by checking if the response contains
                # the key 'message'
                if x.get('message'):
                    recipient_id = x['sender']['id']
                    if x['message'].get('text'):
                        raw_input = x['message'].get('text')
                        input = raw_input.split(',')
                        if len(input) != 3:
                            message = 'Wrong input'
                            bot.send_text_message(recipient_id, message)
                            continue
                        print(train)
                        training_input = (
                            (int(input[0]), int(input[1])), int(input[2]))
                        train[recipient_id].append(training_input)
                        # training_set.append(training_input)
                        print(len(train[recipient_id]))
                        message = 'Input: {} accepted as training. Entry #{}'.format(
                            input, len(train[recipient_id]))
                        print(message)
                        bot.send_text_message(recipient_id, message)
                        if len(train[recipient_id]) >= k + 5:
                            message = 'You have enough training data'  \
                                'Would you like to use the KNN model?'
                            buttons = [{'type': 'postback',
                                        'title': 'Yes',
                                        'payload': 'YES_USE_KNN'},
                                       {'type': 'postback',
                                        'title': 'No',
                                        'payload': 'NO_USE_KNN'}]
                            bot.send_button_message(
                                recipient_id, message, buttons)
                        continue
                # if a postback event
                elif x.get('postback'):
                    recipient_id = x['sender']['id']
                    payload = x['postback'].get('payload')
                    bot.send_text_message(recipient_id, payload)
                    pass
                else:
                    pass
        return "Success"


if __name__ == '__main__':
    app.run(debug=True)
