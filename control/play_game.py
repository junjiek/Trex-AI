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
		# Jump.
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
				birds, cacti = img_processor.getObstacles()
				status = ''
				printInfo = False
				if img_processor.jumping and not controller.isJumping():
					printInfo = True
					status += 'jumping'
				if img_processor.dropping and not controller.isJumping():
					printInfo = True
					status += 'dropping'
				if img_processor.ducking and not controller.isDucking():
					printInfo = True
					status += 'ducking'
				if printInfo:
					print 'Wrong status: '
					print 'tRex :', img_processor.tRex, status
					print 'brids:', img_processor.birds
					print 'cacti:', img_processor.cacti
		time.sleep(0.0005)

if __name__ == "__main__":
	main()