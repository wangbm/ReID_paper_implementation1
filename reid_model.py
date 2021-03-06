#-*- coding: utf-8 -*-
"""
Created on Tue Oct 25 20:38:45 2016

@author: dingning
"""
import numpy as np
np.random.seed(1234)
from keras.models import Model
from keras.layers import Input,Dense,Convolution2D,Activation,MaxPooling2D,Flatten,merge
from keras.optimizers import SGD,Adam,RMSprop
from keras.utils import np_utils
from input_generator import DataSet
from input_generator import load_from_file
import pickle
from keras import backend as K

the_filename = 'data_by_path.pkl'
dir_path = '/home/ubuntu/dataset/market1501/boundingboxtrain'

def cross_input(X):
    tensor_left = X[0]
    tensor_right = X[1]
    x_length = K.int_shape(tensor_left)[1]
    y_length = K.int_shape(tensor_left)[2]
    cross_y = []
    cross_x = []
    tensor_left_padding = K.spatial_2d_padding(tensor_left,padding=(2,2))
    tensor_right_padding = K.spatial_2d_padding(tensor_right,padding=(2,2))
    for i_x in range(2, x_length + 2):
        for i_y in range(2, y_length + 2):
            cross_y.append(tensor_left_padding[:,i_x-2:i_x+3,i_y-2:i_y+3,:] 
                         - tensor_right_padding[:,i_x-2:i_x+3,i_y-2:i_y+3,:])
        cross_x.append(K.concatenate(cross_y,axis=2))
        cross_y = []
    cross_out = K.concatenate(cross_x,axis=1)
    return K.abs(cross_out)
    
def cross_input_shape(input_shapes):
    input_shape = input_shapes[0]
    return (input_shape[0],input_shape[1] * 5,input_shape[2] * 5,input_shape[3])

a1 = Input(shape=(128,64,3))
b1 = Input(shape=(128,64,3))
share = Convolution2D(20,5,5,dim_ordering='tf')
a2 = share(a1)
b2 = share(b1)
a3 = Activation('relu')(a2)
b3 = Activation('relu')(b2)
a4 = MaxPooling2D(dim_ordering='tf')(a3)
b4 = MaxPooling2D(dim_ordering='tf')(b3)
share2 = Convolution2D(25,5,5,dim_ordering='tf')
a5 = share2(a4)
b5 = share2(b4)
a6 = Activation('relu')(a5)
b6 = Activation('relu')(b5)
a7 = MaxPooling2D(dim_ordering='tf')(a6)
b7 = MaxPooling2D(dim_ordering='tf')(b6)
c1 = merge([a7,b7], mode=cross_input, output_shape=cross_input_shape)
c2 = Convolution2D(25,5,5,dim_ordering='tf',activation='relu')(c1)
c3 = MaxPooling2D((2,2),dim_ordering='tf')(c2)
c4 = Convolution2D(25,3,3,dim_ordering='tf',activation='relu')(c3)
c5 = MaxPooling2D((2,2),dim_ordering='tf')(c4)
c6 = Flatten()(c5)
c7 = Dense(10,activation='relu')(c6)
c8 = Dense(2,activation='softmax')(c7)

model = Model(input=[a1,b1],output=c8)
model.summary()

model.compile(optimizer='RMSprop',
loss='categorical_crossentropy',
metrics=['accuracy'])

dataset = load_from_file(the_filename)
market = DataSet(dataset, 100)
market_validation = DataSet(dataset,100)
#a, b = market.next_batch()
model.fit_generator(market.next_batch(), samples_per_epoch=10000, nb_epoch=10,validation_data = market_validation.next_batch(),nb_val_samples=100)

def predict(model,x,y):
    from prepare_dataset import get_image_path_list
    from PIL import Image
    import os
    path_list = get_image_path_list('/home/ubuntu/dataset/market1501/boundingboxtrain/')
    print path_list[x]
    print path_list[y]
    print 'the result is:'
    return model.predict([np.array(Image.open('/home/ubuntu/dataset/market1501/boundingboxtrain/'+path_list[x])).reshape(1,128,64,3),np.array(Image.open('/home/ubuntu/dataset/market1501/boundingboxtrain/'+path_list[y])).reshape(1,128,64,3)])




