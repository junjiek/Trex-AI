import os, base64
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
# from keras.models import Sequential
import cv2
import numpy as np
from matplotlib import pyplot as plt
from process_image import *
import time

# Path to t-rex game html page.
game_path = 'file://' + os.path.abspath(os.path.join(os.getcwd(), '..')) + '/game/index.html'
get_features_from_image = True

class TrexGameController(object):
	"""
	Controller for the T-rex Game in javascript
	"""
	def __init__(self, game_path):
		self.game_path = game_path
		self.chrome_options = Options()
		# Disable security in Chrome to Allow-Control-Allow-Origin.
		self.chrome_options.add_argument("--disable-web-security")
		self.driver = webdriver.Chrome('./chromedriver', chrome_options=self.chrome_options)
		self.driver.get(self.game_path)
		self.body = self.driver.find_element_by_tag_name('body')
		self.canvas = self.driver.find_element_by_id('game-canvas')
		self.img_processor = None
		if get_features_from_image:
			self.img_processor = imageProcessor()
	
	def getDistanceRan(self):
		return self.driver.execute_script("return tRexGameRunner.distanceRan;")

	def getCrashed(self):
		return self.driver.execute_script("return tRexGameRunner.crashed;")

	def getImage(self):
		# Get the canvas as a PNG base64 string and decode.
		canvas_base64 = self.driver.execute_script("return arguments[0].toDataURL().substring(22);", self.canvas)
		canvas_png = base64.b64decode(canvas_base64)
		npimg = np.fromstring(canvas_png, dtype=np.uint8); 
		img = cv2.imdecode(npimg, 0)
		return img

	def hasStart(self):
		return self.driver.execute_script("return tRexGameRunner.runningTime > tRexGameRunner.config.CLEAR_TIME;");

	def getObstacles(self):
		if self.img_processor is None:
			obstacle_length = self.driver.execute_script("return tRexGameRunner.horizon.obstacles.length;")
			if obstacle_length is None:
				return []
			obstacles = []
			for i in range(obstacle_length):
				xPos = self.driver.execute_script("return tRexGameRunner.horizon.obstacles[" + str(i) + "].xPos;")
				width = self.driver.execute_script("return tRexGameRunner.horizon.obstacles[" + str(i) + "].width;")
				obstacles.append((xPos, width))
			return obstacles
		return self.img_processor.cacti, self.img_processor.birds

	def getObjectInfoFromImage(self, delta_time):
		self.img_processor.detectObjects(self.getImage(), delta_time)

	def getCurrentSpeed(self):
		return self.driver.execute_script("return tRexGameRunner.currentSpeed;")

	def isJumping(self):
		if self.img_processor is None:
			return self.driver.execute_script("return tRexGameRunner.tRex.jumping;")
		return self.img_processor.isJumping

	def isDropping(self):
		if self.img_processor is None:
			return False
		return self.img_processor.isDropping

	def isDucking(self):
		if self.img_processor is None:
			return False
		return self.img_processor.isDucking

	def isHIDPI(self):
		return self.driver.execute_script("return IS_HIDPI;")

	def getJumpVelocity(self):
		if self.img_processor is None:
			return self.driver.execute_script("return tRexGameRunner.tRex.jumpVelocity;")
		else:
			return self.img_processor.tRex.speed

	def restart(self):
		self.body.send_keys(Keys.SPACE)

	def jump(self):
		self.body.send_keys(Keys.SPACE)

	def duck(self):
		self.body.send_keys(Keys.ARROW_DOWN)

def main():
	controller = TrexGameController(game_path)
	# your code
	start_time = None
	while 1:
		# Jump.
		if controller.hasStart():
			distanceRan = controller.getDistanceRan()
			crashed = controller.getCrashed()
			if not crashed:
				# print controller.getObstacles()
				# print distanceRan
				if start_time is not None:
					delta_time = time.time() - start_time
				else:
					delta_time = 0
				controller.getObjectInfoFromImage(delta_time)
				birds, cacti = controller.getObstacles()
				status = ''
				if controller.isJumping():
					status += 'jumping'
				if controller.isDropping():
					status += 'dropping'
				if controller.isDucking():
					status += 'ducking'
				print 'tRex :', controller.img_processor.tRex, status
				print 'brids:', birds
				print 'cacti:', cacti

			start_time = time.time()
		time.sleep(0.005)



if __name__ == "__main__":
	main()