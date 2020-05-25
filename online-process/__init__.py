import logging
import json
import random
import azure.functions as func
from ..shared import transact


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        headers={'Content-Type':'application/json'}
        logging.info('Python HTTP trigger function processed a request.')

        mobile = req.params.get('mobile')
        req_body = req.get_json()
        iv=req_body.get('iv')
        ct=req_body.get('ct')


        if not ct or not mobile or not iv:
            body={}
            body['status']='error'
            body['message']='ct or iv or mobile parameter missing'
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers
            )
        else:
            logging.info('check req')
            if not transact.check_request(ct,iv,mobile):
                body={}
                body['status']='error'
                body['message']='invalid request..request already used'
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
            logging.info('check same send')
            if str(mobile)==str(receiver_mobile):
                body={}
                body['status']='error'
                body['message']='Invalid receiver mobile'
                return func.HttpResponse(
                    json.dumps(body),
                    status_code=200,
                    headers=headers
                )

            
            #if not transact.check_ack(mobile,ackpin):
            #    choices=['1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
            #    listme=[random.choice(choices) for i in range(7)]
            #    ackpin=''.join(listme)
                

            logging.info('getupi request')

            receiver_upi,F=transact.get_upi(receiver_mobile)
            if not F:
                body={}
                body['status']='error'
                body['message']='Invalid receiver mobile'
                return func.HttpResponse(
                    json.dumps(body),
                    status_code=200,
                    headers=headers
                )
            
            logging.info('transfer request')
            success=transact.transfer(mobile,sender_upi,receiver_mobile,receiver_upi,amount,pin,'online',ackpin)
            if success==0:
                
                body={}
                body['status']='success'
                body['message']='Transfer success'
                body['id']=ackpin
                return func.HttpResponse(
                    json.dumps(body),
                    status_code=200,
                    headers=headers
                )
            elif success==1:
                body={}
                body['status']='error'
                body['message']='Incorrect upi pin'
                body['id']=ackpin
                return func.HttpResponse(
                    json.dumps(body),
                    status_code=200,
                    headers=headers
                )
            elif success==2:
                body={}
                body['status']='error'
                body['message']='Insuffcient Balance'
                body['id']=ackpin
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