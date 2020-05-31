import logging
import pyodbc
import azure.functions as func
from . import dbtemplate
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import boto3
from ..shared import config

def send_sms(ac1,upi1,atype,ac2,upi2,amount,direction):
    sms='''
    Your HiPay account linked to {0}({2}) is {1} Rs.{3} {6} account {4}({5}).'''
    #session = boto3.Session(
    #    region_name="ap-south-1",
    #    aws_access_key_id=config.accesskey,
    #    aws_secret_access_key=config.secretkey
    #)
    #sns_client = session.client('sns')
    response = config.sns_client.publish(
            PhoneNumber='+91' + str(ac1),
            Message=sms.format(ac1,atype,upi1,amount,ac2,upi2,direction),
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'HIPAY'
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )
    return



def get_db_conn():
    try: 
        server = 'tcp:hipay.database.windows.net'
        database = 'hipay'
        username = config.dbusername
        password = config.dbpassword
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
        
        return pt.decode('utf-8'),True

    except Exception as e:
        logging.info(str(e))
        return '',False
        #raise Exception('error in decode:'+str(e))

def get_upi(phonenumber):
    try:
        conn=get_db_conn()
        cur=conn.cursor()
        cur.execute(dbtemplate.get_upi_db.format(phonenumber))
        res=cur.fetchall()
        if len(res)==0:
            return '',False
        else:
            return res[0][0],True
    except Exception as e:
        logging.info(str(e))
        raise Exception('error in get_upi:'+str(e))

def transfer(sender_ph,sender_upi,receiver_ph,receiver_upi,amount,pin,mode,ackpin):
    try:
    
        conn=get_db_conn()
        cur=conn.cursor()
        cur.execute(dbtemplate.get_amount.format(sender_ph,pin,sender_upi))
        res=cur.fetchall()
        if len(res)==0:
            
            cur.execute(dbtemplate.transaction_insert.format(sender_ph,sender_upi,receiver_ph,receiver_upi,amount,mode,ackpin,1))
    
            #meaning incorrect pin
            conn.commit()
            return 1
        
        if int(res[0][0])<int(amount):
            cur.execute(dbtemplate.transaction_insert.format(sender_ph,sender_upi,receiver_ph,receiver_upi,amount,mode,ackpin,2))
            conn.commit()
            #meaning not sufficient balance
            return 2


        cur.execute(dbtemplate.debit_fund.format(amount,sender_upi))
        cur.execute(dbtemplate.credit_fund.format(amount,receiver_upi))
        cur.execute(dbtemplate.transaction_insert.format(sender_ph,sender_upi,receiver_ph,receiver_upi,amount,mode,ackpin,0))
        conn.commit()
        send_sms(sender_ph,sender_upi,'debited',receiver_ph,receiver_upi,amount,'towards')
        send_sms(receiver_ph,receiver_upi,'credited',sender_ph,sender_upi,amount,'from')
        
        return 0
        
    except Exception as e:
        conn.rollback()
        logging.info(str(e))
        raise Exception('error in transfer_req:'+str(e))




def check_request(payload,iv,phonenumber):
    #return True
    try:
        conn=get_db_conn()
        cur=conn.cursor()
        cur.execute(dbtemplate.check_req.format(payload,iv,phonenumber))
        res=cur.fetchall()
        if res[0][0]>0:
            return False

        else:
            cur.execute(dbtemplate.req_insert.format(payload,iv,phonenumber))
            conn.commit()
            return True
        
    except Exception as e:
        conn.rollback()
        logging.info(str(e))
        raise Exception('error in check_request:'+str(e))


def check_ack(mobile,ackpin):
    try:
        conn=get_db_conn()
        cur=conn.cursor()
        logging.info('getting conn')
        cur.execute(dbtemplate.check_ack_pin.format(ackpin))
        res=cur.fetchall()
        logging.info('check ack')
        logging.info(str(res))
        if res[0][0]==0:
            return True
        else:
            return False
    except Exception as e:
        raise Exception('error in check_ack:'+str(e))









