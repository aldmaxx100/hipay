import logging
import urllib
import json
import azure.functions as func
from ..shared import transact
import boto3
from ..shared import config


def send_ack(mobile,status,message,cipher):
    sms='''
    ackhipay {0} {1} {2}
    
    '''
    session = boto3.Session(
        region_name="ap-southeast-1",
        aws_access_key_id=config.accesskey,
        aws_secret_access_key=config.secretkey
    )
    sns_client = session.client('sns')
    response = sns_client.publish(
            PhoneNumber='+91' + str(mobile),
            Message=sms.format(status,message,cipher),
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




def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('Python HTTP trigger function processed a request.')

        res=req.get_body()
        res=res.decode('utf-8')
        logging.info(res)
        part=res.split('&')
        trash,mobile=part[0].split('=')
        mobile=mobile[2:]
        trash,intercontent=part[1].split('=')
        
        keyword,payload_or,iv=intercontent.split('%20')
        ct=urllib.parse.unquote(payload_or)
        iv=urllib.parse.unquote(iv)
        logging.info(mobile)
        logging.info(payload_or)
        logging.info(iv)
        logging.info('check req')
        if not transact.check_request(ct,iv,mobile):
            body={}
            body['status']='error'
            body['message']='invalid request..request already used'
            send_ack(mobile,'failed','request-invalid',urllib.parse.unquote(payload_or))
            logging.info(body)
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers
            )
        logging.info('shared key')
        key,F=transact.get_shared_key(mobile)
        if not F:
            body={}
            body['status']='error'
            body['message']='mobile number doesnt exist'
            send_ack(mobile,'failed','mobile-number-doesnt-exists',urllib.parse.unquote(payload_or))
            logging.info(body)
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers
            )
            
        logging.info('decode check')
        logging.info(ct)
        logging.info(iv)
        payload,F=transact.decode(ct,iv,key)
        if not F:
            body={}
            body['status']='error'
            body['message']='Invalid ciphertext'
            send_ack(mobile,'failed','invalid-cipher-text',urllib.parse.unquote(payload_or))
            logging.info(body)
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers
            )
        logging.info('param split')
        params=payload.split('@#@')
        logging.info(params)
        receiver_mobile=params[0]
        amount=params[1]
        sender_upi=params[2]
        pin=params[3]
        logging.info('getupi request')
        
        receiver_upi,F=transact.get_upi(receiver_mobile)
        if not F:
            body={}
            body['status']='error'
            body['message']='Invalid receiver mobile'
            send_ack(mobile,'failed','Invalid-receiver-mobile',urllib.parse.unquote(payload_or))
            logging.info(body)
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers
            )
        
        logging.info('transfer request')
        success=transact.transfer(mobile,sender_upi,receiver_mobile,receiver_upi,amount,pin,'offline')
        if success==0:
            
            body={}
            body['status']='succcess'
            body['message']='Transfer success'
            logging.info(body)
            send_ack(mobile,'success','transfer-successfull',urllib.parse.unquote(payload_or))
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers
            )
        elif success==1:
            body={}
            body['status']='error'
            body['message']='Incorrect upi pin'
            send_ack(mobile,'failed','incorrect-upi-pin',urllib.parse.unquote(payload_or))
            logging.info(body)
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers
            )
        elif success==2:
            body={}
            body['status']='error'
            body['message']='Insuffcient Balance'
            send_ack(mobile,'failed','insufficient-balance',urllib.parse.unquote(payload_or))
            logging.info(body)
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers
            )



        return func.HttpResponse(f"ok!")
    except Exception as e:
        logging.info(str(e))
        return func.HttpResponse("Failed")