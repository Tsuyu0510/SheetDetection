import numpy as np 
import pandas as pd 
from operator import itemgetter, attrgetter
import pytesseract
import re
import PIL.Image
import PIL.ImageDraw
from PIL import *
from PIL import ImageEnhance
import shutil
import datetime
#from PIL import ImageEnhance
#from PIL import 
import shutil
#import cv2
import os
import os.path

import logging

## 因為日期未來會新增，故使用date 函數自動輸出今天日期作為路徑變數名稱
#date = datetime.date.today()
#date = str(date)
#date = date.replace('-','') 

## build OCR funcrion 
def OCR_Process(img,rawfileName,fileServerPath):
    #filepath = '/mnt/testforFS/test_returnsheeet_30_20221104' ## mount fileserver directory 
    #img = Image.open(filepath +'/'+ filename)
    logging.info('call ocr_proccess')

    filepath_raw_data = os.path.join(fileServerPath, 'Raw_data') ## OCR 原始檔案位置路徑
    filepath_ocr_success = os.path.join(fileServerPath, 'OCR_success') ## OCR 成功文件夾路徑
    filepath_ocr_fail = os.path.join(fileServerPath, 'OCR_fail') ##OCR 失敗文件夾路徑

    img = img.convert('L') ## 掃描機掃的圖片現在需要加這行程式才能跑起來，該行意思為轉為灰階
     
    img_crop = img.crop((1350,12,1950,420))## fit小白的尺寸
    #img_crop = img.crop((1340,190,1930,420))


    enhancer = ImageEnhance.Color(img_crop)
    enhancer = enhancer.enhance(1)
    enhancer = ImageEnhance.Brightness(enhancer)
    enhancer = enhancer.enhance(2)
    enhancer = ImageEnhance.Contrast(enhancer)
    enhancer = enhancer.enhance(2.5)
    enhancer = ImageEnhance.Sharpness(enhancer)
    img_crop = enhancer.enhance(2)

    threshold = 250
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    img_crop = img_crop.point(table,'1')
    
    text = pytesseract.image_to_string(img_crop,lang='eng')
    #print (text)
    ## regex 28-xxxxxxxx-xxx
    sheetNo = re.compile(r'[2][8]-\d{8}-\d{3}')
    result = sheetNo.findall(text)
    result = list(map(lambda x:x.replace("-",''),result))
    #results= str(result).join(result)
    results = str("").join(result)
    results = str(results[0:14])
    SheetNo = results
    NO_PREFIX = SheetNo[0:2] ##28
    DISTR_CONFIRM_NO = SheetNo[2:10] ## 確認書單號
    DISTR_DEL_TYPE = SheetNo[10:12]  ## 配別
    NO_CHECK_NO = SheetNo[12:13] ## 檢核碼
    #print(NO_PREFIX)
    #print (DISTR_CONFIRM_NO)
    #print(DISTR_DEL_TYPE)
    #print (NO_CHECK_NO)
    #print (SheetNo)
    #img_crop.show()

    ## checkdate
    img_crop_2 = img.crop((2200,200,2740,450)) ## fit小白的尺寸
    ## binary img into black and white 
    ## threshold could define by user

    enhancer = ImageEnhance.Color(img_crop_2)
    enhancer = enhancer.enhance(1)
    enhancer = ImageEnhance.Brightness(enhancer)
    enhancer = enhancer.enhance(2)
    enhancer = ImageEnhance.Contrast(enhancer)
    enhancer = enhancer.enhance(2)
    enhancer = ImageEnhance.Sharpness(enhancer)
    img_crop_2 = enhancer.enhance(2)



    threshold = 241
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    img_crop_2 = img_crop_2.point(table,'1')


    text2 = pytesseract.image_to_string(img_crop_2,lang='eng')
    DeliveryDate = re.compile(r'[2][0]\d{2}/\d{2}/\d{2}')
    result_date = DeliveryDate.findall(text2)
    #results_date= str(result_date).join(result_date)
    results_date= str("").join(result_date)
    results_date = str(results_date[0:11])
    results_date_dash = results_date.replace('/','')
    sheepingDate = results_date_dash
    #print(results_date)
    print(results_date_dash)
    #img_crop_2.show()
    filename = results+'_'+results_date_dash
    #print (filename)
    if len(filename) == 22:
        ## move file from raw_data folder to success folder
        shutil.copy(filepath_raw_data +'/'+rawfileName, filepath_ocr_success +'/'+f"{filename}.jpg") 
        return [SheetNo, sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DISTR_DEL_TYPE,NO_CHECK_NO]
    else:
        ## move file from raw_data folder to fail folder
        shutil.copy(filepath_raw_data+'/'+rawfileName, filepath_ocr_fail+'/'+rawfileName) 
        return 'OCR_FAIL'
    
