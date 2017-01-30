from distance import distance
from operator import itemgetter
from collections import Counter


def get_neighbors(training_set, test_instance, k):
    print('test instance {}'.format(test_instance))
    distances = [_get_tuple_distance(
        training_instance, test_instance) for training_instance in training_set]
    # index 1 is the calculated distance between training_instance and
    # test_instance
    sorted_distances = sorted(distances, key=itemgetter(1))
    # extract only training instances
    sorted_training_instances = [tuple[0] for tuple in sorted_distances]
    # select first k elements
    return sorted_training_instances[:k]


def _get_tuple_distance(training_instance, test_instance):
    # training_instance[0] are the predictors
    return (training_instance, distance(test_instance, training_instance[0]))


# Given an array of the nearest neighbors, get the most common label
def get_majority_vote(neighbors):
    # Index 1 represents the label
    classes = [neighbor[1] for neighbor in neighbors]
    count = Counter(classes)
    return count.most_common()[0][0]


def predict(train, data, k):
    distances = [_get_tuple_distance(
        train, data) for training_instance in train]
    # index 1 is the calculated distance between training_instance and
    # test_instance
    sorted_distances = sorted(distances, key=itemgetter(1))
    # extract only training instances
    sorted_training_instances = [tuple[0] for tuple in sorted_distances]
    # select first k elements
    return sorted_training_instances[:k]
