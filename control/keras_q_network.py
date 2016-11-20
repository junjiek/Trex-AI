from keras.models import Sequential
from keras.optimizers import SGD
from keras.models import model_from_json
from keras.layers import Dense, Activation, Flatten
from keras.layers.convolutional import Convolution2D
from keras.layers.pooling import MaxPooling2D
from numpy import *

class DeepQNN(object):
    def __int__(self):
        self.model = None

    def BuildModel(self):
        model = Sequential()
        # conv1
        model.add(Convolution2D(32,8,8,subsample=(4,4),border_mode='same', input_shape=(4, 80, 80), bias=True))
        # maxpool1
        model.add(MaxPooling2D(pool_size=(2, 2)))
        # conv2
        model.add(Convolution2D(64,4,4,subsample=(2,2),border_mode='same', input_shape=(32, 10, 10), bias=True))
        # maxpool2
        model.add(MaxPooling2D(pool_size=(2, 2),border_mode='valid'))
        # conv3
        model.add(Convolution2D(64,3,3,border_mode='same', input_shape=(64, 3, 3), bias=True))
        # maxpool3
        model.add(MaxPooling2D(pool_size=(2, 2),border_mode='valid'))
        # reshape
        model.add(Flatten())
        # ReLU
        model.add(Activation('relu'))
        # fc
        model.add(Dense(2, input_dim=256))

        sgd = SGD(lr=0.05, decay=1e-6, momentum=0.9, nesterov=True)
        model.compile(loss='ninary_crossentropy', optimizer=sgd, class_mode='categorical')
        self.model = model
        return self.model

    def TrainModel(self, X_train, Y_train):
        self.model.fit(X_train, Y_train, nb_epoch=5, verbose=0)

    def TestModel(self, X_test):
        classes = self.model.predict_classes(X_test, verbose=0)
        proba = self.model.predict_proba(X_test, verbose=0)

if __name__=='__main__':
    deep_q_nn = DeepQNN()
    deep_q_nn.BuildModel()
