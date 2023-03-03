import PIL.Image
import numpy as np 
import PIL.ImageDraw
from PIL import *
import datetime
#from PIL import ImageEnhance
#from PIL import
import shutil
import os
import tensorflow as tf
import keras
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Convolution2D,MaxPooling2D
from keras.layers import Activation,Dropout,Flatten,Dense 
import matplotlib.pyplot as plt
from keras import optimizers



#filepath_pass = '/home/learning03/A5Data/Train/Pass'
#filepath_fail = '/home/learning03/A5Data/Train/Fail'


## model structure 
model = Sequential()

model.add(Convolution2D(filters = 32,kernel_size = 3,padding = 'same',input_shape = (415, 585,3)))
model.add(Activation('softmax'))
model.add(MaxPooling2D(pool_size = (3,3)))


model.add(Convolution2D(filters = 64,kernel_size = 4,padding = 'same'))
model.add(Activation('softmax'))
model.add(MaxPooling2D(pool_size = (3,3)))
#model.add(Dropout(0.25))

model.add(Flatten())
#model.add(Dense(32))
#model.add(Activation('relu'))
#model.add(Dropout(0.25))

model.add(Dense(128))
model.add(Activation('softmax'))
#model.add(kernel_regularizer = regularizers.l2(l=0.001))
model.add(Dropout(0.25))

#model.add(kernel_regularizer = regularizers.l2(l=0.001))
model.add(Dense(1))
model.add(Activation('sigmoid'))
#sgd = tf.keras.optimizers.SGD(lr=0.001, clipnorm=1.)
model.compile(loss = 'binary_crossentropy',optimizer = 'adam',metrics = ['accuracy'])

model.summary()

train_datagen = ImageDataGenerator(
	rescale = 1./255)
	#rotation_range= 30,
	#vertical_flip = True,
	#shear_range = 0.5)


test_datagen = ImageDataGenerator(rescale = 1./255)

train_generator = train_datagen.flow_from_directory('/home/learning03/A4Data/Train',
	target_size = (415, 585),
	batch_size = 2,
	class_mode = 'binary')

test_generator = test_datagen.flow_from_directory('/home/learning03/A4Data/Test',
	target_size = (415, 585),
	batch_size = 2,
	class_mode = 'binary')


history = model.fit(train_generator,batch_size = 2,epochs = 50,validation_data = test_generator,validation_steps = 10)

loss,accuracy = model.evaluate(test_generator)
print (f'The Acc on testing data = {accuracy}')
model.save('A4CNNClassification.h5')




accuracy = history.history['accuracy']
loss = history.history['loss']
val_accuracy = history.history['val_accuracy']
val_loss = history.history['val_loss']
epochs = range(50)

plt.plot(epochs,accuracy,'r-')
plt.plot(epochs,val_accuracy,'b-')
plt.legend()
plt.show()


plt.plot(epochs,loss,'r-')
plt.plot(epochs,val_loss,'b-')
plt.legend()
plt.show()






#X_train_pass = list()
#y_train_pass = list()
#X_train_fail = list()
#y_train_fail = list()

## pic resize
'''
for file in os.listdir(filepath_fail):
	img = Image.open(filepath_fail+'/'+ file)
	width = 50
	img = img.convert('L')
	ratio = float(width)/img.size[0]
	height = int(img.size[1]*ratio)
	img_resize = img.resize((50, height), Image.BILINEAR )
	img_resize.save(filepath_save+'/'+file)
	#img_resize.show()
	img.close()
	#ConvertoNparray(img_resize,50)
	X_train_pass.append(Np_array)
'''
'''

for file in os.listdir(filepath_fail):
	img = Image.open(filepath_fail+'/'+ file)
	img.close()
	#ConvertoNparray(img_resize,50)
	X_train_pass.append(Np_array)

for file_2 in os.listdir(filepath_fail):
	img_2 = Image.open(filepath_fail+'/'+ file_2)
	width = 50
	img_2 = img_2.convert('L')
	ratio = float(width)/img_2.size[0]
	height = int(img_2.size[1]*ratio)
	img_resize_2 = img_2.resize((50, height), Image.BILINEAR )
	Np_array_2  = np.array(img_resize_2,float)
	Np_array_2 /=255
	#img_resize.show()
	#ConvertoNparray(img_resize,50)
	X_train_fail.append(Np_array_2)
	
#X_train = X_train_pass.append(X_train_fail)
#print(X_train_pass)
#print (X_train_fail)
y_train_pass = np.zeros(len(filepath_pass+'/'+ file))
y_train_fail = np.ones(len(filepath_fail+'/'+ file_2))

X_train = X_train_pass+X_train_fail
y_train = y_train_pass+y_train_fail

print (width,height)
#X_train4D = X_train.reshape(x_train.shape[0],50,35,1)
print (X_train)
print (len(filepath_pass+'/'+ file))
print (len(filepath_fail+'/'+ file))

'''