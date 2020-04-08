import numpy as np
import pandas as pd
import tensorflow as tf
import os.path

MODEL_TAG = 'combined46'
WEIGHT_FILE = 'weights_' + MODEL_TAG + '.h5'
MODEL_FILE = 'model_' + MODEL_TAG + '.h5'
EVALUATE_TAG = 'idle46'
EVALUATE_FILE = f'./post_{EVALUATE_TAG}.csv'

from training_config import features, label

test_df = pd.read_csv(EVALUATE_FILE)

test_X = test_df[features]
test_y = test_df[label]


model = tf.keras.models.load_model(MODEL_FILE)
test_df['prediction'] = np.where(model.predict(test_X) < 0.5, 0, 1)
test_df.to_csv(f'predict_{EVALUATE_TAG}.csv', index=False)
model.evaluate(test_X, test_y)
