import cv2
import numpy as np
from matplotlib import pyplot as plt
from enum import Enum


# TODO: the dinasour run into an obstacle.

def isNear(value, target, epsilon):
	return abs(value - target) < epsilon

class rectangle(object):
	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

	def __str__(self):
		return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.w) + ", " + str(self.h) + ")"

	def __repr__(self):
		return self.__str__()

class imageProcessor(object):
	"""
	Extract features from game screenshots
	"""
	def clear(self):
		self.tRex = None
		self.cactus = []
		self.bird = []

	def isTRex(self, x, y, w, h):
		if isNear(w, 85, 5) and isNear(h, 90, 5):
			return True
		# Ducking
		if isNear(w, 116, 5) and isNear(h, 60, 3):
			return True
		return False

	def isBird(self, w, h):
		# (w, h): (86, 54), (86, 62)
		return isNear(w, 92, 3) and (isNear(h, 60, 3) or isNear(h, 68, 3))

	def isCactus(self, w, h):
		return isNear(h, 70, 2) or isNear(h, 100, 2)

	def findObjects(self, img):
		self.clear()
		ret, binary = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)
		contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
		cv2.drawContours(img, contours, -1, (255, 0, 0), 3)
		# name = ''
		for contour in contours:
			x, y, w, h = cv2.boundingRect(contour)
			# Ignoring things that the trex have passed.
			if x < 40:
				continue
			# Ignoring too small bounding boxes.
			if w < 30 or h < 30:
				continue
			roi = img[y : y + h, x : x + w]
			if self.isTRex(x, y, w, h):
				self.tRex = rectangle(x, y, w, h)
				# name += 'TRex '
			elif self.isBird(w, h):
				self.bird.append(rectangle(x, y, w, h))
				# name += 'Bird '
			elif self.isCactus(w, h):
				self.cactus.append(rectangle(x, y, w, h))
				# name += 'Cactus '
			else:
				# name += 'Unrecognized '
				cv2.imwrite(str(x) + '-' + str(y) + '-' + str(w) + '-' + str(h) + '.jpg', roi)
			# cv2.rectangle(img, (x, y), (x + w, y + h), (200, 0, 0), 2)
		# cv2.imwrite(name + '.jpg', img)

def main():
	img = cv2.imread('image.jpg', 0)
	processor = imageProcessor()
	processor.findObstacles(img)
	
if __name__ == '__main__':
	main()


