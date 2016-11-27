import os
import time
import sys
import pygame
from numpy import *
sys.path.append("../pygame/")
sys.path.append('../control/')
import wrapped_trex as game
from image_processor import imageProcessor

ACTIONS = 2

def main():
	game_state = game.GameState()
	img_processor = imageProcessor()
	start_time = None
	action = zeros(ACTIONS)
	action[0] = 1
	while 1:
		time.sleep(0.0005)
		if start_time is not None:
			delta_time = time.time() - start_time
		else:
			delta_time = 0
		start_time = time.time()
		x_t, r_0, terminal = game_state.frame_step(action)
		action[0] = 1
		action[1] = 0
		if not terminal:
			img_processor.detectObjects(x_t, delta_time)
			if img_processor.jumping or img_processor.dropping: continue
			birds, cacti = img_processor.getObstacles()
			# print birds, cacti
			if len(birds) == 0 and len(cacti) == 0: continue
			if len(birds) == 0:
				firstObstcale = cacti[0]
			elif len(cacti) == 0:
				firstObstcale = birds[0]
			elif cacti[0].x < birds[0].x:
				firstObstcale = cacti[0]
			else:
				firstObstcale = birds[0]
			# print firstObstcale.x, img_processor.tRex.x
			if firstObstcale is None:
				# controller.jump()
				action[0] = 0
				action[1] = 1
				continue
			if img_processor.tRex is None:
				# controller.jump()
				action[0] = 0
				action[1] = 1
				continue
			if ((firstObstcale.x + firstObstcale.w) - img_processor.tRex.x) < 200:
				action[0] = 0
				action[1] = 1
			elif firstObstcale.speed > 0:
				if (firstObstcale.x - img_processor.tRex.x) / firstObstcale.speed < 0.3:
					action[0] = 0
					action[1] = 1
				if ((firstObstcale.x + firstObstcale.w) - img_processor.tRex.x) / firstObstcale.speed < 0.4:
					action[0] = 0
					action[1] = 1
		# else:
			# game_state.restart()

		

if __name__ == "__main__":
	main()