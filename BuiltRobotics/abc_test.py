from abc import ABCMeta, abstractmethod, abstractproperty



class test(object):
	__metaclass__ = ABCMeta

	def __init__(self):
		print('Doing things')

	@abstractmethod
	def meth_1(self):
		raise NotImplementedError


class child_test(test):
	def __init__(self):
		super(child_test, self).__init__()
		print('Here now')

	def meth_1(self):
		print('I am implemented')
