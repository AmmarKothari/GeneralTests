import unittest
from mycode import *




class MyFirstTests(unittest.TestCase):

	def runTest(self):
		self.test_hello()

	def test_hello(self):
		self.assertEqual(hello_world(), 'hello world')

	def test_custom_num_list(self):
		self.assertEqual(len(create_num_list(10)), 10)


unittest.main()