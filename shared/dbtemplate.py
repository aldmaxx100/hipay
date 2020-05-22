get_key='''
select sharedkey
from funny_india_master.customer_account_master
where upi='{0}'
'''

check_req='''
select count(1)
from data_logging.requests
where payload='{0}'
and iv='{1}'
and phonenumber={2}

'''

req_insert='''
insert into data_logging.requests
values('{0}','{1}',{2},getdate())
'''

transaction_insert='''
insert into data_logging.transaction_log
values({0},'{1}',{2},'{3}',{4},getdate())
'''


get_upi='''

select upi 
from funny_india_master.customer_account_master
where phonenumber={0}

'''

debit_fund='''
update funny_india_master.customer_account_master
set balance=balance-{0}
where upi='{1}'
'''

credit_fund='''

update funny_india_master.customer_account_master
set balance=balance+{0}
where upi='{1}'

'''
