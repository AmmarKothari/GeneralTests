import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pdb

from sklearn import decomposition
from sklearn import datasets


def IrisExample():
	np.random.seed(5)

	centers = [[1, 1], [-1, -1], [1, -1]]
	iris = datasets.load_iris()
	X = iris.data
	y = iris.target

	fig = plt.figure(1, figsize=(4, 3))
	plt.clf()
	ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)

	plt.cla()
	pca = decomposition.PCA(n_components=3)
	pca.fit(X)
	X = pca.transform(X)

	for name, label in [('Setosa', 0), ('Versicolour', 1), ('Virginica', 2)]:
		ax.text3D(X[y == label, 0].mean(),
				  X[y == label, 1].mean() + 1.5,
				  X[y == label, 2].mean(), name,
				  horizontalalignment='center',
				  bbox=dict(alpha=.5, edgecolor='w', facecolor='w'))
	# Reorder the labels to have colors matching the cluster results
	y = np.choose(y, [1, 2, 0]).astype(np.float)
	ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=y, cmap=plt.cm.spectral,
			   edgecolor='k')

	ax.w_xaxis.set_ticklabels([])
	ax.w_yaxis.set_ticklabels([])
	ax.w_zaxis.set_ticklabels([])
	pdb.set_trace()
	plt.show()

def draw_vector(v0, v1, ax=None):
	ax = ax or plt.gca()
	arrowprops=dict(arrowstyle='->',
					linewidth=2,
					shrinkA=0, shrinkB=0)
	ax.annotate('', v1, v0, arrowprops=arrowprops)


def Example2D():
	rng = np.random.RandomState(1)

	# X = np.dot(rng.rand(2,2), rng.randn(2,200)).T
	mean = [0,0]
	cov = [[1,0], [0,10]]
	X = np.random.multivariate_normal(mean, cov, 2000)

	pca = decomposition.PCA(n_components=2)
	pca.fit(X)

	# plot data
	plt.scatter(X[:, 0], X[:, 1], alpha=0.2)
	for length, vector in zip(pca.explained_variance_, pca.components_):
		v = vector * 3 * np.sqrt(length)
		draw_vector(pca.mean_, pca.mean_ + v)

	plt.plot(X[:,0], X[:,1], marker = 'o', linestyle = 'None')
	plt.axis('equal')
	plt.show()






if __name__ == '__main__':
	Example2D()