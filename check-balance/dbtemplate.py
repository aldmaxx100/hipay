get_balance='''
select balance 
from funny_india_master.customer_account_master
where phonenumber={0} 
'''

get_log='''
SELECT sender_phone ,
sender_upi ,
receiver_phone ,
receiver_upi ,amount ,mode ,
dateadd(MINute,30,dateadd(hour,5,create_time )) as ist_time
from data_logging.transaction_log tl
where (sender_phone ={0} or receiver_phone ={0})
and status=0
and create_time BETWEEN dateadd(day,-7,cast(getdate() as date)) and getdate()
order by create_time DESC 

'''