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
import copy
import cv2

NumObstacle = 2
MinNearTime = 0.4
ACTIONS = 2
NumElement = 3 # x, h, w
SMAPLE_FPS = 30.0
class NewGame(object):
    def __init__(self, img_processor, start_time, nn, game_state):
        self.img_processor = img_processor
        self.start_time = start_time
        self.nn = nn
        self.game_state = game_state
        do_nothing = zeros(ACTIONS)
        do_nothing[1] = 1
        self.action = do_nothing
        self.image = None
        self.LastParams = [1 for i in range(NumObstacle*NumElement)]
        self.NumCrash = 0
        self.previousValidJump = False

    def StartGame(self):
        def Update(SMAPLE_FPS):
            x_t, r_0, terminal = self.game_state.frame_step(self.action)
            ret, binary = cv2.threshold(x_t, 230, 255, cv2.THRESH_BINARY)
            cv2.imwrite('log/'+ str(time.time()) + '.png', binary)
            self.img_processor.detectObjects(x_t, SMAPLE_FPS)
            cl, bl = self.img_processor.getObstacles()
            cl += bl
            cacti_list = sorted(cl,key=lambda a:a.x)

            params = []
            for _ in range(NumObstacle):
                if len(cacti_list) < 1+_ :
                    params += [30000,0,0]
                else:
                    tmp = []
                    tmp.append(cacti_list[_].x)#- self.img_processor.tRex.x - self.img_processor.tRex.w)
                    #tmp.append(cacti_list[_].y)#- self.img_processor.tRex.y)
                    tmp.append(cacti_list[_].w)
                    tmp.append(cacti_list[_].h)
                    '''if self.img_processor.tRex == None:
                        tmp.append(1)
                    else:
                        tmp.append(abs(self.img_processor.tRex.speed))
                    tmp.append(abs(cacti_list[_].speed))'''
                    params += tmp

            if terminal:
                #print 'fuckfuckfuckfucku'

                self.NumCrash += 1
                if self.NumCrash % 10 == 0:
                    model = self.nn.model
                    json_string = model.to_json()
                    open('./mlp/my_model_architecture'+str(self.NumCrash)+'.json', 'w').write(json_string)
                    model.save_weights('./mlp/my_model_weights'+str(self.NumCrash)+'.h5', overwrite=True)
                print self.NumCrash
                print 'neg and pos', self.nn.NumNeg, self.nn.NumPos
                '''if self.LastParams[4] != 0:
                    deltaFactor = (self.LastParams[1] / self.LastParams[4] * self.LastParams[5])
                else:
                    deltaFactor = 0.5 * self.LastParams[2]'''
                deltaFactor = 0.5 * self.LastParams[1]
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
                    tmp = copy.deepcopy(params)
                    for i in range(len(tmp)/NumElement):
                        #tmp[NumElement*i] += 0.5*tmp[2]
                        tmp[NumElement*i] += 0.5*tmp[1]
                    self.nn.TrainModel(array([tmp]), array([[0,1]]))
                    print tmp
                    print 'hit when not jump'
                    #pass
                self.LastParams = [1 for i in range(NumObstacle*NumElement)]

            else:

                if len(cacti_list) == 0 or cacti_list[0].speed == 0:
                    do_nothing = zeros(ACTIONS)
                    do_nothing[0] = 1
                    self.action = do_nothing
                    return

                category, confidence = self.nn.TestModel(array([params]))
                #category = [0]
                #print params
                #print 'category', category
                #print params[0], category[0]
                if (category[0] == 1):#jump if network is really confident
                    '''if params[0]/params[5] > MinNearTime:
                        return'''
                    if params[0] > 400:
                        if self.previousValidJump:
                            self.nn.TrainModel(array([params]), array([[1,0]]))
                            self.previousValidJump = False
                        do_nothing = zeros(ACTIONS)
                        do_nothing[0] = 1
                        self.action = do_nothing
                        return
                    if not self.img_processor.jumping:
                        #if self.LastParams != [1 for i in range(NumObstacle*NumElement)]:
                        if True:
                            self.nn.TrainModel(array([self.LastParams]), array([[0,1]]))
                            self.previousValidJump = True
                            tmp = self.LastParams
                            #delta_tmp = tmp[2]
                            delta_tmp = tmp[1]
                            for i in range(len(tmp)/NumElement):
                                tmp[NumElement*i] += delta_tmp
                            self.nn.TrainModel(array([tmp]), array([[1,0]]))
                        jump = zeros(ACTIONS)
                        jump[1] = 1
                        self.LastParams = params
                        self.action = jump

                else:
                    do_nothing = zeros(ACTIONS)
                    do_nothing[0] = 1
                    self.action = do_nothing


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