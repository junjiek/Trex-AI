import cv2
import numpy as np
import operator
from matplotlib import pyplot as plt
from enum import Enum

def isNear(value, target, epsilon):
	return abs(value - target) <= epsilon

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

	def getInfo(self):
		return self.x, self.y, self.w, self.h, self.speed

def rectSimilar(rect1, rect2):
	return isNear(rect1.w, rect2.w, 3) and isNear(rect1.h, rect2.h, 3)

class imageProcessor(object):
	"""
	Extract features from game screenshots
	"""
	def __init__(self):
		self.tRex = None
		self.birds = []
		self.cacti = []
		self.jumping = False
		self.dropping = False
		self.ducking = False

	def isTRex(self, rect):
		if rect.y < 10:
			return True
		if isNear(rect.w, 80, 5) and isNear(rect.h, 86, 5):
			return True
		# Ducking
		if isNear(rect.w, 116, 5) and isNear(rect.h, 60, 3):
			self.ducking = True
			return True
		return False

	def biggerThanTRex(self, rect):
		if rect.w >= 86 and rect.h >= 80:
			return True
		if rect.w >= 100 and rect.h > 50:
			self.Ducking = True
			return True
		return False

	def isBird(self, rect):
		return isNear(rect.w, 84, 3) and (isNear(rect.h, 52, 3) or isNear(rect.h, 60, 3))

	def isCactus(self, rect):
		return isNear(rect.h, 66, 2) or isNear(rect.h, 92, 2) or isNear(rect.h, 96, 2)

	def isEndGahmeLogo(self, rect):
		return isNear(rect.w, 72, 2) and isNear(rect.h, 64, 2)

	def getObstacles(self):
		return self.cacti, self.birds

	def detectObjects(self, img, delta_time):
		img = cv2.cvtColor(cv2.resize(img.transpose(1,0,2), (1200, 300)), cv2.COLOR_RGB2GRAY)
		ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
		contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
		# cv2.drawContours(img, contours, -1, (255, 0, 0), 3)
		objectRects = []
		for contour in contours:
			x, y, w, h = cv2.boundingRect(contour)
			# Ignoring too small bounding boxes.
			if w < 30 or h < 30:
				continue
			objectRects.append(objectRectangle(x, y, w, h))
			# cv2.rectangle(img, (x, y), (x + w, y + h), (200, 0, 0), 2)
		# cv2.imshow('image',img)
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()
		objectRects.sort(key=operator.attrgetter('x'))

		# name = ''

		birds = []
		cacti = []
		tRex = None
		self.ducking = False
		self.dropping = False
		self.jumping = False
		for rect in objectRects:
			if self.isTRex(rect):
				# name += 'TRex '
				tRex = rect
			elif self.isBird(rect):
				# name += 'Bird '
				if rect.x > 40: birds.append(rect)
			elif self.isCactus(rect):
				# name += 'Cactus '
				if rect.x > 40: cacti.append(rect)
			elif tRex is None and self.biggerThanTRex(rect):
				# name += 'TRex '
				# print "WARN: Trex might run into other object"
				tRex = rect
				# x, y, w, h, s = rect.getInfo()
				# roi = img[y : y + h, x : x + w]
				# cv2.imwrite(str(x) + '-' + str(y) + '-' + str(w) + '-' + str(h) + '-trex.jpg', roi)
				# cv2.imwrite(name + '.jpg', img)
			elif rect.x > 10:
				# name += 'Unrecognized '
				# print "WARN: Unrecognized Object"
				x, y, w, h, s = rect.getInfo()
				roi = img[y : y + h, x : x + w]
				cv2.imwrite(str(x) + '-' + str(y) + '-' + str(w) + '-' + str(h) + '.jpg', roi)
		# cv2.imwrite(name + '.jpg', img)

		# T-rex jumping or dropping.
		if self.tRex is not None and tRex is not None:
			y_delta = (self.tRex.y + self.tRex.h) - (tRex.y + tRex.h)
			if y_delta >= 1:
				self.jumping = True
			elif y_delta <= -1:
				self.dropping = True
			if delta_time > 0:
				tRex.speed = float(y_delta) / delta_time
		self.tRex = tRex

		# Calculates speed for obstacles.
		if delta_time > 0 and len(birds) > 0 and len(self.birds) > 0:
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
			match_pos = 0
			for match_pos in range(len(self.cacti)):
				if rectSimilar(cacti[0], self.cacti[match_pos]):
					cacti[0].speed = float(self.cacti[match_pos].x - cacti[0].x) / delta_time
					break
			for i in range(1, len(cacti)):
				if match_pos + i >= len(self.cacti): break
				if rectSimilar(cacti[i], self.cacti[match_pos + i]):
					cacti[i].speed = float(self.cacti[match_pos + i].x - cacti[i].x) / delta_time
		self.cacti = cacti



