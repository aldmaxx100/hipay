import logging
import urllib
import json
import random
import azure.functions as func
from ..shared import transact
import boto3
from ..shared import config


def send_ack(mobile,status,message,ack1):
    sms='''
    ackhipay {0} {1} {2}
    
    '''
    #session = boto3.Session(
    #    region_name="ap-south-1",
    #    aws_access_key_id=config.accesskey,
    #    aws_secret_access_key=config.secretkey
    #)
    #sns_client = session.client('sns')
    response = config.sns_client.publish(
            PhoneNumber='+91' + str(mobile),
            Message=sms.format(status,message,ack1),
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
    logging.info(response)
    return




def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        headers={'Content-Type':'application/json'}
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
            send_ack(mobile,'failed','request-invalid',ct)
            send_ack(mobile,'failed','request-invalid',ct)
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
            send_ack(mobile,'failed','unregistered',ct)
            send_ack(mobile,'failed','unregistered',ct)
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
            send_ack(mobile,'failed','invalid-ciphertext',ct)
            send_ack(mobile,'failed','invalid-ciphertext',ct)
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
        ackpin=params[4]
        #ackpin_o=ackpin
        if str(mobile)==str(receiver_mobile):
                body={}
                body['status']='error'
                body['message']='Invalid receiver mobile'
                send_ack(mobile,'failed','Invalid-receiver',ackpin)
                send_ack(mobile,'failed','Invalid-receiver',ackpin)
                return func.HttpResponse(
                    json.dumps(body),
                    status_code=200,
                    headers=headers
                )



        logging.info('getupi request')

        #if not transact.check_ack(mobile,ackpin):
        #        choices=['1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        #        listme=[random.choice(choices) for i in range(7)]
        #        ackpin=''.join(listme)
        
        receiver_upi,F=transact.get_upi(receiver_mobile)
        if not F:
            body={}
            body['status']='error'
            body['message']='Invalid receiver mobile'
            send_ack(mobile,'failed','Invalid-receiver',ackpin)
            send_ack(mobile,'failed','Invalid-receiver',ackpin)
            logging.info(body)
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers
            )
        
        logging.info('transfer request')
        success=transact.transfer(mobile,sender_upi,receiver_mobile,receiver_upi,amount,pin,'offline',ackpin)
        if success==0:
            
            body={}
            body['status']='succcess'
            body['message']='Transfer success'
            logging.info(body)
            send_ack(mobile,'success','Transfer-Successful',ackpin)
            send_ack(mobile,'success','Transfer-Successful',ackpin)
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers
            )
        elif success==1:
            body={}
            body['status']='error'
            body['message']='Incorrect upi pin'
            send_ack(mobile,'failed','incorrect-upipin',ackpin)
            send_ack(mobile,'failed','incorrect-upipin',ackpin)
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
            send_ack(mobile,'failed','low-balance',ackpin)
            send_ack(mobile,'failed','low-balance',ackpin)
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