import logging
import azure.functions as func
from ..shared import transact
from . import dbtemplate
import json

def formatter(id_list):
    
    try:
        data=[]
        conn=transact.get_db_conn()
        cur=conn.cursor()
        for id in id_list:
            inter={}
            cur.execute(dbtemplate.get_id_status.format(id))
            res=cur.fetchall()
            if res[0][0]==1:
                status='incorrect pin'
            elif res[0][0]==0:
                status='success'
            elif res[0][0]==2:
                status='insufficent balance'
            else:
                status='pending'

            inter['id']=id
            inter['status']=status
            data.append(inter)
        
        return data
    except Exception as e:
        raise Exception('error in formatter func:'+str(e))
        

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    try:
        headers={'Content-Type':'application/json','Cache-Control':'no-store'}

        logging.info('Python HTTP trigger function processed a request.')
        
        try:
            req_body = req.get_json()
            id_list=req_body['id']
        except Exception as e:
            body={}
            body['status']='error'
            body['message']='body invalid'
            return func.HttpResponse(
                json.dumps(body),
                status_code=200,
                headers=headers            
                )
        data=formatter(id_list)
        body={}
        body['status']='success'
        body['data']=data
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