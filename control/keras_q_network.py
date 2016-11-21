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

        model.add(Convolution2D(32,8,8,subsample=(4,4),border_mode='same', input_shape=(4, 80, 80), bias=True, dim_ordering='th'))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))


        model.add(Convolution2D(64,4,4,subsample=(2,2),border_mode='same', input_shape=(32, 10, 10), bias=True,dim_ordering='th'))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2),border_mode='same'))

        model.add(Convolution2D(64,3,3,subsample=(1,1), border_mode='same', input_shape=(64, 3, 3), bias=True, dim_ordering='th'))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2),border_mode='same'))
        # reshape
        model.add(Flatten())
        # ReLU
        model.add(Activation('relu'))
        # fc
        model.add(Dense(2, input_dim=256))

        sgd = SGD(lr=0.05, decay=1e-6, momentum=0.9, nesterov=True)
        model.compile(loss='mean_squared_error', optimizer=sgd, class_mode='categorical')
        json_string = model.to_json()
        open('data/my_model_architecture_q_cnn.json','w').write(json_string)
        model.save_weights('data.my_model_weights_q_cnn.h5',overwrite=True)
        self.model = model
        return self.model

    def TrainModel(self, X_train, Y_train):
        self.model.fit(X_train, Y_train, nb_epoch=5, verbose=0)

    def TestModel(self, X_test):
        classes = self.model.predict_classes(X_test, verbose=0)
        Q = self.model.predict_proba(X_test, verbose=0)
        return classes, Q

if __name__=='__main__':
    deep_q_nn = DeepQNN()
    deep_q_nn.BuildModel()
    X_test = zeros((1,4,80,80))
    X_test[0,2,3,2] = 21
    print deep_q_nn.TestModel(X_test)
    X_train = zeros((1,4,80,80))
    X_train[0,1,1,1] = 10
    X_train[0,1,8,17]=23.3
    deep_q_nn.TrainModel(X_train,array([[1,0]]))
    print deep_q_nn.TestModel(X_train)
    print deep_q_nn.TestModel(X_test)

