import pickle
import numpy as np
import pandas as pd
import argparse

from training_config import features, label
from predict_ana import predict_ana

pd.options.mode.chained_assignment = None

EVALUATE_FILE = 'post_parsec.csv'

parser = argparse.ArgumentParser()
parser.add_argument('model_tag')
parser.add_argument('evaluate_tag')
parser.add_argument('-p', '--print', action='store_true')
args = parser.parse_args()

weight_file = f'./pickle_{args.model_tag}.weights'
EVALUATE_FILE = f'post_{args.evaluate_tag}.csv'


class FC():

    def __init__(self, weights, bias):
        self.shape = weights.shape
        self.weights = weights
        self.input_dim, self.output_dim = self.shape[0], self.shape[1]
        self.bias = bias

    def forward(self, x):
        y = np.dot(x, self.weights) + self.bias
        print()
        print(x, self.weights, y)
        return np.maximum(y, 0, y) # ReLU

    def __repr__(self):
        return '{} \n {}'.format(self.weights, self.bias)


class Model():

    def __init__(self, weight_file):
        with open(weight_file, 'rb') as f:
            self.weights = pickle.load(f)
        assert len(self.weights) % 2 == 0
        self.layers = []
        for i in range(len(self.weights) // 2):
            self.layers.append(FC(self.weights[i*2], self.weights[i*2+1]))

    def predict(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        exit()
        return 1 if x > 0.5 else 0


test_df = pd.read_csv(EVALUATE_FILE)
test_X = test_df[features].values
test_y = test_df[label].values

model = Model(weight_file)
predictions = np.array(list(map(model.predict, test_X)))
correct = (predictions == test_y.flatten()).sum()
total = len(test_y)
print('Running', weight_file, 'on', EVALUATE_FILE)
print(f'{correct} corrects out of {total}, accuracy: {correct / total :2f}')

test_df['prediction'] = predictions
predict_ana(test_df)

if args.print:
    for layer in model.layers:
        print(layer)
