import cv2
import numpy as np
import operator
from matplotlib import pyplot as plt
from enum import Enum


# TODO: the dinasour run into an obstacle.

def isNear(value, target, epsilon):
	return abs(value - target) < epsilon

class objectRectangle(object):
	"""
	The bounding box for T-Rex, Bird, Cactus.
	The box is represented by (x, y, w, h).
	'speed' is calculated based on the moving distance in delta time.
	'speed' will be initialized as 0 if not calculated.
	"""
	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.speed = 0;

	# For debug printing.
	def __str__(self):
		return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.w) + \
			   ", " + str(self.h) + "; " + str(self.speed) + ")"

	def __repr__(self):
		return self.__str__()

def rectSimilar(rect1, rect2):
	return isNear(rect1.w, rect2.w, 3) and isNear(rect1.h, rect2.h, 3)

class imageProcessor(object):
	"""
	Extract features from game screenshots
	"""
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

	def isEndGahmeLogo(self, w, h):
		return isNear(w, 72, 2) and isNear(h, 64, 2)

	def detectObjects(self, img, delta_time):
		print "----- delta_time: ", delta_time
		ret, binary = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)
		contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
		cv2.drawContours(img, contours, -1, (255, 0, 0), 3)
		# name = ''
		birds = []
		cacti = []
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
				self.tRex = objectRectangle(x, y, w, h)
				# name += 'TRex '
			elif self.isBird(w, h):
				birds.append(objectRectangle(x, y, w, h))
				# name += 'Bird '
			elif self.isCactus(w, h):
				cacti.append(objectRectangle(x, y, w, h))
				# name += 'Cactus '
			else:
				# name += 'Unrecognized '
				print "WARN: Unrecognized Object"
				cv2.imwrite(str(x) + '-' + str(y) + '-' + str(w) + '-' + str(h) + '.jpg', roi)
			# cv2.rectangle(img, (x, y), (x + w, y + h), (200, 0, 0), 2)
		# cv2.imwrite(name + '.jpg', img)

		# Calculates speed.
		if delta_time > 0 and len(birds) > 0 and len(self.birds) > 0:
			birds.sort(key=operator.attrgetter('x'))
			match_pos = 0
			# Find the first matching bird. 
			for match_pos in range(len(self.birds)):
				if rectSimilar(birds[0], self.birds[match_pos]):
					birds[0].speed = float(self.birds[match_pos].x - birds[0].x) / delta_time
					break
			# Match the subsequent birds in order.
			for i in range(1, len(birds)):
				if match_pos + i >= len(self.birds): break
				if rectSimilar(birds[i], self.birds[match_pos + i]):
					birds[i].speed = float(self.birds[match_pos + i].x - birds[i].x) / delta_time

		self.birds = birds

		if delta_time > 0 and len(cacti) > 0 and len(self.cacti) > 0:
			cacti.sort(key=operator.attrgetter('x'))
			match_pos = 0
			for match_pos in range(len(self.cacti)):
				if rectSimilar(cacti[0], self.cacti[match_pos]):
					cacti[0].speed = float(self.cacti[match_pos].x - cacti[0].x) / delta_time
					break

			for i in range(1, len(cacti)):
				if match_pos + i >= len(self.cacti): break
				if rectSimilar(cacti[i], self.cacti[match_pos + i]):
					cacti[i].speed = float(self.cacti[match_pos + i].x - cacti[i].x) / delta_time

			for c in cacti:
				for pre_c in self.cacti:
					if rectSimilar(c, pre_c):
						c.speed = float(pre_c.x - c.x) / delta_time
		self.cacti = cacti

def main():
	img = cv2.imread('image.jpg', 0)
	processor = imageProcessor()
	processor.findObstacles(img)
	
if __name__ == '__main__':
	main()


