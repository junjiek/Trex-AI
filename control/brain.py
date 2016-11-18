import os
from image_processor import imageProcessor
from controller import TrexGameController
import time
from mlp import *

class NewGame(object):
    def __init__(self, controller, img_processor, start_time, nn):
        self.controller = controller
        self.img_processor = img_processor
        self.start_time = start_time
        self.LastParams = [1,1,1]
        self.LastRealParams = [1,1,1]
        self.nn = nn
    def StartGame(self):
        def Update():
            learningRate = 0.03
            birds, cacti = self.img_processor.getObstacles()
            trex = self.img_processor.tRex
            if self.controller.getCrashed():
                if self.LastParams[0] == 0:
                    print 'fuck'
                    self.LastParams = [1,1,1]
                    self.LastRealParams = [1,1,1]
                    return
                deltaFactor = (self.LastParams[0] * 0.1)
                print trex
                print img_processor
                if (self.img_processor.jumping):
                    #self.nn.TrainModel(array([self.LastParams]), array([[0,1]]))
                    #perceptron.propagate(learningRate, [0, 1]) #you should remain on ground

                    self.LastRealParams[0] = self.LastRealParams[0] + deltaFactor;
                    self.nn.TrainModel(array([self.LastRealParams]), array([[1,0]]))
                    print 'fuck1'
                    #perceptron.propagate(learningRate, [1, 0])#you should have jumped

                elif (self.img_processor.dropping):
                    #perceptron.activate(self.LastParams)
                    #umm, we hit it on face :ouch: :ouch:
                    #try to jump from a distance
                    self.nn.TrainModel(array([self.LastParams]), array([[0,1]]))
                    print 'fuck2'
                    self.LastParams[0] = self.LastParams[0] - deltaFactor
                    self.nn.TrainModel(array([self.LastParams]), array([[1,0]]))
                    print 'fuck3'
                    #perceptron.propagate(learningRate, [1, 0])
                else:
                    self.LastParams[0] = self.LastParams[0] + deltaFactor
                    self.nn.TrainModel(array([self.LastParams]), array([[1,0]]))
                    print 'fuck4'
                #self.controller.restart()

            else:
                self.img_processor.detectObjects(self.controller.getImage(), delta_time)
                tmp = [each for each in (birds, cacti) if len(each) != 0]
                if tmp == []:
                    self.nn.TrainModel(array([self.LastParams]), array([[0,1]]))
                    print 'fuck5'
                    return
                NearestObstacle = min(tmp)
                params = []
                if NearestObstacle == None:
                    return
                params.append(NearestObstacle[0].x - trex.x)#position
                params.append(NearestObstacle[0].h)#size
                params.append(round((NearestObstacle[0].speed)))#speed with multiply bias
                category, confidence = self.nn.TestModel(array([params]))
                #confidence = output[0] - output[1] - 0.01 #weight bias
                #category = [0]
                if (category[0] == 0):#jump if network is really confident
                    #Jump jump jump :D !
                    if (not self.img_processor.jumping):
                        if self.LastParams != [1,1,1]:
                            self.nn.TrainModel(array([self.LastParams]), array([[0,1]]))
                            print 'fuck6'
                        self.controller.jump()
                        self.LastParams = params

                else:
                    if (self.img_processor.jumping):
                        self.controller.duck()
                        self.LastParams = params#last move activation
                self.LastRealParams = params#last frame activation
            #well well, our human mind can retain image upto 25ms i.e. 40fps
            #obviously no brain is ideal so :p 20ms :D !

        while True:
            if self.controller.hasStart():
                if start_time is not None:
                    delta_time = time.time() - self.start_time
                else:
                    delta_time = 0
                Update()
            time.sleep(0.02)



if __name__ == '__main__':
    game_path = 'file://' + os.path.abspath(os.path.join(os.getcwd(), '..')) + '/game/index.html'
    controller = TrexGameController(game_path)
    img_processor = imageProcessor()
    start_time = time.time()
    mlp = MLP()
    mlp.BuildModel()
    #mlp = None
    ng = NewGame(controller, img_processor, start_time, mlp)
    ng.StartGame()