#for Transfer Learning
import ssl
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
import matplotlib.pyplot as plt
from tensorflow.keras import applications
from tensorflow.keras.layers import Flatten
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from tensorflow.keras import models, layers, optimizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing.image import load_img, img_to_array

from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Convolution2D,MaxPooling2D
from keras.layers import Activation
from tensorflow.keras.applications import Xception
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications import MobileNet
#%matplotlib inline
ssl._create_default_https_context = ssl._create_unverified_context
train_datagen = ImageDataGenerator(rescale = 1./255)
	#rotation_range= 30,
	#vertical_flip = True,
	#shear_range = 0.5)

img_width = 512
img_height = 512
test_datagen = ImageDataGenerator(rescale = 1./255)


train_generator = train_datagen.flow_from_directory('/home/learning03/A4Data/Train',
	target_size = (img_width,img_height),
	batch_size = 2,
	class_mode = 'categorical')

test_generator = test_datagen.flow_from_directory('/home/learning03/A4Data/Test',
	target_size = (img_width,img_height),
	batch_size = 2,
	class_mode = 'categorical')


def history_plot(history):
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    epochs = range(1, len(acc) + 1)

    plt.title('Training and validation accuracy')
    plt.plot(epochs, acc, 'red', label='Training acc')
    plt.plot(epochs, val_acc, 'blue', label='Validation acc')
    plt.legend()

    plt.figure()
    plt.title('Training and validation loss')
    plt.plot(epochs, loss, 'red', label='Training loss')
    plt.plot(epochs, val_loss, 'blue', label='Validation loss')

    plt.legend()
    plt.show()



Xception_base = Xception(weights='imagenet', include_top=False)

x = Xception_base.output
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dense(512, activation='relu')(x)
predictions = layers.Dense(int(len(train_generator.class_indices.keys())), activation='softmax')(x)
Xception_transfer = models.Model(inputs=Xception_base.input, outputs=predictions)
Xception_transfer.summary()


Xception_transfer.compile(loss='categorical_crossentropy',optimizer=optimizers.SGD(lr=1e-4, momentum=0.9), metrics=['accuracy'])
history = Xception_transfer.fit(train_generator,epochs=100,shuffle = True, verbose = 1, validation_data = test_generator)


history_plot(history)

Xception_transfer.save('A4XceptionClassification.h5')

