v0 = 2
a = -0.2
p = 0
pf = -v0**2/(2*a) # distance to finish

vs = [v0]
ps = [p]
ts = [0]

dt = 0.1
plt.ion()
plt.plot(pf, 'go')
# while np.abs(p - pf) > 0.5:
while vs[-1] > 0.1:
# while ts[-1] < 20:
	v = vs[-1] + a*dt
	p = ps[-1] + v*dt
	ps.append(p)
	vs.append(v)
	ts.append(ts[-1] + dt)

	plt.plot(ts, ps, 'rx')
	plt.plot(ts, vs, 'kx')
	plt.draw()
	plt.pause(0.00001)



pdb.set_trace()
