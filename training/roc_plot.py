import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from training_config import features, label

from sklearn.metrics import roc_curve, auc
from scipy import interp
from sklearn.metrics import roc_auc_score

#  df = pd.read_csv('./test_results.csv')
MODEL_FILE='model_final1.h5'
TEST_FILE='post_testing.csv'

model = tf.keras.models.load_model(MODEL_FILE)

print(model.history.keys())
exit()
test_df = pd.read_csv(TEST_FILE)
test_X = test_df[features]
test_y = test_df[label]

y_pred = model.predict(test_X).ravel()

fpr, tpr, thredsholds = roc_curve(test_y, y_pred)
roc_auc = auc(fpr, tpr)

# total = len(df)
# tp = (df.label.eq(1) & df.prediction.eq(1)).sum()
# fp = (df.label.eq(0) & df.prediction.eq(1)).sum()
# tn = (df.label.eq(0) & df.prediction.eq(0)).sum()
# fn = (df.label.eq(1) & df.prediction.eq(0)).sum()
# print(f'tpr {tp/(tp+fn):.5f}')
# print(f'fpr {fp/(fp+tn):.5f}')
# print(tp/total, fp/total, tn/total, fn/total)

lw = 2
plt.plot(fpr, tpr, color='darkorange',
         lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic example')
plt.legend(loc="lower right")
plt.show()
