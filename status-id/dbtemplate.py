get_id_status='''
select status
from data_logging.transaction_log
where ackpin='{0}'
'''