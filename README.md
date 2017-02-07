# Knnbot: a KNN Messenger Bot

Knnbot is a Facebook Messenger bot written in Python, capable of training a machine learning algorithm known as [K-Nearest Neighbor](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm) using manually inputted data from a user. This project is more on the experimental side, a simple proof of concept where I wanted to show a use case of how a machine learning algorithm could be applied to a chatbot.

## Dependencies
- Flask==0.11.1
- requests==2.10.0
- numpy==1.11.1
- pymessenger==0.0.7.0
- pillow==3.1.1
- matplotlib==1.5.3

With `pip` run `pip install -r requirements.txt`

## Regarding the algorithm
For simplicity purposes the bot just accepts feature vectors of **two** dimensions. This could be easily changed by just modifying the input validation in the function `add_to_training`

The algorithm itself has no limitations regarding this.


## Features
The bot accepts the command `status` which will print the number of training examples the user has inputted, the K, and the state in which the bot is currently at, which is either **training** if the user is training the system, or **predict** is the user has enough training examples.

Also, there will be two buttons: training classes, and show knn. The first one will show all the different classes seen during training and the number of cases associated with that label. The second button will display a 2D scatterplot of the training examples which each data point colored depending on its class.


## Instructions
Coming soon
