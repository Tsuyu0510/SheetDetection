## build insert_db function 
import pymysql
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.types import NVARCHAR, Integer, Float,VARCHAR
import json
import shutil
import os
import cx_Oracle
from sqlalchemy import create_engine
from dbutils.pooled_db import PooledDB
import traceback

import logging

## oracle coneect string 
account = ""
pwd = ""
dbip = ""
dbport = ""
#dbname = jsonData['database_name']
tnsname = ""

dsnStr = cx_Oracle.makedsn(dbip, dbport, sid = tnsname)
pool = PooledDB(cx_Oracle,mincached = 20,blocking = True, user = account,password = pwd,dsn = dsnStr) ## connection pool 
#conn_string = f'oracle+cx_oracle://{account}:{pwd}@{dbip}:{dbport}/{tnsname}'
conn_string = "oracle+cx_oracle://%s:%s@%s" %(account, pwd, dsnStr)
#con = cx_Oracle.connect(account,pwd,dsnStr)
con = pool.connection()

engine = create_engine(conn_string, encoding= 'utf8')
dtypedict = {'object':VARCHAR(length=255),'int':Integer(),'float':Float()}

cur =con.cursor()


## 因為日期未來會新增，故使用date 函數自動輸出今天日期作為路徑變數名稱，不需要可以再拿掉
#date = datetime.date.today()
#date = str(date)
#date = date.replace('-','') 



def INSERT_DB(Table1,YOLO_filename,fileServerPath,yolo_status):
    logging.info('call insert db')

    filepath_yolo_success = os.path.join(fileServerPath, 'YOLO_success') ## yolo成功文件夾路徑
    filepath_yolo_fail = os.path.join(fileServerPath, 'YOLO_fail') ## yolo 失敗文件夾路徑
    filepath_ocr_archived = os.path.join(fileServerPath, 'Archived') ##  歸檔位置路徑

    print('yolo_status: ' + yolo_status)
    
    try:
        if yolo_status == 'success':
            print('in yolo_status')
            rows = [tuple(x) for x in Table1.values]
            print (rows)
            logging.info(rows)
            print('conndb1')
            #Table1.to_sql('IMAGEIDENTIFY'.lower(), engine, index= False,if_exists = 'append')
            cur.executemany('''INSERT INTO exch.imageidentify (DC_NO,NO_PREFIX,DISTR_CONFIRM_NO,DISTR_DEL_TYPE,NO_CHECK_NO,ACCEPT_DATE,FUNC_KIND,LOCATION,QTY,RECEIVER,STORE_CHAPTER,RECEIPT,USER_ID,UPDATE_TIME,ERR_STATUS,ERR_ID,FUNC_ID) VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17)''',rows)
            con.commit()
            cur.close()
            #con.close()
            shutil.move(filepath_yolo_success +'/'+YOLO_filename, filepath_ocr_archived+'/'+YOLO_filename)  
            return Table1, "INSERT_SUCCESS!!!"
        else:
            rows = [tuple(x) for x in Table1.values]
            print (rows)
            logging.info(rows)
            logging.info(rows)
            #Table1.to_sql('IMAGEIDENTIFY'.lower(), engine, index= False,if_exists = 'append')
            cur.executemany('''INSERT INTO exch.imageidentify (DC_NO,NO_PREFIX,DISTR_CONFIRM_NO,DISTR_DEL_TYPE,NO_CHECK_NO,ACCEPT_DATE,FUNC_KIND,LOCATION,QTY,RECEIVER,STORE_CHAPTER,RECEIPT,USER_ID,UPDATE_TIME,ERR_STATUS,ERR_ID,FUNC_ID) VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17)''',rows)
            con.commit()
            cur.close()
            #con.close()
            #shutil.copy(filepath_yolo_fail +'/'+YOLO_filename, filepath_ocr_archived+'/'+YOLO_filename)   
            ##因為失敗還要手動調整最後才移動單據，所以失敗單據先不移動
            return Table1, "YOLO_FAIL_RESULTS_INSERT_SUCCESS!!!"
    except cx_Oracle.IntegrityError as e:
        error_obj, = e.args
        print("Primary key already exists")
        print("Error Code:", error_obj.code)
        print("Error Message:", error_obj.message)
        logging.info("Primary key already exists")
        logging.exception("message")
        return 'Primary key already exists'
    except Exception as err:  
        logging.info('error: conn_db.py')
        logging.exception("message")
        return 'DB UNKNOWN ERROR'
