import logging
import json
import azure.functions as func
from . import dbtemplate
from ..shared import transact


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        headers={'Content-Type':'application/json','Cache-Control':'no-store'}
        logging.info('Python HTTP trigger function processed a request.')

        m1 = req.params.get('m1')
        m2=req.params.get('m2')
        if not m1 or not m2:
            body={}
            body['status']='error'
            body['message']='m1 or m2 param missing'
            return func.HttpResponse(
             json.dumps(body),
             status_code=200,
             headers=headers
             )
        conn=transact.get_db_conn()
        cur=conn.cursor()
        cur.execute(dbtemplate.get_payments.format(m1,m2))
        res=cur.fetchall()
        data=[]
        for r in res:
            inter={}
            inter['sender_phone']=r[0]
            inter['sender_upi']=r[1]
            inter['receiver_phone']=r[2]
            inter['receiver_upi']=r[3]
            inter['amount']=r[4]
            inter['create_time']=str(r[5])
            inter['mode']=r[6]
            inter['id']=r[7]
            if r[8]==0:
                inter['status']='success'
            
            elif r[8]==1:
                inter['status']='incorrect pin'
            
            elif r[8]==2:
                inter['status']='insufficient balance'
            
            data.append(inter)
        body={}
        body['status']='success'
        body['data']=data
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
