import logging
import pyodbc
import azure.functions as func
import json
import random
from  twilio.rest import Client 
from . import dbtemplate

def dbconnect():
    try: 
        server = 'tcp:hipay.database.windows.net'
        database = 'hipay'
        username = 'adminhipay@hipay'
        password = 'admin@Pay'
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    except Exception as e:
        logging.info(str(e))
        raise Exception(e)
    else:
        return cnxn

def send_sms(mobile,otp):
    account_sid = 'AC1d2df8994d4554d98626f7d0ec09bad1'
    auth_token = '74ee91fc30b25e0b61615d14b7ca4d4c'
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
            body="Your code for HiPAY is "+str(otp)+' Valid for 5 minutes',
            messaging_service_sid='MG7542ddd67230e5fb3984182107c5d93e',
            to='+91'+mobile
            )
    return



def main_function(mobile):
    try:
        conn=dbconnect()
        cur=conn.cursor()
        choices=[str(i) for i in range(10)]
        otp_list=[random.choice(choices) for i in range(6)]
        otp=''.join(otp_list)
        send_sms(mobile,otp)
        cur.execute(dbtemplate.insert_template.format(mobile,otp))
        conn.commit()
        
    except Exception as e:
        raise Exception(str(e))
    else:
        return

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        headers={"Content-Type":"application/json"}
        logging.info('Starting send sms')

        mobile = req.params.get('mobile')


        if mobile:
            if len(mobile)!=10:
                body={}
                body['status']='error'
                body['message']='mobile validation failed'
                return func.HttpResponse(
                    json.dumps(body),
                    status_code=200,
                    headers=headers
                    )

            main_function(mobile)
            body={}
            body['status']='success'
            body['message']='otp send successfully'
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers
            )
            
        else:
            body={}
            body['status']='error'
            body['message']='mobile parameter missing'
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers
            )
        
    except Exception as e:
        logging.info(str(e))
        body={}
        body['status']='error'
        body['message']=str(e)
        return func.HttpResponse(
                json.dumps(body),
                status_code=500,
                headers=headers
            )
        
