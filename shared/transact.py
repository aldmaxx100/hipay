import logging
import pyodbc
import azure.functions as func
from . import dbtemplate
#import dbtemplate
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def get_db_conn():
    try: 
        server = 'tcp:hipay.database.windows.net'
        database = 'hipay'
        username = 'adminhipay@hipay'
        password = 'admin@Pay'
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    except Exception as e:
        logging.info(str(e))
        raise Exception('error in get_db_conn: '+str(e))
    else:
        return cnxn

def get_shared_key(upi):
    try:
        conn=get_db_conn()
        cur=conn.cursor()
        cur.execute(dbtemplate.get_key.format(upi))
        res=cur.fetchall()
        
        if len(res)==0:
            return '',False
        else:
            return res[0][0],True
    except Exception as e:
        logging.info(str(e))
        raise Exception('error in get_shared_key:'+str(e))


def decode(payload,iv,key):
    try:
        key=b64decode(key)
        iv = b64decode(iv)
        ct = b64decode(payload)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        
        return pt.decode('utf-8')

    except Exception as e:
        logging.info(str(e))
        raise Exception('error in decode:'+str(e))

def get_upi(phonenumber):
    try:
        conn=get_db_conn()
        cur=conn.cursor()
        cur.execute(dbtemplate.get_upi.format(phonenumber))
        res=cur.fetchall()
        if len(res)==0
            return '',False
        else:
            return res[0][0],True
    except Exception as e:
        logging.info(str(e))
        raise Exception('error in get_upi:'+str(e))

def transfer(sender_ph,sender_upi,receiver_ph,receiver_upi,amount):
    try:
    
        conn=get_db_conn()
        cur=conn.cursor()
        cur.execute(dbtemplate.debit_fund.format(sender_upi,amount))
        cur.execute(dbtemplate.credit_fund.format(receiver_upi,amount))
        cur.excecute(dbtemplate.transaction_insert(sender_ph,sender_upi,receiver_ph,receiver_upi,amount))
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        logging.info(str(e))
        raise Exception('error in get_upi:'+str(e))




def check_request(payload,iv,phonenumber):
    try:
        conn=get_db_conn()
        cur=conn.cursor()
        cur.excecute(dbtemplate.check_request.format(payload,iv,phonenumber))
        res=cur.fetchall()
        if res[0][0]>0:
            return False

        else:
            cur.execute(dbtemplate.req_insert.format(payload,iv,phonenumber))
            conn.commmit()
            return True
        
    except Exception as e:
        conn.rollback()
        logging.info(str(e))
        raise Exception('error in check_request:'+str(e))










