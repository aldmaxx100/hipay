import logging
import secrets
import random
import json
import pyodbc
from base64 import b64encode
import azure.functions as func
from . import dbtemplate
from ..shared import transact



def get_secret_key():
    key=secrets.token_bytes(32)
    shared=b64encode(key).decode('utf-8')
    return shared

def get_account():
    choices=[str(i) for i in range(10)]
    num_list=[random.choice(choices) for i in range(9)]
    accountid=''.join(num_list)
        
    return '1'+accountid

def pingen(mobile):
    
    return int(mobile[-4:])



def upi_gen():
    choices=['1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    num_list=[random.choice(choices) for i in range(random.choice([5,6,7]))]
    upi=''.join(num_list)

    return upi+'@funny'





def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('started')
        headers={"Content-Type":"application/json"}
        mobile=req.params.get('mobile')
        otp=req.params.get('otp')
        logging.info(mobile)
        logging.info(otp)


        if  not mobile  or not otp:
            body={}
            body['status']='error'
            body['message']='mobile or otp parameter missing'
            return func.HttpResponse(
                    json.dumps(body),
                    status_code=200,
                    headers=headers
                )
        mobile=int(mobile)
        otp=int(otp)
        logging.info('taking dbsession')
        conn=transact.get_db_conn()
        cur=conn.cursor()
        cur.execute(dbtemplate.otp_verify.format(mobile,otp))
        result=cur.fetchall()
        logging.info(result)
        if result[0][0]==1:
            logging.info('check if profile exists:')
            cur.execute(dbtemplate.select_record.format(mobile))
            result=cur.fetchall()
            logging.info(result)
            if len(result)==0:
                logging.info('if not insert into table and return') 
                shared=get_secret_key()
                upi=upi_gen()
                pin=pingen(str(mobile))
                account=get_account()
                
                cur.execute(dbtemplate.insert_template.format(account,mobile,upi,pin,shared))
                conn.commit()
                body={}
                body['status']='success'
                body['message']='Otp verified succesfully'
                body['sharedkey']=shared
                body['upiaddress']=upi
                return func.HttpResponse(
                    json.dumps(body),
                    status_code=200,
                    headers=headers
                    )
            else:
                logging.info('profile exists')
                body={}
                body['status']='success'
                body['message']='otp verified successfully'
                body['sharedkey']=result[0][0]
                body['upiaddress']=result[0][1]
                body['smskey']='RF8LP'
                return func.HttpResponse(
                    json.dumps(body),
                    status_code=200,
                    headers=headers
                    )

            
            
            
            
            
        else:
            body={}
            body['status']='success'
            body['message']='otp verification failed'
            return func.HttpResponse(
                    json.dumps(body),
                    status_code=200,
                    headers=headers
                )
        

            
        
        
            

    except Exception as e:
        body={}
        body['status']='error'
        body['message']=str(e)
        return func.HttpResponse(
                json.dumps(body),
                status_code=500,
                headers=headers
            )

