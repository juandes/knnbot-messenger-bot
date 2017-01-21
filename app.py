import numpy as np
import os
import messages
import bot_functions
from user import user
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
train = defaultdict(list)

a = []
TRAINING_STATE = 0
PREDICT_STATE = 1

user = defaultdict(dict)


@app.route('/', methods=['GET'])
def verify():
    # Once the endpoint is registered, it must answer back the 'hub.challenge' value
    # which is received in the GET. This is needed to register the bot in
    # Facebook.
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hi", 200


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
    # For every event
    for event in output['entry']:
        messaging = event['messaging']
        # For every messaging event
        for x in messaging:
            recipient_id = x['sender']['id']
            # Continue if the recipient_id is empty
            if recipient_id == "":
                continue

            # If the user does not have any state, assign it to the default
            if user[recipient_id].get('state') is None:
                modifyUserState(recipient_id, TRAINING_STATE)

            # Check if it is a message event, by checking if the response
            # contains the key 'message'
            if x.get('message'):
                if x['message'].get('text'):
                    raw_input = x['message'].get('text')
                    input = raw_input.split(',')

                    if user[recipient_id].get('state') == PREDICT_STATE:
                        performPrediction(recipient_id, raw_input)
                        continue

                    if len(input) != 3:
                        bot.send_text_message(
                            recipient_id, messages.wrong_input)
                        continue

                    training_input = (
                        (int(input[0]), int(input[1])), int(input[2]))
                    train[recipient_id].append(training_input)

                    message = messages.training_input_accepted.format(
                        input, len(train[recipient_id]))

                    bot.send_text_message(recipient_id, message)

                    if len(train[recipient_id]) >= k + 5:
                        buttons = [bot_functions.create_button('postback', 'Yes', 'YES_USE_KNN'),
                                   bot_functions.create_button('postback', 'No', 'NO_USE_KNN')]
                        bot.send_button_message(
                            recipient_id, messages.enough_training, buttons)
                    continue
            # If the event is postback
            elif x.get('postback'):
                payload = x['postback'].get('payload')
                if payload == 'YES_USE_KNN':
                    modifyUserState(recipient_id, PREDICT_STATE)
                    bot.send_text_message(
                        recipient_id, "Enter example to predict")
                # pass
            else:
                pass
    return "Success"


def performPrediction(recipient_id, raw_input):
    input = raw_input.split(',')
    if len(input) != 2:
        message = "Wrong input on prediction"
        bot.send_text_message(recipient_id, message)
        return

    train_to_fit = np.array(train[recipient_id])
    to_predict = [int(input[0]), int(input[1])]

    neighbors = get_neighbors(
        training_set=train_to_fit, test_instance=to_predict, k=k)
    majority_vote = get_majority_vote(neighbors)
    print 'Predicted label=' + str(majority_vote)

    message = "Predicted label {}".format(str(majority_vote))
    bot.send_text_message(recipient_id, message)


def modifyUserState(recipient_id, state):
    user[recipient_id]['state'] = state


def validateInput(recipient_id, raw_input, state):
    if state == PREDICT_STATE:
        input = raw_input.split(',')
        if len(input) == 3:
            return True

    bot.send_text_message(recipient_id, messages.wrong_input)
    return False


def addToTraining(recipient_id, raw_input):
    return

if __name__ == '__main__':
    app.run(debug=True)
