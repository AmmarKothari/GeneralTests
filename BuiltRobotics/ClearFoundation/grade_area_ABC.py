from abc import ABC, abstractmethod
from ammar_super import AmmarSuper


class grade_area_ABC(AmmarSuper, ABC):
	def __init__(self, grading_poly):
		self.grading_poly = grading_poly

	@abstractmethod
	def draw(self):
		pass

	@abstractmethod
	def poly(self):
		pass

