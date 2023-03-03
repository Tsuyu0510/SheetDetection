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
from keras.models import load_model
from tensorflow.keras import models, layers, optimizers

from keras.preprocessing import image
import os 


filepath = '/home/learning03/A4testimage'
filepath_success = '/home/learning03/returnSheet_A4/CNN_PASS'




model = load_model('/home/learning03/A4XceptionClassification.h5')
#model.compile(loss = 'binary_crossentropy',optimizer = 'adam',metrics = ['accuracy'])
model.compile(loss='categorical_crossentropy',optimizer=optimizers.SGD(lr=1e-4, momentum=0.9), metrics=['accuracy'])


## Xception_Conditions 

for file in os.listdir(filepath):
	img =image.load_img(filepath+'/'+file,target_size = (512, 512))
#img_resize.save(filepath_save+'/'+file)
	x = image.img_to_array(img)/255.
	x = np.expand_dims(x,axis = 0)
	#img_resize.show()
	#img_resize_predict = np.vstack([x])
	preds = model.predict(x.reshape(1,512,512,3))
	print (file, preds)
	
	if preds[0][0] > preds[0][1]:
		#shutil.move(filepath+'/'+file, filepath_OCR_Origin+'/'+file)
		print (file +'_'+'PASS'+'_'+'N')
		#shutil.copy(filepath+'/'+file, filepath_success+'/'+'Y'+'_'+file)

	else:
		#shutil.move(filepath+'/'+file, filepath_PredictionError+'/'+file)
		print(file + '_' +'Fail'+'_'+'Y')
		#shutil.copy(filepath+'/'+file, filepath_success+'/'+'N'+'_'+file)

## CNN_Conditions 
'''
for file in os.listdir(filepath):
	img = image.load_img(filepath+'/'+file,target_size = (827, 585))
	#img_resize.save(filepath_save+'/'+file)
	x = image.img_to_array(img)
	x = np.expand_dims(x,axis = 0)
	#img_resize.show()
	img_resize_predict = np.vstack([x])
	preds = model.predict(img_resize_predict)

	print (file, preds)
	if preds == [1.]:
		print (file +'_'+'PASS'+'_'+'Y')
		#shutil.copy(filepath+'/'+file, filepath_success+'/'+'Y'+'_'+file)
	else:
		print(file + '_' +'Fail'+'_'+'N')
		#shutil.copy(filepath+'/'+file, filepath_success+'/'+'N'+'_'+file)
'''
	
	



