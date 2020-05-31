get_payments='''
select 
sender_phone,
sender_upi,
receiver_phone,
receiver_upi,
amount,
dateadd(minute,30,dateadd(hour,5,create_time)),
mode,
ackpin,
status
from data_logging.transaction_log tl 
where (sender_phone ={0} and receiver_phone ={1} and status=0)
or (sender_phone ={1} and receiver_phone ={0} and status=0)
order by create_time desc
'''