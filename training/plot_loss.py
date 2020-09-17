import matplotlib
import matplotlib.pyplot as plt
import pickle


font = { 'size'   : 13}
matplotlib.rc('font', **font)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


batches_file = 'batches_plot'
loss_file = 'loss_plot'
with open(batches_file, 'rb') as f:
    batches = pickle.load(f)

with open(loss_file, 'rb') as f:
    losses = pickle.load(f)

plt.plot(batches, losses)
#  plt.title("Training history of loss vs. batches")
plt.xlabel('Training batches')
plt.ylabel('Loss')
plt.show()
