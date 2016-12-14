import numpy as np
from knn import get_neighbors, get_majority_vote

import requests
from flask import Flask, request

app = Flask(__name__)


def main():
    k = 1
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


@app.route('/')
def landing():
    return '352546976'

if __name__ == '__main__':
    app.run(debug=True)
