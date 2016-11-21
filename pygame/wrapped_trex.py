import numpy as np
import sys
import random
import pygame
import trex_utils
import pygame.surfarray as surfarray
import math
from pygame.locals import *
from itertools import cycle

FPS = 60
SCREENWIDTH  = 1200
SCREENHEIGHT = 300

pygame.init()
FPSCLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Trex')

IMAGES, SOUNDS, HITMASKS = trex_utils.load()
PIPEGAPSIZE = 100 # gap between upper and lower part of pipe
HORIZONY = 254

PLAYER_WIDTH = IMAGES['player'][0].get_width()
PLAYER_HEIGHT = IMAGES['player'][0].get_height()
LARGE_CACTUS_WIDTH = IMAGES['large_cactci'][0].get_width()
LARGE_CACTUS_HEIGHT = IMAGES['large_cactci'][0].get_height()
SMALL_CACTUS_WIDTH = IMAGES['small_cactci'][0].get_width()
SMALL_CACTUS_HEIGHT = IMAGES['small_cactci'][0].get_height()

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
        'MIN_JUMP_HEIGHT': 35 * 2,
        'SPEED': 6,
        'SPEED_DROP_COEFFICIENT': 3
    }
    def __init__(self):
        self.obstacles = []
        self.runningTime = 0
        self.distanceRan = 0
        self.dimensions = {
            'WIDTH': SCREENWIDTH,
            'HEIGHT': SCREENHEIGHT,
        }
        self.msPerFrame = 1000 / FPS
        self.currentSpeed = GameState.config['SPEED']
        self.highestScore = 0
        self.started = False
        self.activated = False
        self.crashed = False
        self.paused = False
        self.playCount = 0
        self.horizon = Horizon(self.dimensions, GameState.config['GAP_COEFFICIENT'])
        self.tRex = Trex()
        # Distance meter
        self.distanceMeter = DistanceMeter(self.dimensions['WIDTH'])
        self.adjustDimensions()

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

        deltaTime = FPSCLOCK.get_time()
        if self.activated:
            if (self.tRex.jumping):
                self.tRex.updateJump(deltaTime)

            self.runningTime += deltaTime
            hasObstacles = self.runningTime > GameState.config['CLEAR_TIME']
            # First jump triggers the intro.
            # if (self.tRex.jumpCount == 1 and not self.playingIntro):
            #     self.playIntro()
            # The horizon doesn't move until the intro is over.
            # The horizon doesn't move until the intro is over.
            # if (self.playingIntro):
            #     self.horizon.update(0, self.currentSpeed, hasObstacles)
            # else:
                # deltaTime = !self.started ? 0 : deltaTime
            self.horizon.update(deltaTime, self.currentSpeed, hasObstacles)
            # self.horizon.update(deltaTime, self.currentSpeed, hasObstacles)

            # Check for collisions.
            # collision = hasObstacles and checkForCollision(self.horizon.obstacles[0], self.tRex)
            collision = False
            if not collision:
                self.distanceRan += self.currentSpeed * deltaTime / self.msPerFrame
                if (self.currentSpeed < GameState.config['MAX_SPEED']):
                    self.currentSpeed += GameState.config['ACCELERATION']
            else:
                self.gameOver()

            self.distanceMeter.update(deltaTime, math.ceil(self.distanceRan))

        if not self.crashed:
            self.tRex.update(deltaTime, self.tRex.status)

        # draw sprites
        
        # print score so player overlaps the score
        # showScore(self.score)
        

        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        #print self.obstacles[0]['y'] + PIPE_HEIGHT - int(HORIZONY * 0.2)
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
            self.tRex.draw()

        # Game over panel.
        if (self.crashed and self.gameOverPanel):
            self.gameOverPanel.updateDimensions(self.dimensions['WIDTH'])
            self.gameOverPanel.draw()

    # Game over state.
    def gameOver(self):
        self.stop()
        self.crashed = True
        self.distanceMeter.acheivement = False
        self.tRex.update(100, 'CRASHED')
        # Game over panel.
        if self.gameOverPanel is None:
            self.gameOverPanel = GameOverPanel(self.spriteDef.TEXT_SPRITE, self.spriteDef.RESTART, self.dimensions)
        else:
            self.gameOverPanel.draw()

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
        self.distanceRan = 0
        self.currentSpeed = GameState.config['SPEED']
        self.distanceMeter.reset(self.highestScore)
        self.horizon.reset()
        self.tRex.reset()


class Trex:
    config = {
        'DROP_VELOCITY': -5,
        'GRAVITY': 0.6,
        'HEIGHT': 47,
        'HEIGHT_DUCK': 25,
        'INITIAL_JUMP_VELOCITY': -12,
        'INTRO_DURATION': 1500,
        'MAX_JUMP_HEIGHT': 30,
        'MIN_JUMP_HEIGHT': 30,
        'SPEED_DROP_COEFFICIENT': 3,
        'START_X_POS': 50,
        'WIDTH': 44,
        'WIDTH_DUCK': 59
    }
    def __init__(self):
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
        self.groundYPos = 180
        self.yPos = self.groundYPos
        self.minJumpHeight = self.groundYPos - Trex.config['MIN_JUMP_HEIGHT']
        self.msPerFrame = 1000 / 3
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
                self.msPerFrame = 1000 / 3
                self.currentAnimFrames = [0, 1]
            elif self.status == 'RUNNING':
                self.msPerFrame = 1000 / 12
                self.currentAnimFrames = [2, 3]
            elif self.status == 'CRASHED':
                self.msPerFrame = 1000 / 60
                self.currentAnimFrames = [4, 5]
            elif self.status == 'JUMPING':
                self.msPerFrame = 1000 / 60
                self.currentAnimFrames = [0]
            elif self.status == 'DUCKING':
                self.msPerFrame = 1000 / 8
                self.currentAnimFrames = [6, 7]

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
        self.draw()

    def draw(self):
        # Ducking.
        if (self.ducking and self.status != 'CRASHED'):
            SCREEN.blit(IMAGES['player'][self.currentAnimFrames[self.currentFrame]], (self.xPos, self.yPos))
        else:
            # Crashed whilst ducking. Trex is standing up so needs adjustment.
            if (self.ducking and self.status == 'CRASHED'):
                self.xPos+=1
            # Standing / running
        SCREEN.blit(IMAGES['player'][self.currentAnimFrames[self.currentFrame]], (self.xPos, self.yPos))

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
            self.jumpVelocity = Trex.config['INITIAL_JUMP_VELOCITY'] - (speed / 10)
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

        self.update(deltaTime, self.status)

    # Set the speed drop. Immediately cancels the current jump.
    def setSpeedDrop(self, ):
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
        'name': 'small_cactci',
        'width': 17 * 2,
        'height': 35 * 2,
        'spriteNum': 6,
        'yPos': 105 * 2,
        'multipleSpeed': 4,
        'minGap': 120,
        'minSpeed': 0,
    },{
        'name': 'large_cactci',
        'width': 25 * 2,
        'height': 50 * 2,
        'spriteNum': 6,
        'yPos': 90 * 2,
        'multipleSpeed': 7,
        'minGap': 120,
        'minSpeed': 0,
    },{
        'name': 'birds',
        'width': 46 * 2,
        'height': 40 * 2,
        'spriteNum': 1,
        'yPos': [ 100 * 2, 75 * 2, 50 * 2 ],
        'multipleSpeed': 999,
        'minSpeed': 0,
        'minGap': 150,
        'numFrames': 2,
        'frameRate': 1000/6,
        'speedOffset': .8
    }]
    MAX_GAP_COEFFICIENT = 1.5
    MAX_OBSTACLE_LENGTH = 3
    def __init__(self, typeIdx, spritePos, dimensions, gapCoefficient, speed):
        self.typeConfig = Obstacle.types[typeIdx]
        self.spritePos = spritePos
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
        self.followingObstacleCreated = False
        # For animated obstacles.
        self.currentFrame = 0
        self.timer = 0
        self.init(speed)
  
    # Initialise the DOM for the obstacle.
    # @param {number} speed
    def init(self, speed):
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

        # For obstacles that go at a different speed from the horizon.
        if 'speedOffset' in self.typeConfig:
            if random.random() > 0.5:
                self.speedOffset = self.typeConfig['speedOffset']
            else:
                self.speedOffset = -self.typeConfig['speedOffset']

        self.gap = self.getGap(self.gapCoefficient, speed)

    # Draw and crop based on size.
    def draw(self):
        SCREEN.blit(IMAGES[self.typeConfig['name']][self.spritePos + self.currentFrame], (self.xPos, self.yPos))

    # Obstacle frame update.
    # @param {number} deltaTime
    # @param {number} speed
    def update(self, deltaTime, speed):
        if self.remove: return
        if 'speedOffset' in self.typeConfig:
            speed += self.speedOffset
        self.xPos -= math.floor((speed * FPS / 1000) * deltaTime)

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

        textTargetX = Math.round(centerX - (dimensions.TEXT_WIDTH / 2))
        textTargetY = Math.round((self.canvasDimensions.HEIGHT - 25) / 3)
        textTargetWidth = dimensions.TEXT_WIDTH
        textTargetHeight = dimensions.TEXT_HEIGHT

        restartSourceWidth = dimensions.RESTART_WIDTH
        restartSourceHeight = dimensions.RESTART_HEIGHT
        restartTargetX = centerX - (dimensions.RESTART_WIDTH / 2)
        restartTargetY = self.canvasDimensions.HEIGHT / 2

        textSourceY *= 2
        textSourceX *= 2
        textSourceWidth *= 2
        textSourceHeight *= 2
        restartSourceWidth *= 2
        restartSourceHeight *= 2

        textSourceX += self.textImgPos.x
        textSourceY += self.textImgPos.y

        # Game over text from sprite.
        SCREEN.blit(IMAGES['game_over'][0], (textTargetX, textTargetY))
        # Restart button.
        SCREEN.blit(IMAGES['game_over'][1], (restartTargetX, restartTargetY))

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
        'WIDTH': 10 * 2,
        'HEIGHT': 13 * 2,
        'DEST_WIDTH': 11 * 2
    }
    yPos = [0, 13, 27, 40, 53, 67, 80, 93, 107, 120]
    def __init__(self, canvasWidth):
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

        targetX = digitPos * DistanceMeter.dimensions['DEST_WIDTH']
        targetY = self.y
        targetWidth = DistanceMeter.dimensions['WIDTH']
        targetHeight = DistanceMeter.dimensions['HEIGHT']

        # For high DPI we 2x source values.
        sourceWidth *= 2
        sourceHeight *= 2
        if (opt_highScore):
            # Left of the current score.
            highScoreX = self.x - (self.maxScoreUnits * 2) * DistanceMeter.dimensions['WIDTH']
            SCREEN.blit(IMAGES['numbers'][value], (targetX + highScoreX, targetY + self.y))
        else:
            SCREEN.blit(IMAGES['numbers'][value], (targetX + self.x, targetY + self.y))

    def showScore(score):
        """displays score in center of screen"""
        scoreDigits = [int(x) for x in list(str(score))]
        totalWidth = 0 # total width of all numbers to be printed

        for digit in scoreDigits:
            totalWidth += IMAGES['numbers'][digit].get_width()

        Xoffset = (SCREENWIDTH - totalWidth) / 2

        for digit in scoreDigits:
            SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
            Xoffset += IMAGES['numbers'][digit].get_width()

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
    def __init__(self):
        self.dimensions = {
            'WIDTH': SCREENWIDTH,
            'HEIGHT': 12 * 2,
            'YPOS': 127
        }
        self.bumpThreshold = 0.5
        self.xPos = [0, self.dimensions['WIDTH']]
        self.yPos = 127 * 2
        self.draw()

    def draw(self):
        SCREEN.blit(IMAGES['horizons'][0], (self.xPos[0], self.yPos))
        SCREEN.blit(IMAGES['horizons'][1], (self.xPos[1], self.yPos))

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

        # if (self.xPos[line1] <= -self.dimensions['WIDTH']):
        #     self.xPos[line1] += self.dimensions['WIDTH'] * 2
        #     self.xPos[line2] = self.xPos[line1] - self.dimensions['WIDTH']
        #     self.sourceXPos[line1] = self.getRandomType() + self.spritePos.x

    # Update the horizon line.
    # @param {number} deltaTime
    # @param {number} speed
    def update(self, deltaTime, speed):
        increment = math.floor(speed * (FPS / 1000) * deltaTime)
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
    def __init__(self, containerWidth):
        self.containerWidth = containerWidth
        self.xPos = containerWidth
        self.yPos = 0
        self.remove = False
        self.cloudGap = getRandomNum(Cloud.config['MIN_CLOUD_GAP'], Cloud.config['MAX_CLOUD_GAP'])
        self.init()

    def init(self):
        self.yPos = getRandomNum(Cloud.config['MAX_SKY_LEVEL'], Cloud.config['MIN_SKY_LEVEL'])
        self.draw()

    # Draw the cloud.
    def draw(self):
        SCREEN.blit(IMAGES['cloud'], (self.xPos, self.yPos))

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
    def __init__(self, dimensions, gapCoefficient):
        self.dimensions = dimensions
        self.gapCoefficient = gapCoefficient
        self.obstacles = []
        self.obstacleHistory = []
        self.horizonOffsets = [0, 0]
        self.cloudFrequency = Horizon.config['CLOUD_FREQUENCY']
        self.runningTime = 0
        # Cloud
        self.clouds = []
        self.cloudSpeed = Horizon.config['BG_CLOUD_SPEED']

        # Horizon
        self.horizonLine = None
        self.init()

    # Initialise the horizon. Just add the line and a cloud. No obstacles.
    def init(self):
        self.addCloud()
        self.horizonLine = HorizonLine()

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

  
    # Update the cloud positions.
    # @param {number} deltaTime
    # @param {number} currentSpeed
    def updateClouds(self, deltaTime, speed):
        cloudSpeed = self.cloudSpeed / 1000 * deltaTime * speed
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
        print 'addNewObstacle'
        obstacleTypeIndex = getRandomNum(0, len(Obstacle.types) - 1)
        obstacleType = Obstacle.types[obstacleTypeIndex]

        # Check for multiples of the same type of obstacle.
        # Also check obstacle is available at current speed.
        if (self.duplicateObstacleCheck(obstacleType['name']) or \
            currentSpeed < obstacleType['minSpeed']):
            self.addNewObstacle(currentSpeed)
        else:
            obstacleSpritePos = random.randint(0, obstacleType['spriteNum'] - 1)
            self.obstacles.append(Obstacle(obstacleTypeIndex, \
                obstacleSpritePos, self.dimensions, self.gapCoefficient, currentSpeed))

            self.obstacleHistory.append(obstacleType['name'])
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
        self.clouds.append(Cloud(SCREENWIDTH))


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


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

def main():
    game = GameState()
    firstStart = False
    while True:
        input_actions = [1, 0]
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if not game.activated or game.crashed:
                    game.restart()
                input_actions[0] = 0
                input_actions[1] = 1

        game.frame_step(input_actions)

if __name__ == '__main__':
    main()


