get_key='''
select sharedkey
from funny_india_master.customer_account_master
where phonenumber='{0}'
'''

check_req='''
select count(1)
from data_logging.requests
where payloads='{0}'
and iv='{1}'
and phonenumber={2}

'''

req_insert='''
insert into data_logging.requests
values('{0}','{1}',{2},getdate())
'''

transaction_insert='''
insert into data_logging.transaction_log
values({0},'{1}',{2},'{3}',{4},getdate(),'{5}')
'''


get_upi_db='''

select upiaddress
from funny_india_master.customer_account_master
where phonenumber={0}

'''

debit_fund='''
update funny_india_master.customer_account_master
set balance=balance-{0}
where upiaddress='{1}'
'''

credit_fund='''

update funny_india_master.customer_account_master
set balance=balance+{0}
where upiaddress='{1}'

'''

get_amount='''
select balance
from funny_india_master.customer_account_master
where phonenumber={0} and pin={1} and upiaddress='{2}'
'''
