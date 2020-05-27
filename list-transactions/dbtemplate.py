get_transactions='''
select phone,max(create_time) as create_time,upiaddress
from (

select DISTINCT sender_phone as phone,receiver_upi as upiaddress,dateadd(MINUTE ,30,dateadd(hour,5,create_time)) as create_time 
from data_logging.transaction_log tl
where receiver_phone ={0}
union ALL 
select DISTINCT receiver_phone as phone,sender_upi as upiaddress,dateadd(MINUTE ,30,dateadd(hour,5,create_time)) as create_time
from data_logging.transaction_log tl
where sender_phone ={0}
) a
group by phone,upiaddress
order by max(create_time) DESC 



'''