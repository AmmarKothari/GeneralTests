from multiprocessing import Process, Pool, Queue

def f(x):
	return x*x

def pool_test():
	p = Pool(5)
	out = p.map(f, range(10))
	print('Print Values: %s' %out)

def process_test():
	ps = [Process(target = f, args=(i,)) for i in range(10)]
	[p.start() for p in ps]
	[p.join() for p in ps]

def queue_func(q,i):
	q.put(f(i))

def queue_test():
	qs = [Queue() for i in range(10)]
	ps = [Process(target = queue_func, args=(q,i)) for q,i in zip(qs,range(10))]
	[p.start() for p in ps]
	out = [q.get()	 for q in qs]
	[p.join() for p in ps]
	print('Print Values: %s' %out)

def queue_single():
	q = Queue()
	ps = [Process(target = queue_func, args=(q,i)) for i in range(10)]
	[p.start() for p in ps]
	out = [q.get() for i in range(11)]
	[p.join() for p in ps]
	print('Print Values: %s' %out)



if __name__ == '__main__':
	queue_single()