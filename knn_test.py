import numpy as np
import os
from knn import get_neighbors, get_majority_vote

k = 3


def main():
    print 'hey'
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
            # We are using a array because the original program uses an array
            # of multiple test examples
            to_predict = np.array(to_predict)

            neighbors = get_neighbors(
                training_set=train_to_fit, test_instance=to_predict[0], k=k)
                majority_vote = get_majority_vote(neighbors)
                predictions.append(majority_vote)
                print 'Predicted label=' + str(majority_vote)


if __name__ == '__main__':
    main()
