import os
from image_processor import imageProcessor
from controller import TrexGameController
import time

# Path to t-rex game html page.
game_path = 'file://' + os.path.abspath(os.path.join(os.getcwd(), '..')) + '/game/index.html'

def main():
	controller = TrexGameController(game_path)
	img_processor = imageProcessor()
	start_time = None
	while 1:
		time.sleep(0.0005)
		if controller.hasStart():
			if start_time is not None:
				delta_time = time.time() - start_time
			else:
				delta_time = 0
			start_time = time.time()
			distanceRan = controller.getDistanceRan()
			crashed = controller.getCrashed()
			if not crashed:
				# print controller.getObstacles()
				# print distanceRan
				img_processor.detectObjects(controller.getImage(), delta_time)
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
					controller.jump()
					continue
				if ((firstObstcale.x + firstObstcale.w) - img_processor.tRex.x) < 200:
					controller.jump()
				elif firstObstcale.speed > 0:
					if (firstObstcale.x - img_processor.tRex.x) / firstObstcale.speed < 0.3:
						controller.jump()
					if ((firstObstcale.x + firstObstcale.w) - img_processor.tRex.x) / firstObstcale.speed < 0.4:
						controller.jump()

		

if __name__ == "__main__":
	main()