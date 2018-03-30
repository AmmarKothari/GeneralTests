'''
Implementing a 2D version of IRL policy improvement

'''


import numpy as np
import pdb, copy, sys
from sklearn import svm
import matplotlib.pyplot as plt

def plotNonLinearBoundary(ax, clf):
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
	ax.scatter(clf.support_vectors_[:, 0], clf.support_vectors_[:, 1], s=100, linewidth=1, facecolors='none')

def plotLinearBoundary(ax, clf):
	xlim = ax.get_xlim()
	ylim = ax.get_ylim()

	# get equations for lines
	a,b = getBoundaryLine(clf)
	a1, b1 = getParallelLine(a,b,clf.support_vectors_[0])
	a2, b2 = getParallelLine(a,b,clf.support_vectors_[1])
	a1p, b1p = getPerpendicularLine(a,b, clf.support_vectors_[0])

	# evaluate at certain points
	x = np.arange(xlim[0], xlim[1])
	y = a*x + b

	y1 = a1*x + b1
	y2 = a2*x + b2
	y1p = a1p*x + b1p

	# plot points
	ax.plot(x,y,linestyle='-')
	ax.plot(x,y1,linestyle='--')
	ax.plot(x,y2,linestyle='--')
	ax.plot(x,y1p,linestyle='--')

	# plot support vectors
	ax.scatter(clf.support_vectors_[:, 0], clf.support_vectors_[:, 1], s=100, linewidth=1, facecolors='none')

	# reset window limits
	# ax.set_xlim(xlim)
	# ax.set_ylim(ylim)

def plotSVM(X, y, clf):
	plt.cla()
	plt.scatter(X[:, 0], X[:, 1], c=y, s=30, cmap=plt.cm.Paired, marker="x")

	# plot the decision function
	ax = plt.gca()
	# plotNonLinearBoundary(ax,clf)
	plotLinearBoundary(ax, clf)

	plt.ion()
	plt.show()
	plt.pause(0.1)
	# pdb.set_trace()
	# plt.show()



def getBoundaryLine(clf):
	# returns the coefficients for the decision boundary
	W = clf.coef_[0]
	I = clf.intercept_
	a = -W[0]/W[1]
	b = -I[0]/W[1]
	return a,b

def getParallelLine(a,b,xy):
	# calculate parallel line through given point
	# return m and b
	a_p = a
	b_p = xy[1] - a*xy[0]
	return a_p, b_p

def getPerpendicularLine(a,b, xy):
	# returns the coefficients of the line perp to boundary and through the support vector
	# xy should not be the optimal policy
	c = -1/a
	d = xy[1] - c*xy[0]
	return c,d

def onLine(a,b,xy):
	# sees if a point is on a line
	y_test = a*xy[0] + b
	pdb.set_trace()

def randEntry(entries):
	# chooses a random entry from arrray and returns it
	i_r = np.random.randint(len(entries))
	return entries[i_r]

def normVec(vec):
	#returns normalized version of vector
	return [vec[0], vec[1]] /np.linalg.norm([vec[0], vec[1]])

def clamp(pi, lims):
	# limits the possible values of a policy
	return np.clip(pi, *lims)

def optimizePolicy(w):
	# find the set of values that achieves a max value given the current weighting
	ITER = 100 # number of iterations to run for
	N = 50 # number of samples per iteration
	M = 10 # number to keep from previous iteration
	x = [0,0]
	# simulated annealing
	x_last = [copy.deepcopy(x) for i in range(M)]
	xs = [copy.deepcopy(x) for i in range(N)]
	mu = [np.array([0]) for i in range(N)]
	for i in range(ITER):
		# generate new solutions -- the first M solutions are from last time
		for j in range(N-M):
			sol = randEntry(x_last)
			xs[j+M] = clamp(sol + np.random.randn(np.size(sol)), [-100.0, 100.0])
			mu[j+M] = np.matmul(xs[j+M], w.T) # evaluate policy step
		
		# evaluate solutions
		sort_idx = np.argsort(mu, axis=0).ravel()
		mu = [mu[s] for s in sort_idx]
		xs = [xs[s] for s in sort_idx]
		x_last = copy.deepcopy(xs[-M:])
	return xs[-1].reshape(1,-1)


mu_optimal = np.array([[100.0, 100.0], [98, 100], [100, 97], [98, 97]]).reshape(-1,2)
epsilon = 1
step_size = 1e-1


w0 = np.array([-1,-1]).reshape(1,2)
w = copy.deepcopy(w0)
mu_initial = optimizePolicy(w)
mus = copy.deepcopy(mu_initial)

# pdb.set_trace()
while abs(np.mean(np.matmul(mu_optimal, w.T)) - np.matmul(mus[-1], w.T)) > epsilon:
	X_iter = np.append(mus, mu_optimal, axis=0)
	y_iter = np.append(np.zeros(len(mus)), np.ones(len(mu_optimal)))
	clf = svm.SVC(kernel='linear', C=1000)
	clf.fit(X_iter, y_iter)
	plotSVM(X_iter, y_iter, clf)
	a,b = getBoundaryLine(clf)
	ap, bp = getPerpendicularLine(a,b, clf.support_vectors_[0])
	
	# how to update w? - unit vector that points along perp
	dx = 1e-2*(clf.support_vectors_[-1][0] - clf.support_vectors_[0][0])
	xv = clf.support_vectors_[0][0] + dx #choose x so it moves toward expert
	yv = ap*xv + bp
	dy = yv - clf.support_vectors_[0][1]
	w = w +  normVec([dx,dy]) * step_size # this may need to be improved to ensure its always towards the optimal policy
	if np.linalg.norm(w) < 0.1:
		w = normVec(w.ravel() + np.random.randn(2))

	w = normVec(w.ravel()) # L2 constraint
	print('W: %s, Pi: %s' %(w, mus[-1]))
	# optimize policy
	# calculate reward
	mus = np.append(mus, optimizePolicy(w), axis=0)

pdb.set_trace()
