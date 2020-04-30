import sys
from training_config import *
from keras_conf import *
from prep import preprocess
from keras_lb import keras_train
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--tags', nargs='+', help='tags list', required=True)
parser.add_argument('-o', '--object', help='tag for model object')

args = parser.parse_args()

tags = args.tags
if len(tags) == 1:
    model_tag = args.object or tags[0]
else:
    model_tag = args.object

preprocess(tags, out_tag=model_tag)
keras_train(model_tag=model_tag)
