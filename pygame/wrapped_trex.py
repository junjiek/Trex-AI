import numpy as np
import sys
import random
import pygame
import pygame.surfarray as surfarray
import math
from pygame.locals import *
from itertools import cycle
from copy import deepcopy

FPS = 60.0
SAMPLE_FPS = 30.0
SCREENWIDTH  = 600
SCREENHEIGHT = 150

pygame.init()
# FPSCLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((SCREENWIDTH * 2, SCREENHEIGHT * 2))
pygame.display.set_caption('Trex')

IMAGES_PATH = (
    '../pygame/offline-sprite-1x.png',
    '../pygame/offline-sprite-2x.png',
)

IS_HIDPI = True

IMAGE_SPRITE = pygame.image.load(IMAGES_PATH[1]).convert_alpha()

def getRandomNum(min, max):
    return int(math.floor(random.random() * (max - min + 1))) + min

class GameState:
    config = {
        'ACCELERATION': 0.001,
        'BG_CLOUD_SPEED': 0.2,
        'BOTTOM_PAD': 10,
        'CLEAR_TIME': 3000,
        'CLOUD_FREQUENCY': 0.5,
        'GAMEOVER_CLEAR_TIME': 750,
        'GAP_COEFFICIENT': 0.6,
        'GRAVITY': 0.6,
        'INITIAL_JUMP_VELOCITY': 12,
        'MAX_CLOUDS': 6,
        'MAX_OBSTACLE_LENGTH': 3,
        'MAX_OBSTACLE_DUPLICATION': 2,
        'MAX_SPEED': 13,
        'MIN_JUMP_HEIGHT': 35,
        'SPEED': 9,
        'SPEED_DROP_COEFFICIENT': 3
    }
    spriteDefinition = {
        'LDPI': {
            'CACTUS_LARGE': {'x': 332, 'y': 2},
            'CACTUS_SMALL': {'x': 228, 'y': 2},
            'CLOUD': {'x': 86, 'y': 2},
            'HORIZON': {'x': 2, 'y': 54},
            'PTERODACTYL': {'x': 134, 'y': 2},
            'RESTART': {'x': 2, 'y': 2},
            'TEXT_SPRITE': {'x': 484, 'y': 2},
            'TREX': {'x': 677, 'y': 2}
        },
        'HDPI': {
            'CACTUS_LARGE': {'x': 652, 'y': 2},
            'CACTUS_SMALL': {'x': 446, 'y': 2},
            'CLOUD': {'x': 166, 'y': 2},
            'HORIZON': {'x': 2, 'y': 104},
            'PTERODACTYL': {'x': 260, 'y': 2},
            'RESTART': {'x': 2, 'y': 2},
            'TEXT_SPRITE': {'x': 954, 'y': 2},
            'TREX': {'x': 1338, 'y': 2}
        }
    }
    def __init__(self):
        self.obstacles = []
        self.runningTime = 0
        self.distanceRan = 0
        self.lastScore = 0
        self.dimensions = {
            'WIDTH': SCREENWIDTH,
            'HEIGHT': SCREENHEIGHT,
        }
        self.spriteDef = GameState.spriteDefinition['HDPI']
        self.msPerFrame = 1000.0 / FPS
        self.currentSpeed = GameState.config['SPEED']
        self.highestScore = 0
        self.started = False
        self.activated = False
        self.crashed = False
        self.paused = False
        self.playCount = 0
        self.horizon = Horizon(self.spriteDef, self.dimensions, GameState.config['GAP_COEFFICIENT'])
        self.tRex = Trex(self.spriteDef['TREX'])
        # Distance meter
        self.distanceMeter = DistanceMeter(self.spriteDef['TEXT_SPRITE'], self.dimensions['WIDTH'])
        self.gameOverPanel = None
        self.adjustDimensions()
        self.restart()

    def playIntro(self):
        if (not self.started and not self.crashed):
            self.playingIntro = True
            self.tRex.playingIntro = True
            self.activated = True
            self.started = True
        elif (self.crashed):
            self.restart()

    def startGame(self):
        self.runningTime = 0
        self.playingIntro = False
        self.tRex.playingIntro = False
        self.playCount += 1
    
    def jump_or_not(self):
        return self.tRex.jumping 

    def getScore(self):
        return self.distanceMeter.getActualDistance(self.distanceRan)

    def frame_step(self, input_actions):
        pygame.event.pump()
        background = pygame.Surface(SCREEN.get_size())
        background = background.convert()
        background.fill((247, 247, 247))
        SCREEN.blit(background, (0,0))
        reward = 0.1
        terminal = False

        if sum(input_actions) != 1:
            raise ValueError('Multiple input actions!')

        # input_actions[0] == 1: do nothing
        # input_actions[1] == 1: flap the bird
        if input_actions[1] == 1:
            if not self.tRex.jumping and not self.tRex.ducking:
                self.tRex.startJump(self.currentSpeed)
            self.tRex.setDuck(False)
        # elif input_actions[2] == 1:
        #     if (self.tRex.jumping):
        #         # Speed drop, activated only when jump key is not pressed.
        #         self.tRex.setSpeedDrop();
        #     elif not self.tRex.jumping and not self.tRex.ducking:
        #         # Duck.
        #         self.tRex.setDuck(True);


        deltaTime = 1000 / SAMPLE_FPS
        speed = self.currentSpeed
        if self.activated:
            if (self.tRex.jumping):
                self.tRex.updateJump(deltaTime)

            self.runningTime += deltaTime
            # hasObstacles = self.runningTime > GameState.config['CLEAR_TIME']
            hasObstacles = True
            if hasObstacles:
                self.horizon.updateObstacles(deltaTime, speed)

            # Check for collisions.
            collision = hasObstacles and checkForCollision(self.horizon.obstacles[0], self.tRex)
            if not collision:
                self.distanceRan += self.currentSpeed * deltaTime / self.msPerFrame
                #if (self.currentSpeed < GameState.config['MAX_SPEED']):
                    #self.currentSpeed += GameState.config['ACCELERATION']
            else:
                self.gameOver()
        
        self.tRex.update(deltaTime, self.tRex.status)
        if self.crashed:
            terminal = True
            reward = -100
            self.restart()

        image_data = pygame.surfarray.array3d(pygame.display.get_surface())

        if self.activated:
            self.distanceMeter.update(deltaTime, math.ceil(self.distanceRan))
            self.horizon.updateClouds(deltaTime, speed)
            self.horizon.updateHorizonLine(deltaTime, speed)


        pygame.display.update()
        # FPSCLOCK.tick(60)
        return image_data, reward, terminal

    def adjustDimensions(self):
        # Redraw the elements back onto the canvas.
        self.distanceMeter.calcXPos(self.dimensions['WIDTH'])
        self.horizon.update(0, 0, True)
        self.tRex.update(0, self.tRex.status)

        # Outer container and distance meter.
        if (self.activated or self.crashed or self.paused):
            self.distanceMeter.update(0, math.ceil(self.distanceRan))
            self.stop()
        else:
            self.tRex.draw(0, 0)

        # Game over panel.
        if (self.crashed and self.gameOverPanel):
            self.gameOverPanel.updateDimensions(self.dimensions['WIDTH'])
            self.gameOverPanel.draw()

    # Game over state.
    def gameOver(self):
        self.stop()
        self.crashed = True
        self.distanceMeter.acheivement = False
        # self.tRex.update(100, 'CRASHED')
        # Game over panel.
        # if self.gameOverPanel is None:
        #     self.gameOverPanel = GameOverPanel(self.spriteDef['TEXT_SPRITE'], self.spriteDef['RESTART'], self.dimensions)
        # else:
        #     self.gameOverPanel.draw()

        # Update the high score.
        if (self.distanceRan > self.highestScore):
            self.highestScore = math.ceil(self.distanceRan)
            self.distanceMeter.setHighScore(self.highestScore)

    def stop(self):
        self.activated = False
        self.paused = True

    def play(self):
        if not self.crashed:
            self.activated = True
            self.paused = False
            self.tRex.update(0, Trex.status.RUNNING)
            self.time = getTimeStamp()

    def restart(self):
        self.playCount += 1
        self.runningTime = 0
        self.activated = True
        self.crashed = False
        self.lastScore = self.getScore()
        self.distanceRan = 0
        self.currentSpeed = GameState.config['SPEED']
        self.distanceMeter.reset(self.highestScore)
        self.horizon.reset()
        self.tRex.reset()

class CollisionBox:
    """docstring for CollisionBox"""
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

class Trex:
    config = {
        'DROP_VELOCITY': -5,
        'GRAVITY': 0.6,
        'HEIGHT': 47,
        'HEIGHT_DUCK': 25,
        'INITIAL_JUMP_VELOCITY': -10,
        'INTRO_DURATION': 1500,
        'MAX_JUMP_HEIGHT': 30,
        'MIN_JUMP_HEIGHT': 30,
        'SPEED_DROP_COEFFICIENT': 3,
        'START_X_POS': 50,
        'WIDTH': 44,
        'WIDTH_DUCK': 59
    }
    collisionBoxes = {
        'DUCKING': [CollisionBox(1, 18, 55, 25)],
        'RUNNING':[ CollisionBox(22, 0, 17, 16), CollisionBox(1, 18, 30, 9), CollisionBox(10, 35, 14, 8), CollisionBox(1, 24, 29, 5), CollisionBox(5, 30, 21, 4), CollisionBox(9, 34, 15, 4)]
    }
    BLINK_TIMING = 7000
    def __init__(self, spritePos):
        self.spritePos = spritePos
        self.xPos = Trex.config['START_X_POS']
        self.yPos = 0
        # Current status.
        self.jumping = False
        self.ducking = False
        self.jumpVelocity = 0
        self.reachedMinHeight = False
        self.speedDrop = False
        self.jumpCount = 0
        self.jumpspotX = 0
        self.timer = 0

        # Position when on the ground.
        # self.groundYPos = 180
        self.groundYPos = SCREENHEIGHT - Trex.config['HEIGHT'] - GameState.config['BOTTOM_PAD'];
        self.yPos = self.groundYPos
        self.minJumpHeight = self.groundYPos - Trex.config['MIN_JUMP_HEIGHT']
        # self.msPerFrame = 1000.0 * 20 / FPS
        self.msPerFrame = 1000.0 / FPS
        self.currentFrame = 0
        self.currentAnimFrames = [0, 1]
        self.status = 'WAITING'
        self.update(0, 'WAITING')

    def update(self, deltaTime, status):
        self.timer += deltaTime
        if self.status != status:
            self.currentFrame = 0
            self.status = status
            if self.status == 'WAITING':
                self.msPerFrame = 1000.0 * 20 / FPS
                self.msPerFrame = 1000.0 / 3
                self.currentAnimFrames = [44, 0]
            elif self.status == 'RUNNING':
                self.msPerFrame = 1000.0 * 5 / FPS
                self.msPerFrame = 1000.0 / 12
                self.currentAnimFrames = [88, 132]
            elif self.status == 'CRASHED':
                self.msPerFrame = 1000.0 / FPS
                self.msPerFrame = 1000.0 / 60
                self.currentAnimFrames = [220]
            elif self.status == 'JUMPING':
                self.msPerFrame = 1000.0 / FPS
                self.msPerFrame = 1000.0 / 60
                self.currentAnimFrames = [0]
            elif self.status == 'DUCKING':
                self.msPerFrame = 1000.0 * 7.5 / FPS
                self.msPerFrame = 1000.0 / 8
                self.currentAnimFrames = [262, 321]
        if deltaTime > 0:
            self.draw(self.currentAnimFrames[self.currentFrame], 0)
        # Update the frame position.
        if self.timer >= self.msPerFrame:
            if self.currentFrame >= len(self.currentAnimFrames) - 1:
                self.currentFrame = 0
            else:
                self.currentFrame += 1 
            self.timer = 0
        if self.speedDrop and self.yPos == self.groundYPos:
            self.speedDrop = False
            self.setDuck(True)

    def draw(self, x, y):
        # Ducking.
        sourceX = x
        sourceY = y
        if self.ducking and self.status != 'CRASHED':
            sourceWidth = self.config['WIDTH_DUCK']
        else:
            sourceWidth = self.config['WIDTH']
        sourceHeight = self.config['HEIGHT']

        if (IS_HIDPI):
            sourceX *= 2
            sourceY *= 2
            sourceWidth *= 2
            sourceHeight *= 2
        sourceX += self.spritePos['x']
        sourceY += self.spritePos['y']
        if (self.ducking and self.status != 'CRASHED'):
            SCREEN.blit(IMAGE_SPRITE, \
                (self.xPos * 2, self.yPos * 2, self.config['WIDTH_DUCK'], self.config['HEIGHT']), \
                (sourceX, sourceY, sourceWidth, sourceHeight))
        else:
            # Crashed whilst ducking. Trex is standing up so needs adjustment.
            if (self.ducking and self.status == 'CRASHED'):
                self.xPos+=1
            # Standing / running

            SCREEN.blit(IMAGE_SPRITE, \
                (self.xPos * 2, self.yPos * 2 , self.config['WIDTH'], self.config['HEIGHT']), \
                (sourceX, sourceY, sourceWidth, sourceHeight))

    # def setBlinkDelay(self):
    #     self.blinkDelay = math.ceil(random.random() * Trex.config['BLINK_TIMING'])

    # def blink(self, time):
    #     deltaTime = time - self.animStartTime
    #     if (deltaTime >= self.blinkDelay):
    #         self.draw(self.currentAnimFrames[self.currentFrame], 0)
    #     if (self.currentFrame == 1):
    #         # Set new random delay to blink.
    #         self.setBlinkDelay()
    #         self.animStartTime = time

    def startJump(self, speed):
        if not self.jumping:
            self.update(0, 'JUMPING')
            # Tweak the jump velocity based on the speed.
            self.jumpVelocity = Trex.config['INITIAL_JUMP_VELOCITY'] - (speed / 10.0)
            self.jumping = True
            self.reachedMinHeight = False
            self.speedDrop = False

    # Jump is complete, falling down.
    def endJump(self):
        if self.reachedMinHeight and self.jumpVelocity < Trex.config['DROP_VELOCITY']:
            self.jumpVelocity = Trex.config['DROP_VELOCITY']

    # Update frame for a jump.
    # @param {number} deltaTime
    # @param {number} speed
    def updateJump(self, deltaTime):
        framesElapsed = deltaTime / self.msPerFrame
        # print self.yPos, self.jumpVelocity, self.reachedMinHeight
        # Speed drop makes Trex fall faster.
        if (self.speedDrop):
            self.yPos += round(self.jumpVelocity *
            Trex.config['SPEED_DROP_COEFFICIENT'] * framesElapsed)
        else:
            self.yPos += round(self.jumpVelocity * framesElapsed)
            self.jumpVelocity += Trex.config['GRAVITY'] * framesElapsed

        # Minimum height has been reached.
        if (self.yPos < self.minJumpHeight or self.speedDrop):
            self.reachedMinHeight = True
        # Reached max height
        if (self.yPos < Trex.config['MAX_JUMP_HEIGHT'] or self.speedDrop):
            self.endJump()

        # Back down at ground level. Jump completed.
        if (self.yPos > self.groundYPos):
            self.reset()
            self.jumpCount+=1

        # self.update(deltaTime, self.status)

    # Set the speed drop. Immediately cancels the current jump.
    def setSpeedDrop(self):
        self.speedDrop = True
        self.jumpVelocity = 1

    # @param {boolean} isDucking.
    def setDuck(self, isDucking):
        if (isDucking and self.status != 'DUCKING'):
            self.update(0, 'DUCKING')
            self.ducking = True
        elif (self.status == 'DUCKING'):
            self.update(0, 'RUNNING')
            self.ducking = False

    # Reset the t-rex to running at start of game.
    def reset(self):
        self.yPos = self.groundYPos
        self.jumpVelocity = 0
        self.jumping = False
        self.ducking = False
        self.update(0, 'RUNNING')
        self.midair = False
        self.speedDrop = False
        self.jumpCount = 0

class Obstacle:
    types = [{
        'type': 'CACTUS_SMALL',
        'width': 17,
        'height': 35,
        'spriteNum': 6,
        'yPos': 105,
        'multipleSpeed': 4,
        'minGap': 120,
        'minSpeed': 0,
        'collisionBoxes': [CollisionBox(0, 7, 5, 27), CollisionBox(4, 0, 6, 34), CollisionBox(10, 4, 7, 14)],
    },{
        'type': 'CACTUS_LARGE',
        'width': 25,
        'height': 50,
        'spriteNum': 6,
        'yPos': 90,
        'multipleSpeed': 7,
        'minGap': 120,
        'minSpeed': 0,
        'collisionBoxes': [CollisionBox(0, 12, 7, 38), CollisionBox(8, 0, 7, 49), CollisionBox(13, 10, 10, 38)],
    }]
    # },{
    #     'type': 'PTERODACTYL',
    #     'width': 46,
    #     'height': 40,
    #     'spriteNum': 1,
    #     'yPos': [ 100, 75, 60 ],
    #     'multipleSpeed': 999,
    #     'minSpeed': 8.5,
    #     'minGap': 150,
    #     'numFrames': 2,
    #     'frameRate': 1000.0/6,
    #     'speedOffset': .8,
    #     'collisionBoxes': [CollisionBox(15, 15, 16, 5), CollisionBox(18, 21, 24, 6), CollisionBox(2, 14, 4, 3), CollisionBox(6, 10, 4, 7), CollisionBox(10, 8, 6, 9)],
    # }]
    MAX_GAP_COEFFICIENT = 1.5
    MAX_OBSTACLE_LENGTH = 3
    def __init__(self, typeIdx, spriteImgPos, dimensions, gapCoefficient, speed):
        self.typeConfig = Obstacle.types[typeIdx]
        self.spritePos = spriteImgPos
        self.gapCoefficient = gapCoefficient
        self.size = getRandomNum(1, Obstacle.MAX_OBSTACLE_LENGTH)
        self.dimensions = dimensions
        self.remove = False
        self.xPos = 0
        self.yPos = 0
        self.width = 0
        self.height = 0
        self.gap = 0
        self.speedOffset = 0
        self.collisionBoxes = []
        self.followingObstacleCreated = False
        # For animated obstacles.
        self.currentFrame = 0
        self.timer = 0
        self.init(speed)
  
    # Initialise the DOM for the obstacle.
    # @param {number} speeds
    def init(self, speed):
        self.collisionBoxes = deepcopy(self.typeConfig['collisionBoxes'])
        # Only allow sizing if we're at the right speed.
        if (self.size > 1 and self.typeConfig['multipleSpeed'] > speed):
          self.size = 1

        self.width = self.typeConfig['width'] * self.size
        self.height = self.typeConfig['height']
        self.xPos = self.dimensions['WIDTH'] - self.width

        # Check if obstacle can be positioned at various heights.
        if type(self.typeConfig['yPos']) is list:
            yPosConfig = self.typeConfig['yPos']
            self.yPos = yPosConfig[getRandomNum(0, len(yPosConfig) - 1)]
        else:
            self.yPos = self.typeConfig['yPos']

        self.draw()

        # Make collision box adjustments,
        # Central box is adjusted to the size as one box.
        #      ____        ______        ________
        #    _|   |-|    _|     |-|    _|       |-|
        #   | |<->| |   | |<--->| |   | |<----->| |
        #   | | 1 | |   | |  2  | |   | |   3   | |
        #   |_|___|_|   |_|_____|_|   |_|_______|_|
        #
        if (self.size > 1):
            self.collisionBoxes[1].width = self.width - self.collisionBoxes[0].width -\
                                           self.collisionBoxes[2].width
            self.collisionBoxes[2].x = self.width - self.collisionBoxes[2].width

        # For obstacles that go at a different speed from the horizon.
        if 'speedOffset' in self.typeConfig:
            if random.random() > 0.5:
                self.speedOffset = self.typeConfig['speedOffset']
            else:
                self.speedOffset = -self.typeConfig['speedOffset']

        self.gap = self.getGap(self.gapCoefficient, speed)

    # Draw and crop based on size.
    def draw(self):
        sourceWidth = self.typeConfig['width']
        sourceHeight = self.typeConfig['height']

        if (IS_HIDPI):
            sourceWidth = sourceWidth * 2
            sourceHeight = sourceHeight * 2

        # X position in sprite.
        sourceX = (sourceWidth * self.size) * (0.5 * (self.size - 1)) + self.spritePos['x']

        # Animation frames.
        if (self.currentFrame > 0):
            sourceX += sourceWidth * self.currentFrame

        SCREEN.blit(IMAGE_SPRITE, 
            (self.xPos * 2, self.yPos * 2, self.typeConfig['width'] * self.size, self.typeConfig['height']),\
            (sourceX, self.spritePos['y'], sourceWidth * self.size, sourceHeight))

    # Obstacle frame update.
    # @param {number} deltaTime
    # @param {number} speed
    def update(self, deltaTime, speed):
        if self.remove: return
        if 'speedOffset' in self.typeConfig:
            speed += self.speedOffset
        self.xPos -= math.floor((speed * FPS / 1000.0) * deltaTime)

        # Update frame
        if 'numFrames' in self.typeConfig:
            self.timer += deltaTime
            if self.timer >= self.typeConfig['frameRate']:
                if self.currentFrame == self.typeConfig['numFrames'] - 1:
                    self.currentFrame = 0
                else:
                    self.currentFrame += 1
                self.timer = 0
        self.draw()
        if not self.isVisible():
            self.remove = True

    # Calculate a random gap size.
    # - Minimum gap gets wider as speed increses
    # @param {number} gapCoefficient
    # @param {number} speed
    # @return {number} The gap size.
    def getGap(self, gapCoefficient, speed):
        minGap = int(round(self.width * speed + self.typeConfig['minGap'] * gapCoefficient))
        maxGap = int(round(minGap * Obstacle.MAX_GAP_COEFFICIENT))
        return getRandomNum(minGap, maxGap)

    # Check if obstacle is visible.
    # @return {boolean} Whether the obstacle is in the game area.
    def isVisible(self):
        return self.xPos + self.width > 0


class GameOverPanel:
    dimensions = {
        'TEXT_X': 0,
        'TEXT_Y': 13,
        'TEXT_WIDTH': 191,
        'TEXT_HEIGHT': 11,
        'RESTART_WIDTH': 36,
        'RESTART_HEIGHT': 32
    }
    def __init__(self, textImgPos, restartImgPos, dimensions):
        self.canvasDimensions = dimensions
        self.textImgPos = textImgPos
        self.restartImgPos = restartImgPos
        self.draw()

    # Update the panel dimensions.
    # @param {number} width New canvas width.
    # @param {number} opt_height Optional new canvas height.
    def updateDimensions(self, width, opt_height):
        self.canvasDimensions['WIDTH'] = width
        if (opt_height):
            self.canvasDimensions['HEIGHT'] = opt_height

    # Draw the panel.
    def draw(self):
        dimensions = GameOverPanel.dimensions
        centerX = self.canvasDimensions['WIDTH'] / 2

        # Game over text.
        textSourceX = dimensions['TEXT_X']
        textSourceY = dimensions['TEXT_Y']
        textSourceWidth = dimensions['TEXT_WIDTH']
        textSourceHeight = dimensions['TEXT_HEIGHT']

        textTargetX = int(round(centerX - (dimensions['TEXT_WIDTH'] / 2)))
        textTargetY = int(round((self.canvasDimensions['HEIGHT'] - 25) / 3))
        textTargetWidth = dimensions['TEXT_WIDTH']
        textTargetHeight = dimensions['TEXT_HEIGHT']

        restartSourceWidth = dimensions['RESTART_WIDTH']
        restartSourceHeight = dimensions['RESTART_HEIGHT']
        restartTargetX = centerX - (dimensions['RESTART_WIDTH'] / 2)
        restartTargetY = self.canvasDimensions['HEIGHT'] / 2

        if IS_HIDPI:
            textSourceY *= 2
            textSourceX *= 2
            textSourceWidth *= 2
            textSourceHeight *= 2
            restartSourceWidth *= 2
            restartSourceHeight *= 2

        textSourceX += self.textImgPos['x']
        textSourceY += self.textImgPos['y']

        # Game over text from sprite.
        SCREEN.blit(IMAGE_SPRITE,\
            (textTargetX * 2, textTargetY * 2, textTargetWidth, textTargetHeight),\
            (textSourceX, textSourceY, textSourceWidth, textSourceHeight))
        # Restart button.
        SCREEN.blit(IMAGE_SPRITE,\
            (restartTargetX * 2, restartTargetY * 2, dimensions['RESTART_WIDTH'], dimensions['RESTART_HEIGHT']),\
            (self.restartImgPos['x'], self.restartImgPos['y'],
            restartSourceWidth, restartSourceHeight))

        

class DistanceMeter:
    config = {
        # Number of digits.
        'MAX_DISTANCE_UNITS': 5,
        # Distance that causes achievement animation.
        'ACHIEVEMENT_DISTANCE': 100,
        # Used for conversion from pixel distance to a scaled unit.
        'COEFFICIENT': 0.025,
        # Flash duration in milliseconds.
        'FLASH_DURATION': 1000 / 4,
        # Flash iterations for achievement animation.
        'FLASH_ITERATIONS': 3
    }
    dimensions = {
        'WIDTH': 10,
        'HEIGHT': 13,
        'DEST_WIDTH': 11,
    }
    yPos = [0, 13, 27, 40, 53, 67, 80, 93, 107, 120]
    def __init__(self, spritePos, canvasWidth):
        self.x = 0
        self.y = 5

        self.currentDistance = 0
        self.maxScore = 0
        self.highScore = ''
        self.digits = []
        self.acheivement = False
        self.defaultString = ''
        self.flashTimer = 0
        self.flashIterations = 0
        self.spritePos = spritePos
        self.config = DistanceMeter.config
        self.maxScoreUnits = self.config['MAX_DISTANCE_UNITS']
        self.init(canvasWidth)

    # Initialise the distance meter to '00000'.
    # @param {number} width Canvas width in px.
    def init(self, width):
        maxDistanceStr = ''

        self.calcXPos(width)
        self.maxScore = self.maxScoreUnits
        for i in range(self.maxScoreUnits):
            self.draw(i, 0, False)
            self.defaultString += '0'
            maxDistanceStr += '9'

        self.maxScore = int(maxDistanceStr)

    # Calculate the xPos in the canvas.
    # @param {number} canvasWidth
    def calcXPos(self, canvasWidth):
        self.x = canvasWidth - (DistanceMeter.dimensions['DEST_WIDTH'] *
            (self.maxScoreUnits + 1))

    # Draw a digit to canvas.
    # @param {number} digitPos Position of the digit.
    # @param {number} value Digit value 0-9.
    # @param {boolean} opt_highScore Whether drawing the high score.
    def draw(self, digitPos, value, opt_highScore):
        sourceWidth = DistanceMeter.dimensions['WIDTH']
        sourceHeight = DistanceMeter.dimensions['HEIGHT']
        sourceX = DistanceMeter.dimensions['WIDTH'] * value
        sourceY = 0

        targetX = digitPos * DistanceMeter.dimensions['DEST_WIDTH']
        targetY = self.y
        targetWidth = DistanceMeter.dimensions['WIDTH']
        targetHeight = DistanceMeter.dimensions['HEIGHT']

        # For high DPI we 2x source values.
        if IS_HIDPI:
            sourceWidth *= 2
            sourceHeight *= 2
            sourceX *= 2
        sourceX += self.spritePos['x']
        sourceY += self.spritePos['y']

        if (opt_highScore):
            # Left of the current score.
            highScoreX = self.x - (self.maxScoreUnits * 2) * DistanceMeter.dimensions['WIDTH']
            targetX += highScoreX
            targetY += self.y
        else:
            targetX += self.x
            targetY += self.y

        SCREEN.blit(IMAGE_SPRITE,\
            (targetX * 2, targetY * 2, targetWidth, targetHeight),\
            (sourceX, sourceY, sourceWidth, sourceHeight))

    # Covert pixel distance to a 'real' distance.
    # @param {number} distance Pixel distance ran.
    # @return {number} The 'real' distance ran.
    def getActualDistance(self, distance):
        if distance:
            return int(round(distance * self.config['COEFFICIENT']))
        return 0

    # Update the distance meter.
    # @param {number} distance
    # @param {number} deltaTime
    # @return {boolean} Whether the acheivement sound fx should be played.
    def update(self, deltaTime, distance):
        paint = True

        if not self.acheivement:
            distance = self.getActualDistance(distance)

            # Score has gone beyond the initial digit count.
            if (distance > self.maxScore and self.maxScoreUnits ==
                self.config['MAX_DISTANCE_UNITS']):
                self.maxScoreUnits += 1
                self.maxScore = int(self.maxScore + '9')
            else:
                self.distance = 0

            if (distance > 0):
                # Acheivement unlocked
                if (distance % self.config['ACHIEVEMENT_DISTANCE'] == 0):
                    # Flash score and play sound.
                    self.acheivement = True
                    self.flashTimer = 0

                # Create a string representation of the distance with leading 0.
                distanceStr = (self.defaultString + str(distance))[-self.maxScoreUnits:]
                self.digits = [d for d in distanceStr]
            else:
                self.digits = [d for d in self.defaultString]
        else:
            # Control flashing of the score on reaching acheivement.
            if (self.flashIterations <= self.config['FLASH_ITERATIONS']):
                self.flashTimer += deltaTime

                if (self.flashTimer < self.config['FLASH_DURATION']):
                  paint = False
                elif (self.flashTimer >
                    self.config['FLASH_DURATION'] * 2):
                  self.flashTimer = 0
                  self.flashIterations += 1
            else:
                self.acheivement = False
                self.flashIterations = 0
                self.flashTimer = 0

        # Draw the digits if not flashing.
        if (paint):
            for i in reversed(range(len(self.digits))):
                self.draw(i, int(self.digits[i]), False)
        self.drawHighScore()

    # Draw the high score.
    def drawHighScore(self):
        for i in reversed(range(len(self.highScore))):
          self.draw(i, int(self.highScore[i], 10), True)

    # Set the highscore as a array string.
    # Position of char in the sprite: H - 10, I - 11.
    # @param {number} distance Distance ran in pixels.
    def setHighScore(self, distance):
        distance = self.getActualDistance(distance)
        highScoreStr = (self.defaultString + str(distance))[-self.maxScoreUnits:]

        self.highScore = ['10', '11'] + [d for d in highScoreStr]

    # Reset the distance meter back to '00000'.
    def reset(self, highestScore):
        self.update(0, 0)
        self.setHighScore(highestScore)
        self.acheivement = False


class HorizonLine(object):
    """docstring for HorizonLine"""
    dimensions = {
        'WIDTH': 600,
        'HEIGHT': 12,
        'YPOS': 127
    }
    def __init__(self, spritePos):
        self.spritePos = spritePos
        self.dimensions = HorizonLine.dimensions
        self.bumpThreshold = 0.5
        self.sourceXPos = [self.spritePos['x'], self.spritePos['x'] + self.dimensions['WIDTH']]
        self.xPos = []
        self.yPos = 0
        self.sourceDimensions = {}
        self.setSourceDimensions()
        self.draw()

    def setSourceDimensions(self):
        for dimension in HorizonLine.dimensions:
            if (IS_HIDPI):
                if (dimension != 'YPOS'):
                    self.sourceDimensions[dimension] = HorizonLine.dimensions[dimension] * 2
            else:
                self.sourceDimensions[dimension] = HorizonLine.dimensions[dimension]

        self.xPos = [0, HorizonLine.dimensions['WIDTH']]
        self.yPos = HorizonLine.dimensions['YPOS']

    def draw(self):
        SCREEN.blit(IMAGE_SPRITE,\
            (self.xPos[0] * 2, self.yPos * 2, self.dimensions['WIDTH'], self.dimensions['HEIGHT']),\
            (self.sourceXPos[0], self.spritePos['y'], self.sourceDimensions['WIDTH'], self.sourceDimensions['HEIGHT']))
        SCREEN.blit(IMAGE_SPRITE,\
            (self.xPos[1] * 2, self.yPos * 2, self.dimensions['WIDTH'], self.dimensions['HEIGHT']),\
            (self.sourceXPos[1], self.spritePos['y'], self.sourceDimensions['WIDTH'], self.sourceDimensions['HEIGHT']))

    # Return the crop x position of a type.
    def getRandomType(self):
        if random.random() > self.bumpThreshold:
            return self.dimensions['WIDTH']
        return 0

    # Update the x position of an indivdual piece of the line.
    # @param {number} pos Line position.
    # @param {number} increment
    def updateXPos(self, pos, increment):
        line1 = pos
        line2 = 0
        if pos == 0:
            line2 = 1

        self.xPos[line1] -= increment
        self.xPos[line2] = self.xPos[line1] + self.dimensions['WIDTH']

        if (self.xPos[line1] <= -self.dimensions['WIDTH']):
            self.xPos[line1] += self.dimensions['WIDTH'] * 2
            self.xPos[line2] = self.xPos[line1] - self.dimensions['WIDTH']
            self.sourceXPos[line1] = self.getRandomType() + self.spritePos['x']

    # Update the horizon line.
    # @param {number} deltaTime
    # @param {number} speed
    def update(self, deltaTime, speed):
        increment = math.floor(speed * (FPS / 1000.0) * deltaTime)
        if (self.xPos[0] <= 0):
            self.updateXPos(0, increment)
        else:
            self.updateXPos(1, increment)
        self.draw()

    # Reset horizon to the starting position.
    def reset(self):
        self.xPos[0] = 0
        self.xPos[1] = self.dimensions['WIDTH']

class Cloud:
    config = {
      'HEIGHT': 14,
      'MAX_CLOUD_GAP': 400,
      'MAX_SKY_LEVEL': 30,
      'MIN_CLOUD_GAP': 100,
      'MIN_SKY_LEVEL': 71,
      'WIDTH': 46
    }
    def __init__(self, spritePos, containerWidth):
        self.containerWidth = containerWidth
        self.xPos = containerWidth
        self.spritePos = spritePos
        self.yPos = 0
        self.remove = False
        self.cloudGap = getRandomNum(Cloud.config['MIN_CLOUD_GAP'], Cloud.config['MAX_CLOUD_GAP'])
        self.init()

    def init(self):
        self.yPos = getRandomNum(Cloud.config['MAX_SKY_LEVEL'], Cloud.config['MIN_SKY_LEVEL'])
        self.draw()

    # Draw the cloud.
    def draw(self):
        sourceWidth = Cloud.config['WIDTH']
        sourceHeight = Cloud.config['HEIGHT']
        if (IS_HIDPI):
            sourceWidth = sourceWidth * 2
            sourceHeight = sourceHeight * 2
        SCREEN.blit(IMAGE_SPRITE,\
            (self.xPos * 2, self.yPos * 2, Cloud.config['WIDTH'], Cloud.config['HEIGHT']),\
            (self.spritePos['x'], self.spritePos['y'], sourceWidth, sourceHeight))

    # Update the cloud position.
    # @param {number} speed
    def update(self, speed):
        if not self.remove:
            self.xPos -= math.ceil(speed)
            self.draw()

        # Mark as removeable if no longer in the canvas.
        if not self.isVisible():
            self.remove = True

    # Check if the cloud is visible on the stage.
    # @return {boolean}
    def isVisible(self):
        return self.xPos + Cloud.config['WIDTH'] > 0


class Horizon:
    config = {
        'BG_CLOUD_SPEED': 0.2,
        'BUMPY_THRESHOLD': .3,
        'CLOUD_FREQUENCY': .5,
        'HORIZON_HEIGHT': 16,
        'MAX_CLOUDS': 6
    }
    def __init__(self, spritePos, dimensions, gapCoefficient):
        self.dimensions = dimensions
        self.gapCoefficient = gapCoefficient
        self.obstacles = []
        self.obstacleHistory = []
        self.horizonOffsets = [0, 0]
        self.cloudFrequency = Horizon.config['CLOUD_FREQUENCY']
        self.runningTime = 0
        self.spritePos = spritePos
        # Cloud
        self.clouds = []
        self.cloudSpeed = Horizon.config['BG_CLOUD_SPEED']

        # Horizon
        self.horizonLine = None
        self.init()

    # Initialise the horizon. Just add the line and a cloud. No obstacles.
    def init(self):
        self.addCloud()
        self.horizonLine = HorizonLine(self.spritePos['HORIZON'])

    # @param {number} deltaTime
    # @param {number} currentSpeed
    # @param {boolean} updateObstacles Used as an override to prevent
    #     the obstacles from being updated / added. self happens in the
    #     ease in section.
    def update(self, deltaTime, currentSpeed, updateObstacles):
        self.runningTime += deltaTime
        self.horizonLine.update(deltaTime, currentSpeed)
        self.updateClouds(deltaTime, currentSpeed)
        if (updateObstacles):
            self.updateObstacles(deltaTime, currentSpeed)

    def updateHorizonLine(self, deltaTime, currentSpeed):
        self.horizonLine.update(deltaTime, currentSpeed)

    # Update the cloud positions.
    # @param {number} deltaTime
    # @param {number} currentSpeed
    def updateClouds(self, deltaTime, speed):
        cloudSpeed = self.cloudSpeed / 1000.0 * deltaTime * speed
        numClouds = len(self.clouds)

        if numClouds <= 0: return

        for i in reversed(range(numClouds)):
            self.clouds[i].update(cloudSpeed)

        lastCloud = self.clouds[numClouds - 1]

        # Check for adding a new cloud.
        if numClouds < Horizon.config['MAX_CLOUDS'] and \
            (self.dimensions['WIDTH'] - lastCloud.xPos) > lastCloud.cloudGap and \
            self.cloudFrequency > random.random():
            self.addCloud()

        # Remove expired clouds.
        self.clouds = [c for c in self.clouds if not c.remove]

  
    # Update the obstacle positions.
    # @param {number} deltaTime
    # @param {number} currentSpeed
    def updateObstacles(self, deltaTime, currentSpeed):
        # Obstacles, move to Horizon layer.
        # print 'updatedObstacles', self.obstacles
        updatedObstacles = []
        for o in self.obstacles:
            o.update(deltaTime, currentSpeed)
            # Clean up existing obstacles.
            if not o.remove:
                updatedObstacles.append(o)
        self.obstacles = updatedObstacles

        if len(self.obstacles) > 0:
            lastObstacle = self.obstacles[len(self.obstacles) - 1]
            if (lastObstacle and not lastObstacle.followingObstacleCreated and \
                lastObstacle.isVisible() and \
                (lastObstacle.xPos + lastObstacle.width + lastObstacle.gap) < SCREENWIDTH):
                self.addNewObstacle(currentSpeed)
                lastObstacle.followingObstacleCreated = True
        else:
            # Create new obstacles.
            self.addNewObstacle(currentSpeed)
  
    # Add a new obstacle.
    # @param {number} currentSpeed
    def addNewObstacle(self, currentSpeed):
        obstacleTypeIndex = getRandomNum(0, len(Obstacle.types) - 1)
        obstacleType = Obstacle.types[obstacleTypeIndex]

        # Check for multiples of the same type of obstacle.
        # Also check obstacle is available at current speed.
        if (self.duplicateObstacleCheck(obstacleType['type']) or \
            currentSpeed < obstacleType['minSpeed']):
            self.addNewObstacle(currentSpeed)
        else:
            obstacleSpritePos = self.spritePos[obstacleType['type']]
            self.obstacles.append(Obstacle(obstacleTypeIndex, \
                obstacleSpritePos, self.dimensions, self.gapCoefficient, currentSpeed))

            self.obstacleHistory.append(obstacleType['type'])
            if len(self.obstacleHistory) > GameState.config['MAX_OBSTACLE_DUPLICATION']:
                self.obstacleHistory = self.obstacleHistory[-GameState.config['MAX_OBSTACLE_DUPLICATION']:]

  
    # Returns whether the previous two obstacles are the same as the next one.
    # Maximum duplication is set in config value MAX_OBSTACLE_DUPLICATION.
    # @return {boolean}
    def duplicateObstacleCheck(self, nextObstacleType):
        duplicateCount = 0
        for i in range(len(self.obstacleHistory)):
            if self.obstacleHistory[i] == nextObstacleType:
                duplicateCount += 1
            else:
                duplicateCount = 0
        return duplicateCount >= GameState.config['MAX_OBSTACLE_DUPLICATION']

  
    # Reset the horizon layer.
    # Remove existing obstacles and reposition the horizon line.
    def reset(self):
        self.obstacles = []
        self.horizonLine.reset()
  
    # Update the canvas width and scaling.
    # @param {number} width Canvas width.
    # @param {number} height Canvas height.
    def resize(self, width, height):
        self.canvas.width = width
        self.canvas.height = height

    # Add a new cloud to the horizon.
    def addCloud(self):
        self.clouds.append(Cloud(self.spritePos['CLOUD'], SCREENWIDTH))

def checkCrash(player, obstacles, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= HORIZONY - 1:
        return True
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])

        for obstacle in obstacles:
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(obstacle.xPos, obstacle.yPos, obstacle, PIPE_HEIGHT)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], PIPE_WIDTH, PIPE_HEIGHT)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return True

    return False

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def createAdjustedCollisionBox(box, adjustment):
  return CollisionBox(box.x + adjustment.x, box.y + adjustment.y,
                      box.width, box.height)

def boxCompare(tRexBox, obstacleBox):
    crashed = False;
    tRexBoxX = tRexBox.x;
    tRexBoxY = tRexBox.y;
    obstacleBoxX = obstacleBox.x;
    obstacleBoxY = obstacleBox.y;

    # Axis-Aligned Bounding Box method.
    if (tRexBox.x < obstacleBoxX + obstacleBox.width and\
        tRexBox.x + tRexBox.width > obstacleBoxX and\
        tRexBox.y < obstacleBox.y + obstacleBox.height and\
        tRexBox.height + tRexBox.y > obstacleBox.y):
        crashed = True;
    return crashed;


def checkForCollision(obstacle, tRex):
    obstacleBoxXPos = SCREENWIDTH + obstacle.xPos;

    # Adjustments are made to the bounding box as there is a 1 pixel white
    # border around the t-rex and obstacles.
    tRexBox = CollisionBox(tRex.xPos + 1, tRex.yPos + 1,\
                    tRex.config['WIDTH'] - 2, tRex.config['HEIGHT'] - 2);

    obstacleBox = CollisionBox(obstacle.xPos + 1, obstacle.yPos + 1,\
                    obstacle.typeConfig['width'] * obstacle.size - 2, obstacle.typeConfig['height'] - 2);

    # Debug outer box
    # if (opt_canvasCtx):
    #     drawCollisionBoxes(opt_canvasCtx, tRexBox, obstacleBox);

    # Simple outer bounds check.
    if (boxCompare(tRexBox, obstacleBox)):
        collisionBoxes = obstacle.collisionBoxes;
        if tRex.ducking:
            tRexCollisionBoxes = Trex.collisionBoxes['DUCKING']
        else:
            tRexCollisionBoxes = Trex.collisionBoxes['RUNNING'];

        # Detailed axis aligned box check.
        for t in range(len(tRexCollisionBoxes)):
            for i in range(len(collisionBoxes)):
                # Adjust the box to actual positions.
                adjTrexBox = createAdjustedCollisionBox(tRexCollisionBoxes[t], tRexBox);
                adjObstacleBox = createAdjustedCollisionBox(collisionBoxes[i], obstacleBox);
                crashed = boxCompare(adjTrexBox, adjObstacleBox);

                # Draw boxes for debug.
                # if (opt_canvasCtx):
                #     drawCollisionBoxes(opt_canvasCtx, adjTrexBox, adjObstacleBox);

                if (crashed):
                  return [adjTrexBox, adjObstacleBox];
    return False;

def main():
    game = GameState()
    firstStart = False
    while True:
        input_actions = [1, 0, 0]
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if not game.activated or game.crashed:
                    game.restart()
                input_actions[0] = 0
                input_actions[1] = 1
            if event.type == KEYDOWN and event.key == K_DOWN:
                input_actions[0] = 0
                input_actions[1] = 0
                input_actions[2] = 1
            if event.type == KEYUP and event.key == K_DOWN:
                game.tRex.speedDrop = False;
                game.tRex.setDuck(False)
        if not game.crashed:
            game.frame_step(input_actions)

if __name__ == '__main__':
    main()


