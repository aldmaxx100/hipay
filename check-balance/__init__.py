import logging
import json
import azure.functions as func
from . import dbtemplate
from ..shared import transact

def formatted(result,mobile):
    data=[]
    for r in result:
        inter={}
        if str(r[0])==str(mobile):
            inter['type']='debit'
            inter['phone']=r[2]
            inter['upi']=r[3]
            inter['amount']=r[4]
            inter['mode']=r[5]
            inter['time']=str(r[6])


        elif str(r[2])==str(mobile):
            inter['type']='credit'
            inter['phone']=r[0]
            inter['upi']=r[1]
            inter['amount']=r[4]
            inter['mode']=r[5]
            inter['time']=str(r[6])

        
        data.append(inter)





    return data


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        headers={'Content-Type':'application/json'}
        logging.info('Python HTTP trigger function processed a request.')
        mobile=req.params.get('mobile')
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
        cur.execute(dbtemplate.get_balance.format(mobile))
        result=cur.fetchall()
        balance=result[0][0]
        cur.execute(dbtemplate.get_log.format(mobile))
        result=cur.fetchall()
        data=formatted(result,mobile)
        body={}
        body['balance']=balance
        body['data']=data
        body['status']='success'

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