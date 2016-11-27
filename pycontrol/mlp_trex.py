import os
import time
import sys
from mlp import *
from image_processor import imageProcessor
sys.path.append("../pygame/")
sys.path.append('../control/')
import wrapped_trex as game
from controller import TrexGameController
from numpy import *

NumObstacle = 3
MinNearTime = 0.3
ACTIONS = 2
NumElement = 6
class NewGame(object):
    def __init__(self, img_processor, start_time, nn, game_state):
        self.img_processor = img_processor
        self.start_time = start_time
        self.nn = nn
        self.game_state = game_state
        do_nothing = zeros(ACTIONS)
        do_nothing[0] = 1
        x_t, r_0, terminal = self.game_state.frame_step(do_nothing)
        self.image = x_t
        self.terminal = terminal
        self.LastParams = [1 for i in range(NumObstacle*NumElement)]
        self.WaitonCrash = False
        self.NumJump = 0
    def StartGame(self):
        def Update(delta_time):
            self.img_processor.detectObjects(self.image, delta_time)
            cacti_list, birds_list = self.img_processor.getObstacles()
            if len(cacti_list) == 0 or cacti_list[0].speed == 0:
                do_nothing = zeros(ACTIONS)
                do_nothing[0] = 1
                x_t, r_0, terminal = self.game_state.frame_step(do_nothing)
                self.image = x_t
                self.terminal = terminal
                return
            if self.terminal:
                print 'fuckkckckkckckckckckckckckkckckckck'
                #print 'Num of Jump', self.NumJump
                if self.LastParams[4] != 0:
                    deltaFactor = (self.LastParams[1] / self.LastParams[4] * self.LastParams[5])
                else:
                    deltaFactor = self.LastParams[2]
                if (self.img_processor.jumping):
                    print 'when jump'
                    for i in range(len(self.LastParams)/NumElement):
                        self.LastParams[NumElement*i] += deltaFactor
                    self.nn.TrainModel(array([self.LastParams]), array([[0,1]]))
                    #print 'hit face ------------------jump'
                    for i in range(len(self.LastParams)/NumElement):
                        self.LastParams[NumElement*i] += deltaFactor
                    self.nn.TrainModel(array([self.LastParams]), array([[1,0]]))
                    #print 'hit face ------------------stay'
                    #perceptron.propagate(learningRate, [1, 0])#you should have jumped

                elif (self.img_processor.dropping):
                    print 'when drop'
                    #deltaFactor = self.LastParams[1]
                    self.nn.TrainModel(array([self.LastParams]), array([[1,0]]))
                    #print 'hit feet ------------------ stay'
                    for i in range(len(self.LastParams)/NumElement):
                        self.LastParams[NumElement*i] -= deltaFactor
                    self.nn.TrainModel(array([self.LastParams]), array([[0,1]]))
                    #print 'hit feet ------------------- jump'
                    #perceptron.propagate(learningRate, [1, 0])
                else:
                    self.nn.TrainModel(array([self.LastParams]), array([[0,1]]))
                    print 'hit when not jump'
                    #pass
                self.NumJump = 0

            else:
                params = []
                for _ in range(NumObstacle):
                    if len(cacti_list) < 1+_ or cacti_list[_] == None:
                        params += [1,1,1,1,1,1]
                    else:
                        tmp = []
                        tmp.append(cacti_list[_].x)#- self.img_processor.tRex.x - self.img_processor.tRex.w)
                        tmp.append(cacti_list[_].y)#- self.img_processor.tRex.y)
                        tmp.append(cacti_list[_].w)
                        tmp.append(cacti_list[_].h)
                        if self.img_processor.tRex == None:
                            tmp.append(1)
                        else:
                            tmp.append(self.img_processor.tRex.speed)
                        tmp.append(cacti_list[_].speed)
                        params += tmp
                category, confidence = self.nn.TestModel(array([params]))
                #category = [0]
                #print params
                #print 'category', category
                if (category[0] == 1):#jump if network is really confident
                    #Jump jump jump :D !
                    '''if params[5] == 0:
                        print params
                        return'''
                    #print params[0]/params[5]
                    if params[0]/params[5] > MinNearTime:
                        return
                    if not self.img_processor.jumping:
                        if self.LastParams != [1 for i in range(NumObstacle*NumElement)]:
                            self.nn.TrainModel(array([self.LastParams]), array([[0,1]]))
                            self.NumJump += 1
                            #print 'previous jump succeed'
                        jump = zeros(ACTIONS)
                        jump[1] = 1
                        x_t, r_0, terminal = self.game_state.frame_step(jump)
                        self.image = x_t
                        self.terminal = terminal
                        self.LastParams = params
                else:
                    do_nothing = zeros(ACTIONS)
                    do_nothing[0] = 1
                    x_t, r_0, terminal = self.game_state.frame_step(do_nothing)
                    self.terminal = terminal
                    self.image = x_t
                '''else:
                    if (self.controller.isJumping()):
                        self.controller.duck()
                        self.LastParams = params#last move activation'''


        while True:
            delta_time = time.time() - self.start_time
            self.start_time  = time.time()
            Update(delta_time)
            #time.sleep(0.01)



if __name__ == '__main__':
    game_state = game.GameState()
    img_processor = imageProcessor()
    start_time = time.time()
    mlp = MLP()
    mlp.BuildModel()
    #mlp = None
    ng = NewGame(img_processor, start_time, mlp, game_state)
    ng.StartGame()