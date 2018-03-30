# i am using this to get a better feeling for max margin methods
# specifically in reference to Apprenticeship Learning via Inverse Reinforcement Learning
# copied from http://scikit-learn.org/stable/auto_examples/svm/plot_separating_hyperplane.html
''''

This is the equivalent of picking random policies to get closer to the ideal policy
As a better policy is found, the dividing boundary can be updated
Giving a better estimation of how to get to the goal

'''



import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.datasets import make_blobs
import pdb

# we create 40 separable points
X, _ = make_blobs(n_samples=40, centers=2, random_state=6)
np.random.seed(6)

# idx = np.random.randint(len(y))
# y = [1  if i == idx else 0 for i,Y in enumerate(y)]
# add a max value and make that the 'expert' policy
X = np.append(X, np.max(X,0).reshape(1,-1), axis=0)
y = np.zeros((len(X), 1))
y[-1] = 1


# fit the model, don't regularize for illustration purposes
for i in range(2,len(X)):
	# pdb.set_trace()
	y_iter = np.append(y[:i], y[-1])
	X_iter = np.append(X[:i], X[-1].reshape(1,-1), axis=0)
	clf = svm.SVC(kernel='linear', C=1000)
	clf.fit(X_iter, y_iter)
	plt.cla()
	plt.scatter(X_iter[:, 0], X_iter[:, 1], c=y_iter, s=30, cmap=plt.cm.Paired, marker="x")

	# plot the decision function
	ax = plt.gca()
	xlim = ax.get_xlim()
	ylim = ax.get_ylim()

	# create grid to evaluate model
	xx = np.linspace(xlim[0], xlim[1], 30)
	yy = np.linspace(ylim[0], ylim[1], 30)
	YY, XX = np.meshgrid(yy, xx)
	xy = np.vstack([XX.ravel(), YY.ravel()]).T
	Z = clf.decision_function(xy).reshape(XX.shape)

	# plot decision boundary and margins
	ax.contour(XX, YY, Z, colors='k', levels=[-1, 0, 1], alpha=0.5,
	           linestyles=['--', '-', '--'])
	# plot support vectors
	# pdb.set_trace()
	ax.scatter(clf.support_vectors_[:, 0], clf.support_vectors_[:, 1], s=100, linewidth=1, facecolors='none')
	plt.ion()
	plt.show()
	plt.pause(0.1)
	# pdb.set_trace()
	# plt.show()