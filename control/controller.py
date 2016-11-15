import base64
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
# from keras.models import Sequential
import cv2
import numpy as np

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
		obstacle_length = self.driver.execute_script("return tRexGameRunner.horizon.obstacles.length;")
		if obstacle_length is None:
			return []
		obstacles = []
		for i in range(obstacle_length):
			xPos = self.driver.execute_script("return tRexGameRunner.horizon.obstacles[" + str(i) + "].xPos;")
			width = self.driver.execute_script("return tRexGameRunner.horizon.obstacles[" + str(i) + "].width;")
			obstacles.append((xPos, width))
		return obstacles

	def getCurrentSpeed(self):
		return self.driver.execute_script("return tRexGameRunner.currentSpeed;")

	def isJumping(self):
		return self.driver.execute_script("return tRexGameRunner.tRex.jumping;")

	def isDucking(self):
		return self.driver.execute_script("return tRexGameRunner.tRex.ducking;")

	def isHIDPI(self):
		return self.driver.execute_script("return IS_HIDPI;")

	def getJumpVelocity(self):
		return self.driver.execute_script("return tRexGameRunner.tRex.jumpVelocity;")

	def restart(self):
		self.body.send_keys(Keys.SPACE)

	def jump(self):
		self.body.send_keys(Keys.SPACE)

	def duck(self):
		self.body.send_keys(Keys.ARROW_DOWN)

