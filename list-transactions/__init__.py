import logging
import json
from ..shared import transact
from . import dbtemplate
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        headers={'Content-Type':'application/json','Cache-Control':'no-store'}

    
        logging.info('Python HTTP trigger function processed a request.')

        mobile = req.params.get('mobile')
        if not mobile:
            body={}
            body['status']='error'
            body['message']='mobile param missing'
            return func.HttpResponse(
            json.dumps(body),
            status_code=200,
            headers=headers
            )
        conn=transact.get_db_conn()
        cur=conn.cursor()
        cur.execute(dbtemplate.get_transactions.format(mobile))
        result=cur.fetchall()
        data=[]
        for r in result:
            data.append({'phone':r[0],'upiaddress':r[2],'create_time':str(r[1])})
        
        body={}
        body['status']='success'
        body['message']='list retrieved success'
        body['data']=data

        return func.HttpResponse(
            json.dumps(body),
            headers=headers,
            status_code=200
            )
    except Exception as e:
        logging.info(str(e))
        return func.HttpResponse(
            json.dumps(body),
            status_code=500,
            headers=headers
            )
