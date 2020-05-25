get_transactions='''
select phone,max(create_time) as create_time 
from (

select DISTINCT sender_phone as phone,dateadd(MINUTE ,30,dateadd(hour,5,create_time)) as create_time 
from data_logging.transaction_log tl
where receiver_phone ={0}
union ALL 
select DISTINCT receiver_phone as phone ,dateadd(MINUTE ,30,dateadd(hour,5,create_time)) as create_time
from data_logging.transaction_log tl
where sender_phone ={0}
) a
group by phone 
order by max(create_time) DESC 



'''