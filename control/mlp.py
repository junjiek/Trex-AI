from keras.models import Sequential
from keras.optimizers import SGD, Adadelta, Adagrad
from keras.models import model_from_json
from keras.layers import Dense, Activation
from numpy import *

class MLP(object):
    def __int__(self):
        self.model = None

    def BuildModel(self):
        model = Sequential()
        model.add(Dense(output_dim=4, input_dim=8))
        model.add(Activation("relu"))
        model.add(Dense(2, init='normal'))
        model.add(Activation("softmax"))


        sgd = SGD(l2=0.0,lr=0.05, decay=1e-6, momentum=0.9, nesterov=True)
        model.compile(loss='binary_crossentropy', optimizer=sgd, class_mode="categorical")
        json_string = model.to_json()
        open('data/my_model_architecture_un.json', 'w').write(json_string)
        model.save_weights('data/my_model_weights_un.h5', overwrite=True)
        self.model = model
        return self.model

    def TrainModel(self, X_train, Y_train):
        #model.fit(X_train, Y_train, nb_epoch=5, batch_size=32)
        #self.model.train_on_batch(X_train, Y_train)
        #print X_train, Y_train
        self.model.fit(X_train, Y_train,nb_epoch=5,verbose=0)

    def TestModel(self,X_test):
        classes = self.model.predict_classes(X_test,verbose=0)
        proba = self.model.predict_proba(X_test,verbose=0)
        return classes,proba


if __name__ == '__main__':
    mlp = MLP()
    mlp.BuildModel()
    mlp.TrainModel(array([[0,0,1]]), array([[0,1]]))
    print mlp.TestModel(array([[0,0,1]]))
    mlp.TrainModel(array([[1,1,0]]), array([[1,0]]))
    print mlp.TestModel(array([[1,1,0]]))
    print mlp.TestModel(array([[0,0,1]]))
