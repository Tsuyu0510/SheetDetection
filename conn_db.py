## build insert_db function 
import pymysql
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.types import NVARCHAR, Integer, Float,VARCHAR






def INSERT_DB(Table1):
    dtypedict = {'object':VARCHAR(length= 255),'int':Integer(),'float':Float()}
    engine = create_engine('mysql+pymysql://root:*********', encoding= 'utf8')
    con = pymysql.connect(host = '*******', user = '***',password = '******', database = '****')
    #timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        Table1.to_sql('DeliverySheet_New', engine, index= False,if_exists = 'append', dtype = dtypedict)
        #shutil.move(filepath+'/'+file, filepath3+'/'+file)  
        return print (Table1),print ("INSERT_SUCCESS!!!")
    except sqlalchemy.exc.IntegrityError:
        pass
        return print ('SUCCESS_ALL DATA WAS UPDATED')
               
