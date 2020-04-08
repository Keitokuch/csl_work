import pickle
import numpy as np
import pandas as pd

from training_config import features, label

EVALUATE_FILE = 'post60.csv'

test_df = pd.read_csv(EVALUATE_FILE)

test_X = test_df[features].values
test_y = test_df[label].values

class FC():

    def __init__(self, weights, bias):
        self.shape = weights.shape
        self.weights = weights
        self.input_dim, self.output_dim = self.shape[0], self.shape[1]
        self.bias = bias

    def forward(self, x):
        y = np.dot(x, self.weights) + self.bias
        return np.maximum(y, 0, y) # ReLU


class Model():

    def __init__(self, weight_file):
        with open(weight_file, 'rb') as f:
            self.weights = pickle.load(f)
        assert len(self.weights) % 2 == 0
        self.layers = []
        for i in range(len(self.weights) // 2):
            self.layers.append(FC(self.weights[i*2], self.weights[i*2+1]))
        print(self.layers)

    def predict(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return 1 if x > 0.5 else 0


model = Model('weights_pickle')
results = np.array(list(map(model.predict, test_X)))
correct = (results == test_y.flatten()).sum()
total = len(test_y)
print(f'{correct} corrects out of {total}, accuracy: {correct / total :2f}')
