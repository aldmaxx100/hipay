import logging
import pyodbc
import azure.functions as func
import json
import random 
from . import dbtemplate
from ..shared import config,transact
import boto3

def send_sms(mobile,otp):
    session = boto3.Session(
        region_name="ap-south-1",
        aws_access_key_id=config.accesskey,
        aws_secret_access_key=config.secretkey
    )
    sns_client = session.client('sns')
    response = sns_client.publish(
            PhoneNumber='+91' + str(mobile),
            Message='Hello there!Your OTP for HiPAY Verification is ' + str(
                otp) + '.This Otp is valid for 5 minutes.',
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



def main_function(mobile):
    try:
        conn=transact.get_db_conn()
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
        
