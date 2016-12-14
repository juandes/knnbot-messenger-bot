import numpy as np
import os
from knn import get_neighbors, get_majority_vote
from pymessenger.bot import Bot

import requests
from flask import Flask, request

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = "bot_verify"
bot = Bot(ACCESS_TOKEN)

k = 3


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


@app.route("/", methods=['POST'])
def webhook():
    predictions = []
    train = []

    if request.method == 'POST':
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for x in messaging:
                if x.get('message'):
                    recipient_id = x['sender']['id']
                    if x['message'].get('text'):
                        input = x['message'].get('text')
                        print('input: {}'.format(input))
                        t = ((int(input[0]), int(input[1])), int(input[2]))

                        train.append(t)

                        if len(train) > k + 0:
                            train_to_fit = np.array(train)

                            name = raw_input(
                                "Input to predict: ")   # Python 2.x
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
                        else:
                            bot.send_text_message(
                                recipient_id, "input accepted")
                        #message = x['message']['text']
                        #bot.send_text_message(recipient_id, message)
                else:
                    pass
        return "Success"


"""def webhook():
    if request.method == 'POST':
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for x in messaging:
                if x.get('message'):
                    recipient_id = x['sender']['id']
                    if x['message'].get('text'):
                        message = x['message']['text']
                        bot.send_text_message(recipient_id, message)
                    if x['message'].get('attachment'):
                        bot.send_attachment_url(recipient_id, x['message']['attachment']['type'],
                                                x['message']['attachment']['payload']['url'])
                else:
                    pass
        return "Success"
"""

if __name__ == '__main__':
    app.run(debug=True)
