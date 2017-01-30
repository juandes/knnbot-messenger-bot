import matplotlib.pyplot as plt
from PIL import Image


class user(object):

    def __init__(self, recipient_id, state):
        self.recipient_id = recipient_id
        self.state = state
        self.training_set = []
        self.training_classes_count = {}

    def training_set_length(self):
        return len(self.training_set)

    def get_state(self):
        if self.state == 0:
            return "TRAINING"
        else:
            return "PREDICT"

    def add_training_example(self, training_example):
        self.training_set.append(training_example)
        self.add_training_class(training_example[1])

    def add_training_class(self, training_class):
        if self.training_classes_count.get(training_class):
            self.training_classes_count[training_class] += 1
        else:
            self.training_classes_count[training_class] = 1

    def get_training_classes(self):
        message = ""
        if len(self.training_classes_count) == 0:
            return "Empty training set"

        for key, value in self.training_classes_count.iteritems():
            message += "Class: {}. Number of examples: {}\n".format(key, value)
        return message

    def generate_knn_plot(self):
        x = [int(i[0][0]) for i in self.training_set]
        y = [int(i[0][1]) for i in self.training_set]
        label = [int(i[1]) for i in self.training_set]

        plt.scatter(x, y, c=label)
        plt.savefig(self.recipient_id + '.png', format='png')
        # Convert the image to JPEG, because of the problem trying to
        # send an PNG image to the bot
        Image.open(self.recipient_id +
                   '.png').save(self.recipient_id + '.jpg', 'JPEG')
