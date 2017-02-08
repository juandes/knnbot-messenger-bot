import numpy as np
import os
import messages
import bot_functions
import matplotlib.pyplot as plt
import requests
import subprocess

from user import user
from knn import get_neighbors, get_majority_vote
from pymessenger.bot import Bot
from collections import defaultdict
from flask import Flask, request

app = Flask(__name__)

# Bot related
ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
bot = Bot(ACCESS_TOKEN)

# k of KNN
k = 3

# User dict and states
users = defaultdict(user)
TRAINING_STATE = 0
PREDICT_STATE = 1


@app.route('/', methods=['GET'])
def verify():
    # Once the endpoint is registered, it must answer back the 'hub.challenge' value
    # which is received in the GET. This is needed to register the bot on
    # Facebook.
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hi", 200


@app.route("/", methods=['POST'])
def webhook():
    output = request.get_json()
    print("POST: {}".format(output))

    # For every event
    for event in output['entry']:
        messaging = event['messaging']
        # For every content in the event
        for x in messaging:
            recipient_id = x['sender']['id']
            # Continue if the recipient_id is empty
            if recipient_id == "":
                continue

            # If the user does not exist, create a new one with
            # the default state, TRAINING_STATE
            if users.get(recipient_id) is None:
                users[recipient_id] = user(recipient_id, TRAINING_STATE)

            # Check the content is a message by checking if the response
            # contains the key 'message'
            if x.get('message'):
                if x['message'].get('text'):
                    raw_input = x['message'].get('text')

                    if raw_input == 'status':
                        show_status(recipient_id)
                    elif raw_input == 'train' or raw_input == 'training':
                        modify_user_state(recipient_id, TRAINING_STATE)
                        bot.send_text_message(recipient_id, "TRAINING state")
                    elif raw_input == 'predict':
                        if users[recipient_id].training_set_length() >= k:
                            modify_user_state(recipient_id, PREDICT_STATE)
                            bot.send_text_message(
                                recipient_id, "PREDICT state")
                        else:
                            bot.send_text_message(
                                recipient_id, "Not enough training examples")
                    elif users[recipient_id].state == TRAINING_STATE:
                        add_to_training(recipient_id, raw_input)
                        check_if_enough_training(recipient_id)
                    elif users[recipient_id].state == PREDICT_STATE:
                        perform_prediction(recipient_id, raw_input)

            # If the content is postback
            elif x.get('postback'):
                payload = x['postback'].get('payload')
                if payload == 'YES_USE_KNN':
                    modify_user_state(recipient_id, PREDICT_STATE)
                    bot.send_text_message(
                        recipient_id, "Enter example to predict")
                elif payload == 'NO_USE_KNN':
                    bot.send_text_message(
                        recipient_id, "Keep on training!")
                elif payload == 'TRAINING_CLASSES':
                    bot.send_text_message(recipient_id, users[
                        recipient_id].get_training_classes())
                elif payload == 'SHOW_KNN':
                    users[recipient_id].generate_knn_plot()
                    # The send_image function of the library was giving some
                    # problems, so instead, I'm using a curl command
                    # to upload the image.
                    subprocess.call(["curl",
                                     "-F",
                                     "recipient={\"id\":\"" +
                                     str(recipient_id) + "\"}",
                                     "-F", "message={\"attachment\":{\"type\":\"image\", \"payload\":{}}}",
                                     "-F", "filedata=@{}.jpg".format(
                                         recipient_id),
                                     "https://graph.facebook.com/v2.6/me/messages?access_token={}".format(ACCESS_TOKEN)], shell=False)
            else:
                pass
    return "Success"


def perform_prediction(recipient_id, raw_input):
    input = raw_input.split(',')
    # Check of the input if of shape (x,y)
    if len(input) != 2:
        message = "Wrong input on prediction"
        bot.send_text_message(recipient_id, message)
        return

    # Get the user's training set
    train_to_fit = np.array(users[recipient_id].training_set)
    # Convert the input to predict into the right format
    to_predict = [int(input[0]), int(input[1])]

    neighbors = get_neighbors(
        training_set=train_to_fit, test_instance=to_predict, k=k)
    majority_vote = get_majority_vote(neighbors)
    print 'Predicted label=' + str(majority_vote)

    message = "Predicted label {}".format(str(majority_vote))
    bot.send_text_message(recipient_id, message)


def modify_user_state(recipient_id, state):
    users[recipient_id].state = state


# Add a new training input to the training list
def add_to_training(recipient_id, raw_input):
    input = raw_input.split(',')
    if len(input) != 3:
        bot.send_text_message(
            recipient_id, messages.wrong_input)
        return

    # Each training example is of the shape((x,y), label)
    training_input = ((int(input[0]), int(input[1])), int(input[2]))
    users[recipient_id].add_training_example(training_input)

    # Send a message to the user stating that the input was accepted
    message = messages.training_input_accepted.format(
        input, users[recipient_id].training_set_length())
    bot.send_text_message(recipient_id, message)


# If the users has enough training examples, offer them to
# test the model
def check_if_enough_training(recipient_id):
    if users[recipient_id].training_set_length() >= k:
        buttons = [bot_functions.create_button('postback', 'Yes', 'YES_USE_KNN'),
                   bot_functions.create_button('postback', 'No', 'NO_USE_KNN')]
        bot.send_button_message(
            recipient_id, messages.enough_training, buttons)


def show_status(recipient_id):
    message = "Number of training examples: {} \n"\
        "K: {} \n"\
        "State: {} \n"\
        "For more details, click any of the buttons below.".format(users[recipient_id].training_set_length(),
                                                                   k, users[recipient_id].get_state())

    buttons = [bot_functions.create_button(
        'postback', 'Training Classes', 'TRAINING_CLASSES'),
        bot_functions.create_button(
        'postback', 'Show KNN', 'SHOW_KNN')]
    bot.send_button_message(recipient_id, message, buttons)


if __name__ == '__main__':
    app.run(debug=True)
