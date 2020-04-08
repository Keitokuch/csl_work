import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation
from tensorflow.keras import optimizers
import os.path
import pickle

from training_config import features, label

TEST_SIZE = 50000
MODEL_TAG = 'combined48'
#  MODEL_TAG = 'final'
#  DATA_FILE = './post_combined48.csv'
DATA_FILE = './post_combined71.csv'
#  DATA_FILE = './post_ng20.csv'
#  DATA_FILE = './test_parsec.csv'
#  DATA_FILE = './post_ng_high.csv'
WEIGHT_FILE = 'weights_' + MODEL_TAG + '.h5'
MODEL_FILE = 'model_' + MODEL_TAG + '.h5'
#  WEIGHT_FILE = 'weights14.h5'
#  MODEL_FILE = 'model14.h5'
DO_LOAD         = 1
DO_TRAIN        = 0
DO_SAVE         = 0
EVALUATE        = 1
LOAD_EVALUATE   = 1
EVALUATE_TAG = 'idle46'
EVALUATE_SET = f'./post_{EVALUATE_TAG}.csv'
#  EVALUATE_SET = './post_fibo46.csv'

X_val           = 0

EPOCHS = 3


def random_split(data, proportion=0.1):
    nrow = len(data)
    indices = np.random.permutation(nrow)
    test_size = int(nrow * proportion)
    test_indices = indices[:test_size]
    train_indices = indices[test_size:]
    test_data = data.iloc[test_indices]
    train_data = data.iloc[train_indices]
    return train_data, test_data


def get_model(input_dim):
    model = Sequential()
    model.add(Dense(10, activation='relu', input_dim=input_dim))
    #  model.add(Dense(5, activation='relu'))
    model.add(Dense(1))
    sgd = optimizers.SGD()
    rmsprop = optimizers.RMSprop(learning_rate=0.001, rho=0.9)
    adam = optimizers.Adam()
    model.compile(optimizer=adam, loss='binary_crossentropy', metrics=['accuracy'])
    return model


df = pd.read_csv(DATA_FILE)
head_df = df[:TEST_SIZE]
tail_df = df[-TEST_SIZE:]
head_X, head_y = head_df[features], head_df[label]
tail_X, tail_y = tail_df[features], tail_df[label]

sum_acc = 0
if X_val:
    for time in range(X_val):
        train_df, test_df = random_split(df, 0.1)
        train_X = train_df[features]
        train_y = train_df[label]
        test_X = test_df[features]
        test_y = test_df[label]
        n_features = train_X.shape[1]
        model = get_model(n_features)
        model.fit(train_X, train_y, batch_size=64, validation_split=0.1, epochs=3)
        loss, acc = model.evaluate(test_X, test_y)
        sum_acc += acc
        print(time, loss, acc, sum_acc / (time+1))
    print('avg acc', sum_acc / X_val)
    exit()


train_df, test_df = random_split(df, 0.1)
if LOAD_EVALUATE:
    extra_test_df = pd.read_csv(EVALUATE_SET)

train_X = train_df[features]
train_y = train_df[label]

test_X = test_df[features]
test_y = test_df[label]


n_features = train_X.shape[1]

model = get_model(n_features)

if DO_LOAD:
    try:
        model.load_weights(WEIGHT_FILE)
    except:
        try:
            model = tf.keras.models.load_model(MODEL_FILE)
        except:
            print('load model failed')
            pass


weights = model.get_weights()
#  with open('weights_pickle', 'wb') as f:
    #  pickle.dump(weights, f)

for lay in weights:
    print(len(lay), type(lay[0]))
#  first = weights[0]
#  print(first[0])


#final 10-relu 32-0.1-3
if DO_TRAIN:
    model.fit(train_X, train_y, batch_size=32, validation_split=0.1, epochs=EPOCHS)
if DO_SAVE:
    model.save_weights(WEIGHT_FILE)
    model.save(MODEL_FILE)

if EVALUATE:
    print(model.evaluate(test_X, test_y))
    print(model.evaluate(head_X, head_y))
    print(model.evaluate(tail_X, tail_y))
    if LOAD_EVALUATE:
        test_df = extra_test_df
        test_X, test_y = test_df[features], test_df[label]
        print(model.evaluate(test_df[features], test_df[label]))
        test_df = test_df[features + label]
        test_df.loc[:,'prediction'] = np.where(model.predict(test_X) < 0.5, 0, 1)
        test_df.to_csv(f'predict_{EVALUATE_TAG}.csv', index=False)

        print(EVALUATE_TAG)
        df = test_df
        total = len(df)
        stats = {}
        stats['can migrate'] = df.can_migrate.eq(1).sum()
        stats['false-negative (1,0)'] = (df.can_migrate.eq(1) & df.prediction.eq(0)).sum()
        stats['false-positive (0,1)'] = (df.can_migrate.eq(0) & df.prediction.eq(1)).sum()
        stats['true-positive (1,1)'] = (df.can_migrate.eq(1) & df.prediction.eq(1)).sum()
        stats['true-negative (0,0)'] = (df.can_migrate.eq(0) & df.prediction.eq(0)).sum()
        stats['total'] = len(df)
        for item in stats:
            print(item, stats[item], '{:.4f}'.format(stats[item] / total))
