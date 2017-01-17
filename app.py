import numpy as np
import os
from knn import get_neighbors, get_majority_vote
from pymessenger.bot import Bot
from collections import defaultdict

import requests
from flask import Flask, request

app = Flask(__name__)

#ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
VERIFY_TOKEN = "bot_verify"
bot = Bot(ACCESS_TOKEN)

k = 3


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hi", 200


training_set = []
train = defaultdict(list)

a = []
TRAINING_STATE = 0
PREDICT_STATE = 1
user_state = {}


def performPrediction(recipient_id, input):
    if len(input) != 2:
        message = "Wrong input on prediction"
        bot.send_text_message(recipient_id, message)
        return

    train_to_fit = np.array(train[recipient_id])
    to_predict = [(int(input[0]), int(input[1]))]
    to_predict = np.array(to_predict)

    neighbors = get_neighbors(
        training_set=train_to_fit, test_instance=to_predict[0], k=k)
    majority_vote = get_majority_vote(neighbors)
    print 'Predicted label=' + str(majority_vote)

    message = "Predicted label {}".format(str(majority_vote))
    bot.send_text_message(recipient_id, message)


def modifyUserState(recipient_id, state):
    user_state[recipient_id] = state


def validateInput(raw_input, recipient_id, state):
    if state == PREDICT_STATE:
        input = raw_input.split(',')
        if len(input) == 3:
            return True

    bot.send_text_message(recipient_id, "Wrong input")
    return False


@app.route("/2", methods=['POST'])
def webhook2():
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


@app.route("/", methods=['POST'])
def webhook():

    output = request.get_json()
    print("POST: {}".format(output))
    # for every event
    for event in output['entry']:
        messaging = event['messaging']
        # for every messaging event
        for x in messaging:
            recipient_id = x['sender']['id']
            # Continue if the recipient_id is empty
            if recipient_id == "":
                continue

            # If the user does not have any state, assign it to the default
            if user_state.get(recipient_id) is None:
                modifyUserState(recipient_id, TRAINING_STATE)

            # Check if it is a message event, by checking if the response
            # contains the key 'message'
            if x.get('message'):
                if x['message'].get('text'):
                    raw_input = x['message'].get('text')
                    input = raw_input.split(',')
                    if user_state.get(recipient_id) == PREDICT_STATE:
                        performPrediction(recipient_id, input)
                        continue

                    if len(input) != 3:
                        message = 'Wrong input'
                        bot.send_text_message(recipient_id, message)
                        continue

                    training_input = (
                        (int(input[0]), int(input[1])), int(input[2]))
                    train[recipient_id].append(training_input)

                    message = 'Input: {} accepted as training. Entry #{}'.format(
                        input, len(train[recipient_id]))

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
                        bot.send_button_message(recipient_id, message, buttons)
                    continue
            # if a postback event
            elif x.get('postback'):
                payload = x['postback'].get('payload')
                if payload == 'YES_USE_KNN':
                    user_state[recipient_id] = PREDICT_STATE
                    bot.send_text_message(
                        recipient_id, "Enter example to predict")
                pass
            else:
                pass
    return "Success"


if __name__ == '__main__':
    app.run(debug=True)
