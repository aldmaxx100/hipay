otp_verify='''
select count(1)
from service_master.otp_table
where mobile={0}
and otp={1}
and create_time BETWEEN dateadd(minute,-5,getdate()) and getdate() 
'''

insert_template='''
insert into funny_india_master.customer_account_master(accountid,phonenumber,balance,upiaddress,pin,sharedkey)
values({0},{1},20000,'{2}',{3},'{4}')

'''

select_record='''
select sharedkey,upiaddress
from funny_india_master.customer_account_master
where phonenumber={0}

'''