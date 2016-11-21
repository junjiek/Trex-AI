import cv2
import numpy as np
import operator
from matplotlib import pyplot as plt
from enum import Enum

  # HDPI: {
  #   CACTUS_LARGE: {x: 652,y: 2},
  #   CACTUS_SMALL: {x: 446,y: 2},
  #   CLOUD: {x: 166,y: 2},
  #   HORIZON: {x: 2,y: 104},
  #   PTERODACTYL: {x: 260,y: 2},
  #   RESTART: {x: 2,y: 2},
  #   TEXT_SPRITE: {x: 954,y: 2},
  #   TREX: {x: 1338,y: 2}
  # }

#   HorizonLine.dimensions = {
#   WIDTH: 600,
#   HEIGHT: 12,
#   YPOS: 127
# };

# GameOverPanel.dimensions = {
#   TEXT_X: 0,
#   TEXT_Y: 13,
#   TEXT_WIDTH: 191,
#   TEXT_HEIGHT: 11,
#   RESTART_WIDTH: 36,
#   RESTART_HEIGHT: 32
# };

# Trex.config = {
#   DROP_VELOCITY: -5,
#   GRAVITY: 0.6,
#   HEIGHT: 47,
#   HEIGHT_DUCK: 25,
#   INIITAL_JUMP_VELOCITY: -10,
#   INTRO_DURATION: 1500,
#   MAX_JUMP_HEIGHT: 30,
#   MIN_JUMP_HEIGHT: 30,
#   SPEED_DROP_COEFFICIENT: 3,
#   SPRITE_WIDTH: 262,
#   START_X_POS: 50,
#   WIDTH: 44,
#   WIDTH_DUCK: 59
# };

# 
# Obstacle.types = [
#   {
#     type: 'CACTUS_SMALL',
#     width: 17,
#     height: 35,
#     yPos: 105,
#     multipleSpeed: 4,
#     minGap: 120,
#     minSpeed: 0,
#     collisionBoxes: [
#       new CollisionBox(0, 7, 5, 27),
#       new CollisionBox(4, 0, 6, 34),
#       new CollisionBox(10, 4, 7, 14)
#     ]
#   },
#   {
#     type: 'CACTUS_LARGE',
#     width: 25,
#     height: 50,
#     yPos: 90,
#     multipleSpeed: 7,
#     minGap: 120,
#     minSpeed: 0,
#     collisionBoxes: [
#       new CollisionBox(0, 12, 7, 38),
#       new CollisionBox(8, 0, 7, 49),
#       new CollisionBox(13, 10, 10, 38)
#     ]
#   },
#   {
#     type: 'PTERODACTYL',
#     width: 46,
#     height: 40,
#     yPos: [ 100, 75, 50 ], // Variable height.
#     yPosMobile: [ 100, 50 ], // Variable height mobile.
#     multipleSpeed: 999,
#     minSpeed: 8.5,
#     minGap: 150,
#     collisionBoxes: [
#       new CollisionBox(15, 15, 16, 5),
#       new CollisionBox(18, 21, 24, 6),
#       new CollisionBox(2, 14, 4, 3),
#       new CollisionBox(6, 10, 4, 7),
#       new CollisionBox(10, 8, 6, 9)
#     ],
#     numFrames: 2,
#     frameRate: 1000/6,
#     speedOffset: .8
#   }
# ];
# Trex.collisionBoxes = {
#   DUCKING: [
#     new CollisionBox(1, 18, 55, 25)
#   ],
#   RUNNING: [
#     new CollisionBox(22, 0, 17, 16),
#     new CollisionBox(1, 18, 30, 9),
#     new CollisionBox(10, 35, 14, 8),
#     new CollisionBox(1, 24, 29, 5),
#     new CollisionBox(5, 30, 21, 4),
#     new CollisionBox(9, 34, 15, 4)
#   ]
# };

# Cloud.config = {
#   HEIGHT: 14,
#   MAX_CLOUD_GAP: 400,
#   MAX_SKY_LEVEL: 30,
#   MIN_CLOUD_GAP: 100,
#   MIN_SKY_LEVEL: 71,
#   WIDTH: 46
# };



img = cv2.imread('./assets/offline-sprite-2x.png', cv2.IMREAD_UNCHANGED)
x = 2
y = 2
w = 36
h = 32

roi = img[y : y + h * 2, x : x + w * 2]
cv2.imwrite('./assets/restart.png', roi)
# cv2.imshow('image',roi)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

    # this.canvasCtx.drawImage(Runner.imageSprite,
    #     this.restartImgPos.x, this.restartImgPos.y,
    #     restartSourceWidth, restartSourceHeight,
    #     restartTargetX, restartTargetY, dimensions.RESTART_WIDTH,
    #     dimensions.RESTART_HEIGHT);
