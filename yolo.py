import numpy as np 
import pandas as pd 
from operator import itemgetter, attrgetter
import pytesseract
import re
import PIL.Image
import PIL.ImageDraw
from PIL import *
from PIL import ImageEnhance

import datetime
#from PIL import ImageEnhance
#from PIL import 
import shutil
#import cv2
import os
import os.path
import datetime

import logging
import json


loc_dt = datetime.datetime.now()
loc_dt_format = loc_dt.strftime("%Y-%m-%d %H:%M:%S")

null_value = [''] ##空值用

## 因為日期未來會新增，故使用date 函數自動輸出今天日期作為路徑變數名稱，不需要可以再拿掉
#date = datetime.date.today()
#date = str(date)
#date = date.replace('-','') 


## get DC_NO
def DC_NO_FUNC():
    with open("/opt/orion/config.json") as jsonFile:
        data = json.load(jsonFile)
        DC_NO = data['dc_id'] 
    return DC_NO



##fake list
#DC_NO =['1']
DC_NO = list(DC_NO_FUNC())
USER_ID = ['']
UPDATE_TIME = ['']
ERR_STATUS =['']
ERR_ID = ['']
FUNC_ID = ['']


# sample data 
# build YOLO PARSER function return list version for api 1 
def YOLO_PARSER(sheepingDate,SheetNo,data,fileServerPath):
    
    file_name = SheetNo+'_'+sheepingDate+'.jpg'
    logging.info('call yolo_parser')

    
    filepath_ocr_success = os.path.join(fileServerPath, 'OCR_success') ## OCR 成功文件夾路徑
    filepath_yolo_tmp = os.path.join(fileServerPath, 'YOLO_tmp') ## YOLO文件暫存區
    filepath_yolo_success = os.path.join(fileServerPath, 'YOLO_success') ## YOLO成功文件夾路徑
    filepath_yolo_fail = os.path.join(fileServerPath, 'YOLO_fail') ##YOLO失敗文件夾路徑


    ##－－－－－－－－－－－－－－－－－－－－－－－－單號拆解開始－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
  
    NO_PREFIX = SheetNo[0:2] ##28
    DISTR_CONFIRM_NO = SheetNo[2:10] ## 確認書單號
    DISTR_DEL_TYPE = SheetNo[10:12]  ## 配別
    
    NO_CHECK_NO = SheetNo[12:13] ## 檢核碼
    
    ##－－－－－－－－－－－－－－－－－－－－－－－－單號拆解結束－－－－－－－－－－－－－－－－－－－－－－－－－－－－－

    
    LabelIndex = [1,2,3,4,5,6]
    Labelresult_null = ['null','null','null','null','null','null','null','null','null','null','null','null','null','null','null','null','null','null']
  
   
    ##－－－－－－－－－－－－－－－－－－－－－－－－配別轉換開始－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
    ## 假資料，未來會變成直接query 成一個df 
    fake_df = pd.DataFrame({"DEL_TYPE": ["01", "02", "03", "04","05","06","06","07","08","08","10","11","12","13","99"],
    "CUST_DEL_TYPE": ["01","11","21","31","41","51","51","71","22","61","12","13","42","04","91"]},) ## 假資料，未來會變成直接query 成一個df 
    ## 把query 出的df 先轉成列表再轉成字典
    jsonList=[] 
    jsonList2 = []
    for i in fake_df['CUST_DEL_TYPE']:
        jsonList.append(i)
    for j in fake_df['DEL_TYPE']:
        jsonList2.append(j)
    
    #DISTR_DEL_TYPE = '51'    
    #print (jsonList)
    #print (jsonList2)
    result_dict = dict(zip(jsonList,jsonList2)) ## 兩個欄位組成字典
    #print (result_dict)
    DEL_TYPE = result_dict.get(DISTR_DEL_TYPE)  ## call key to get value
    #print (DEL_TYPE)
    
    ##－－－－－－－－－－－－－－－－－－－－－－－配別轉換結束－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－


    #LabelIndex_1 = [7,8,9,10,11,12,13,14,15,16,17,18]
    ## mapping the probability of label(for abnormal cases)
    ##model index for 3 differnet detection areas
    Model_index = ['1','2','3'] ## for send, receice,receiveitems 
    #print (SheetNo[0][10:12])
    ## get percentile y 
    top_y = []
    for i in range(0,len(data)):
        y = data[i][2][1]
        top_y.append(y)

    aray = np.array(top_y) ## covert list Y_location to array

    percentile_1 = np.percentile(aray,35) ## get p(35) to determined row 1
    percentile_2 = np.percentile(aray,65) ## get p(65) to determine row 2
    #test_sort = np.sort(top_y) 
    
    #print (top_y)
    #print (test_sort)
    #print (percentile_1)
    #print (percentile_2)
    ## get top_x
    top_x = []
    for j in range(0,len(data)):
        x = data[j][2][0]
        top_x.append(x)
    #print (top_x)
    ## get labelresult 
    Label_result = []
    for i in range(0,len(data)):
        result = data[i][0]
        Label_result.append(result)
    #print (Label_result)
    
    ## 取百分位數排序三行手寫區域
    Labelresult_total = list(zip(Label_result, top_x,top_y))
    y1 = []
    y2 = []
    y3 = []
    for i in range(0,len(Labelresult_total)):
        if int(Labelresult_total[i][2]) <= percentile_1: ## applied p(35) as row1 result 
            y1.append(Labelresult_total[i])
    
        elif  percentile_1 < int(Labelresult_total[i][2]) <= percentile_2: ## applied p(35) and p(65) as row1 and row2 result 
            y2.append(Labelresult_total[i])
    
        elif int(Labelresult_total[i][2]) >percentile_2:   ##  applied p(65) as row3  
            y3.append(Labelresult_total[i])


    y1_sort = sorted(y1, key = itemgetter(1))
    y2_sort = sorted(y2, key = itemgetter(1))
    y3_sort = sorted(y3, key = itemgetter(1))


    y_sort = y1_sort+y2_sort+y3_sort

    Labelresult_df_ori = []

    for i in range(0,len(y_sort)):
        value = y_sort[i][0]
        Labelresult_df_ori.append(value)
    

    #Labelresult_df
    
    Stamped = []
    Signed = []
    Barcode = []

    if 'stamp' in Labelresult_df_ori:
        Stamped = 'Y'
    else:
        Stamped ='N'

    if 'sign' in Labelresult_df_ori:
        Signed = 'Y'
    else:
        Signed ='N'
    
    if 'barcode' in Labelresult_df_ori:
        Barcode = 'Y'
    else:
        Barcode ='N'

   




    three_strings_stamp = []
    three_strings_sign = []
    three_strings_barcode = []

    for i in range(0,len(Labelresult_df_ori)):
        if Stamped == 'Y' :
            three_strings_stamp = ['stamp']
        elif Stamped =='N':
            three_strings_stamp = ['nostamp']
     


    for i in range(0,len(Labelresult_df_ori)):
        if Signed == 'Y' :
            three_strings_sign =['sign']
        elif Signed =='N':
            three_strings_sign =['nosign']
   

    for i in range(0,len(Labelresult_df_ori)):
        if Barcode == 'Y' :
            three_strings_barcode =['barcode']
        elif Barcode =='N':
            three_strings_barcode =['nobarcode']
     

            
    #print (three_strings_stamp)
    #print (three_strings_sign)
    #print (three_strings_barcode)

    three_string_list = three_strings_stamp + three_strings_sign + three_strings_barcode
    
    
    #print(three_string_list)

    #print (Labelresult_df_ori)

    Labelresult_df = [k for k in  Labelresult_df_ori if k not in three_string_list]
    
  
    #print (Labelresult_df)
    #[v1,v2,v3,v4,v5,v6]
    Labelresult_df_1 = Labelresult_df[0:6]   
    Labelresult_df_2 = Labelresult_df[6:12]
    Labelresult_df_3 = Labelresult_df[12:18]

    ## {1:v1,2:v2,3:v3,4:v4,5:v5,6:v6}
    label_index_result_1 = dict(zip(LabelIndex,Labelresult_df_1)) 
    label_index_result_2 = dict(zip(LabelIndex,Labelresult_df_2))
    label_index_result_3 = dict(zip(LabelIndex,Labelresult_df_3))
    
    
    ##{1:{1:v1,2:v2,3:v3,4:v4,5:v5,6:v6}}
    model_label_index_result_1 = {Model_index[0]:label_index_result_1}
    model_label_index_result_2 = {Model_index[1]:label_index_result_2}
    model_label_index_result_3 = {Model_index[2]:label_index_result_2}

    ##組合三個dict
    model_lable_index_result_dic = {}
    model_lable_index_result_dic.update(model_label_index_result_1)
    model_lable_index_result_dic.update(model_label_index_result_2)
    model_lable_index_result_dic.update(model_label_index_result_3)
    
    #print (model_lable_index_result_dic)
    ##dic for null and other situation 

    model_lable_index_result_dic_null = {'1': {1: 'null', 2: 'null', 3: 'null', 4: 'null', 5: 'null', 6: 'null'}, 
                                         '2': {1: 'null', 2: 'null', 3: 'null', 4: 'null', 5: 'null', 6: 'null'}, 
                                         '3': {1: 'null', 2: 'null', 3: 'null', 4: 'null', 5: 'null', 6: 'null'}}
    
    
    result_list_dict_null = model_lable_index_result_dic_null ## build a dict for null result
 
    result_list_dict_success = model_lable_index_result_dic ## build a dict for success result 

    ## 組合輸出的列表，同時把對應的字典包在裡頭
    ##prepare result dict -> sheepingDate','SheetNo -> for null
    #key_list = ['sheepingDate','SheetNo','yolo_index']
    #value_list =[sheepingDate,SheetNo,result_list_dict_null]
    
    #key_return_dict_null = ['yolo_index']
    return_value_null = [result_list_dict_null]
    #return_dict_null = dict(zip(key_return_dict_null,return_value_null))
    
    #prepare result dict -> Stamped[0],Signed[0],Barcode[0]
    #key_list_2 = ['Stamped','Signed','Barcode']
    value_list_2 = [Stamped[0],Signed[0],Barcode[0]]
    #return_dict_2 = dict(zip(key_list_2,value_list_2))
    
    return_dict_all_null = [] # 定义一个空列表
    return_dict_all_null = return_value_null+value_list_2
    #return_dict_all_null = 
    
    
        
    ##prepare result dict -> sheepingDate','SheetNo -> for success
    ##key_list_success = ['sheepingDate','SheetNo','yolo_index']
    #value_list_success =[sheepingDate,SheetNo,]
    #key_return_dict_success = ['yolo_index']
    return_value_success = [result_list_dict_success]
    #return_dict_success = dict(zip(key_return_dict_success,return_value_success))
    #print (return_dict_success)
    
    
    #prepare result dict -> Stamped[0],Signed[0],Barcode[0]
    #key_list_2 = ['Stamped','Signed','Barcode']
    value_list_2 = [Stamped[0],Signed[0],Barcode[0]]
    #return_dict_2 = dict(zip(key_list_2,value_list_2)) ## stamp,sign,barcode
    
    
    return_dict_all_success = [] # 定义一个空列表
    return_dict_all_success = return_value_success+value_list_2
    # return_dict_all_success = return_dict_all_success
    #print (return_dict_all_success)

    ## 判斷最終是否成功失敗
    ## df 

   

    if len(Labelresult_df)!=18: # 不是18格, 回傳為fail
        print('success db no data 1')
        #print ('存在格式錯誤')
        Totalresult1_null=[
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],null_value[0],LabelIndex[0],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],null_value[0],LabelIndex[1],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],null_value[0],LabelIndex[2],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],null_value[0],LabelIndex[3],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],null_value[0],LabelIndex[4],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],null_value[0],LabelIndex[5],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],null_value[0],LabelIndex[0],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],null_value[0],LabelIndex[1],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],null_value[0],LabelIndex[2],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],null_value[0],LabelIndex[3],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],null_value[0],LabelIndex[4],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],null_value[0],LabelIndex[5],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],null_value[0],LabelIndex[0],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],null_value[0],LabelIndex[1],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],null_value[0],LabelIndex[2],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],null_value[0],LabelIndex[3],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],null_value[0],LabelIndex[4],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
        [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],null_value[0],LabelIndex[5],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]]]

        Table1 = pd.DataFrame (Totalresult1_null,columns = ['ACCEPT_DATE','NO_PREFIX','DISTR_CONFIRM_NO','DISTR_DEL_TYPE','NO_CHECK_NO','FUNC_KIND','QTY','LOCATION','STORE_CHAPTER','RECEIVER','RECEIPT','DC_NO','USERID','UPDATE_TIME','ERR_STATUS','ERR_ID','FUNC_ID'])

        Table1['ACCEPT_DATE']= pd.to_datetime (Table1['ACCEPT_DATE']) ##修改驗收日為DATE格式
        Table1['ACCEPT_DATE']=  Table1['ACCEPT_DATE'].dt.date ##修改驗收日為DATE格式
        Table1['UPDATE_TIME']= pd.to_datetime (Table1['UPDATE_TIME']) ##修改驗收日為DATE格式
        Table1['LOCATION']= Table1['LOCATION'].astype(str) ##修改Loacation為字串
        #Table1['QTY']= Table1['QTY'].astype(str).astype(int) ##修改QTY為int格式

        Table1 = Table1[['DC_NO','NO_PREFIX','DISTR_CONFIRM_NO','DISTR_DEL_TYPE','NO_CHECK_NO','ACCEPT_DATE','FUNC_KIND','LOCATION','QTY','RECEIVER','STORE_CHAPTER','RECEIPT','USERID','UPDATE_TIME','ERR_STATUS','ERR_ID','FUNC_ID']] ##修改欄位順序 
        print(Table1)
        #Table1_null[['Labelresult_null']]=Table1_null[['Labelresult_null']].astype('str')
        #Totalresult1_null_list=[
        #sheepingDate[0],SheetNo[0],Model_index,result_list_dict_null,Stamped[0],Signed[0],Barcode[0]]

        #Table1_null = pd.DataFrame (Totalresult1_null,columns = ['ShippingDate','SheetNo','Model_index','Labelresult','LabelIndex','Stamped','Signed','Barcode'])
        #Table1_null[['Labelresult_null']]=Table1_null[['Labelresult_null']].astype('str')
        shutil.copy(filepath_ocr_success +'/'+ file_name, filepath_yolo_tmp+'/'+file_name) ## 複製一份備份到暫存區
        shutil.copy(filepath_ocr_success +'/'+ file_name, filepath_yolo_fail+'/'+file_name) 
        os.remove(filepath_ocr_success +'/'+ file_name,) ## 刪除舊的檔案
        
        logging.info('yolo辨識失敗, 不是18格:' + sheepingDate + '_' + SheetNo)
        return 'YOLO_PARSER_FAIL' , return_dict_all_null ,Table1
    
    else:
        if 'other' in Labelresult_df: #有other時, 要認定為fail, 並且json回傳null
            print('success db no data 2')
            logging.info('success db no data 2')
            #print ('存在格式錯誤')
            Totalresult1_null=[
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],null_value[0],LabelIndex[0],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],null_value[0],LabelIndex[1],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],null_value[0],LabelIndex[2],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],null_value[0],LabelIndex[3],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],null_value[0],LabelIndex[4],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],null_value[0],LabelIndex[5],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],null_value[0],LabelIndex[0],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],null_value[0],LabelIndex[1],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],null_value[0],LabelIndex[2],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],null_value[0],LabelIndex[3],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],null_value[0],LabelIndex[4],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],null_value[0],LabelIndex[5],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],null_value[0],LabelIndex[0],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],null_value[0],LabelIndex[1],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],null_value[0],LabelIndex[2],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],null_value[0],LabelIndex[3],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],null_value[0],LabelIndex[4],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],null_value[0],LabelIndex[5],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]]]

            Table1 = pd.DataFrame (Totalresult1_null,columns = ['ACCEPT_DATE','NO_PREFIX','DISTR_CONFIRM_NO','DISTR_DEL_TYPE','NO_CHECK_NO','FUNC_KIND','QTY','LOCATION','STORE_CHAPTER','RECEIVER','RECEIPT','DC_NO','USERID','UPDATE_TIME','ERR_STATUS','ERR_ID','FUNC_ID'])

            Table1['ACCEPT_DATE']= pd.to_datetime (Table1['ACCEPT_DATE']) ##修改驗收日為DATE格式
            Table1['ACCEPT_DATE']=  Table1['ACCEPT_DATE'].dt.date ##修改驗收日為DATE格式
            Table1['UPDATE_TIME']= pd.to_datetime (Table1['UPDATE_TIME']) ##修改驗收日為DATE格式
            Table1['LOCATION']= Table1['LOCATION'].astype(str) ##修改Loacation為字串
            #Table1['QTY']= Table1['QTY'].astype(str).astype(int) ##修改QTY為int格式

            Table1 = Table1[['DC_NO','NO_PREFIX','DISTR_CONFIRM_NO','DISTR_DEL_TYPE','NO_CHECK_NO','ACCEPT_DATE','FUNC_KIND','LOCATION','QTY','RECEIVER','STORE_CHAPTER','RECEIPT','USERID','UPDATE_TIME','ERR_STATUS','ERR_ID','FUNC_ID']] ##修改欄位順序 
            print(Table1)
            logging.info(Table1)
            #Table1_null[['Labelresult_null']]=Table1_null[['Labelresult_null']].astype('str')
            #Totalresult1_null_list=[
            #sheepingDate[0],SheetNo[0],Model_index,result_list_dict_null,Stamped[0],Signed[0],Barcode[0]]

            #Table1_null = pd.DataFrame (Totalresult1_null,columns = ['ShippingDate','SheetNo','Model_index','Labelresult','LabelIndex','Stamped','Signed','Barcode'])
            #Table1_null[['Labelresult_null']]=Table1_null[['Labelresult_null']].astype('str')
            shutil.copy(filepath_ocr_success +'/'+ file_name, filepath_yolo_tmp+'/'+file_name) ## 複製一份備份到暫存區
            shutil.copy(filepath_ocr_success +'/'+ file_name, filepath_yolo_fail+'/'+file_name) 
            os.remove(filepath_ocr_success +'/'+ file_name,) ## 刪除舊的檔案
            logging.info('yolo辨識失敗, 有other:' + sheepingDate + '_' + SheetNo)
            return 'YOLO_PARSER_FAIL' , return_dict_all_null ,Table1

        else: # 有18格, 沒有other, 判斷出的都是數值
            Totalresult1=[
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],Labelresult_df[0],LabelIndex[0],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],Labelresult_df[1],LabelIndex[1],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],Labelresult_df[2],LabelIndex[2],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],Labelresult_df[3],LabelIndex[3],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],Labelresult_df[4],LabelIndex[4],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],Labelresult_df[5],LabelIndex[5],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],Labelresult_df[6],LabelIndex[0],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],Labelresult_df[7],LabelIndex[1],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],Labelresult_df[8],LabelIndex[2],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],Labelresult_df[9],LabelIndex[3],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],Labelresult_df[10],LabelIndex[4],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],Labelresult_df[11],LabelIndex[5],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],Labelresult_df[12],LabelIndex[0],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],Labelresult_df[13],LabelIndex[1],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],Labelresult_df[14],LabelIndex[2],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],Labelresult_df[15],LabelIndex[3],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],Labelresult_df[16],LabelIndex[4],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]],
            [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],Labelresult_df[17],LabelIndex[5],Stamped[0],Signed[0],Barcode[0],DC_NO[0],USER_ID[0],loc_dt_format,ERR_STATUS[0],ERR_ID[0],FUNC_ID[0]]]

            #print ("全家配別為"+''+DISTR_DEL_TYPE+''+','+ "轉換為全台配別為"+''+DEL_TYPE+"") ## 測試確認用不需要可以註解掉
            Table1 = pd.DataFrame (Totalresult1,columns = ['ACCEPT_DATE','NO_PREFIX','DISTR_CONFIRM_NO','DISTR_DEL_TYPE','NO_CHECK_NO','FUNC_KIND','QTY','LOCATION','STORE_CHAPTER','RECEIVER','RECEIPT','DC_NO','USERID','UPDATE_TIME','ERR_STATUS','ERR_ID','FUNC_ID'])
            Table1['ACCEPT_DATE']= pd.to_datetime (Table1['ACCEPT_DATE']) ##修改驗收日為DATE格式
            Table1['ACCEPT_DATE']=  Table1['ACCEPT_DATE'].dt.date ##修改驗收日為DATE格式
            Table1['UPDATE_TIME']= pd.to_datetime (Table1['UPDATE_TIME']) ##修改驗收日為DATE格式
            Table1['LOCATION']= Table1['LOCATION'].astype(str) ##修改Location為字串
            Table1['QTY']= Table1['QTY'].astype(str).astype(int) ##修改QTY為int格式

            Table1 = Table1[['DC_NO','NO_PREFIX','DISTR_CONFIRM_NO','DISTR_DEL_TYPE','NO_CHECK_NO','ACCEPT_DATE','FUNC_KIND','LOCATION','QTY','RECEIVER','STORE_CHAPTER','RECEIPT','USERID','UPDATE_TIME','ERR_STATUS','ERR_ID','FUNC_ID']] ##修改欄位順序 
            print(Table1)
            
            #Totalresult1_success_list= [
            #sheepingDate[0],SheetNo[0],Model_index,result_list_dict_success,Stamped[0],Signed[0],Barcode[0]]

            #Table1 = pd.DataFrame (Totalresult1,columns = ['ShippingDate','SheetNo','Model_index','Labelresult','LabelIndex','Stamped','Signed','Barcode'])
            #Table1[['Labelresult']]=Table1[['Labelresult']].astype('int')
            #Table1['Labelresult']=Table1['Labelresult'].astype(int)
            shutil.copy(filepath_ocr_success +'/'+ file_name, filepath_yolo_tmp+'/'+file_name) ## 複製一份備份到暫存區
            shutil.copy(filepath_ocr_success +'/'+ file_name, filepath_yolo_success+'/'+ file_name) ## move改為copy 
            os.remove(filepath_ocr_success +'/'+ file_name,) ## 刪除舊的檔案
            logging.info('yolo辨識成功:' + sheepingDate + '_' + SheetNo)
            return 'YOLO_PARSER_SUCCESS', return_dict_all_success, Table1














#def Yolo_modification(data):## 修改用API 
#    Model_index = ['發出','回收','回收項目'] ## 發出，回收，回收項目
#    
#    lst_key=[]
#    lst_value=[]
#    for key,value in data.items():
#        lst_key.append(key)
#        lst_value.append(value)
#    #print (lst_key)
#    #print (lst_value)
#
#    lst_key_2=[]
#    lst_value_2=[]
#    for key2,value2 in lst_value[6].items():
#        lst_key_2.append(key2)
#        lst_value_2.append(value2)
#    #print (lst_key_2)
#    #print (lst_value_2)
#
#    #SheetNo = lst_value[0]
#    NO_PREFIX = lst_value[2]
#    DISTR_CONFIRM_NO = lst_value[3]
#    DISTR_DEL_TYPE = lst_value[4]
#    NO_CHECK_NO = lst_value[5]
#    sheepingDate = lst_value[1]
#    Stamped = lst_value[8]
#    Signed = lst_value[7]
#    Barcode = lst_value[9]
#
#    LabelIndex = lst_key_2
#    Labelresult_df = lst_value_2
#    
#    
#    ##－－－－－配別轉換開始－－－－－－－－－－－－－－－－
#    
#    ## 假資料，未來會變成直接query 成一個df 
#    fake_df = pd.DataFrame({"DEL_TYPE": ["01", "02", "03", "04","05","06","06","07","08","08","10","11","12","13","99"],
#    "CUST_DEL_TYPE": ["01","11","21","31","41","51","51","71","22","61","12","13","42","04","91"]},) ## 假資料，未來會變成直接query 成一個df 
#    ## 把query 出的df 先轉成列表再轉成字典
#    jsonList=[] 
#    jsonList2 = []
#    for i in fake_df['CUST_DEL_TYPE']:
#        jsonList.append(i)
#    for j in fake_df['DEL_TYPE']:
#        jsonList2.append(j)
#    
#    #print (jsonList)
#    #print (jsonList2)
#    result_dict = dict(zip(jsonList,jsonList2)) ## 兩個欄位組成字典
#    #print (result_dict)
#    DEL_TYPE = result_dict.get(DISTR_DEL_TYPE)  ## call key to get value
#    #print (DEL_TYPE)
#    
#    ##－－－－－配別轉換結束--------------------------
#    
#
#    Totalresult1=[
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],Labelresult_df[0],LabelIndex[0],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],Labelresult_df[1],LabelIndex[1],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],Labelresult_df[2],LabelIndex[2],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],Labelresult_df[3],LabelIndex[3],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],Labelresult_df[4],LabelIndex[4],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[0],Labelresult_df[5],LabelIndex[5],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],Labelresult_df[6],LabelIndex[6],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],Labelresult_df[7],LabelIndex[7],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],Labelresult_df[8],LabelIndex[8],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],Labelresult_df[9],LabelIndex[9],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],Labelresult_df[10],LabelIndex[10],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[1],Labelresult_df[11],LabelIndex[11],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],Labelresult_df[12],LabelIndex[12],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],Labelresult_df[13],LabelIndex[13],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],Labelresult_df[14],LabelIndex[14],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],Labelresult_df[15],LabelIndex[15],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],Labelresult_df[16],LabelIndex[16],Stamped,Signed,Barcode],
#                [sheepingDate,NO_PREFIX,DISTR_CONFIRM_NO,DEL_TYPE,NO_CHECK_NO,Model_index[2],Labelresult_df[17],LabelIndex[17],Stamped,Signed,Barcode]
#
#                ]
#
#    print ("全家配別為"+''+DISTR_DEL_TYPE+''+','+ "轉換為全台配別為"+''+DEL_TYPE+"") ## 測試確認用不需要可以註解掉
#    Table1 = pd.DataFrame (Totalresult1,columns = ['ACCEPT_DATE','NO_PREFIX','DISTR_CONFIRM_NO','DISTR_DEL_TYPE','NO_CHECK_NO','FUNC_KIND','QTY','LOCATION','STORE_CHAPTER','RECEIVER','RECEIPT'])
#    Table1 = Table1[['NO_PREFIX','DISTR_CONFIRM_NO','DISTR_DEL_TYPE','NO_CHECK_NO','ACCEPT_DATE','FUNC_KIND','LOCATION','QTY','RECEIVER','STORE_CHAPTER','RECEIPT']] ##修改欄位順序 
#    return Table1
