"""
Link: https://www.codewars.com/kata/5a5db0f580eba84589000979/train/python
"""
class Zombie:
	def __init__(self, x: int, y: int, health: int):
		self.position = [x ,y]
		self._health = health

	@property
	def health(self):
		return self._health
	
	@health.setter
	def health(self, new_hp):
		return max(new_hp, 0)

	def walk(self):
		x -= 1
		self.position = [x, y]


class peeshooter():
	pass


def plants_and_zombies(lawn,zombies):
	#your code goes here. you can do it!
	pass
