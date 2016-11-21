import numpy as np
import sys
import random
import pygame
import trex_utils
import pygame.surfarray as surfarray
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

class Trex:
    def __init__(self):
        self.config = {
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
        self.xPos = self.config['START_X_POS']
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
        self.minJumpHeight = self.groundYPos - self.config['MIN_JUMP_HEIGHT']
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
            self.timer = 0;
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
    #     self.blinkDelay = ceil(random.random() * self.config['BLINK_TIMING'])

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
            self.jumpVelocity = self.config['INITIAL_JUMP_VELOCITY'] - (speed / 10)
            self.jumping = True
            self.reachedMinHeight = False
            self.speedDrop = False

    # Jump is complete, falling down.
    def endJump(self):
        if self.reachedMinHeight and self.jumpVelocity < self.config['DROP_VELOCITY']:
            self.jumpVelocity = self.config['DROP_VELOCITY']

    # Update frame for a jump.
    # @param {number} deltaTime
    # @param {number} speed
    def updateJump(self, deltaTime):
        framesElapsed = deltaTime / self.msPerFrame
        # print self.yPos, self.jumpVelocity, self.reachedMinHeight
        # Speed drop makes Trex fall faster.
        if (self.speedDrop):
            self.yPos += round(self.jumpVelocity *
            self.config['SPEED_DROP_COEFFICIENT'] * framesElapsed)
        else:
            self.yPos += round(self.jumpVelocity * framesElapsed)
            self.jumpVelocity += self.config['GRAVITY'] * framesElapsed

        # Minimum height has been reached.
        if (self.yPos < self.minJumpHeight or self.speedDrop):
            self.reachedMinHeight = True
        # Reached max height
        if (self.yPos < self.config['MAX_JUMP_HEIGHT'] or self.speedDrop):
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

class GameState:
    def __init__(self):
        self.config = {
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
            'MOBILE_SPEED_COEFFICIENT': 1.2,
            'SPEED': 6,
            'SPEED_DROP_COEFFICIENT': 3
        }
        self.score = self.playerIndex = self.loopIter = 0
        self.tRex = Trex()
        self.obstacles = []
        self.runningTime = 0
        self.activated = True
        self.crashed = False
        self.distanceRan = 0

        self.msPerFrame = 1000 / FPS
        self.currentSpeed = self.config['SPEED']
        self.started = False

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

        # # playerIndex basex change
        # if (self.loopIter + 1) % 3 == 0:
        #     self.tRex.playerIndex = next(PLAYER_INDEX_GEN)
        # self.loopIter = (self.loopIter + 1) % 30
        # self.basex = -((-self.basex + 100) % self.baseShift)

        deltaTime = 0
        # if self.started:
        deltaTime = FPSCLOCK.get_time()
        if (self.tRex.jumping):
            self.tRex.updateJump(deltaTime)

        self.runningTime += deltaTime
        hasObstacles = self.runningTime > self.config['CLEAR_TIME']
        # The horizon doesn't move until the intro is over.

        # self.horizon.update(deltaTime, self.currentSpeed, hasObstacles)

        # Check for collisions.
        # collision = hasObstacles and checkForCollision(self.horizon.obstacles[0], self.tRex)

        # if not collision:
        #     self.distanceRan += self.currentSpeed * deltaTime / self.msPerFrame
        #     if (self.currentSpeed < self.config['MAX_SPEED']):
        #         self.currentSpeed += self.config['ACCELERATION']
        # else:
        #     self.gameOver()

        if not self.crashed:
            self.tRex.update(deltaTime, self.tRex.status)

        # draw sprites
        

        # for uPipe, lPipe in zip(self.obstacles, self.lowerPipes):
        #     SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
        #     SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['horizons'][0], (0, HORIZONY))
        SCREEN.blit(IMAGES['horizons'][1], (IMAGES['horizons'][0].get_width(), HORIZONY))
        # print score so player overlaps the score
        # showScore(self.score)
        

        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        #print self.obstacles[0]['y'] + PIPE_HEIGHT - int(HORIZONY * 0.2)
        return image_data, reward, terminal

# def getRandomObstacle():
    """returns a randomly generated pipe"""



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

        for uPipe, lPipe in zip(obstacles, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], PIPE_WIDTH, PIPE_HEIGHT)
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
    while True:
        input_actions = [1, 0]
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # game.started = True
                input_actions[0] = 0
                input_actions[1] = 1

        game.frame_step(input_actions)

if __name__ == '__main__':
    main()


