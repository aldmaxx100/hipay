import os
import boto3
accesskey=os.environ['accesskey']
secretkey=os.environ['secretkey']
dbusername =os.environ['dbusername']
dbpassword =os.environ['dbpassword']
smskey=os.environ['smskey']
session = boto3.Session(
        region_name="ap-south-1",
        aws_access_key_id=accesskey,
        aws_secret_access_key=secretkey
    )
sns_client = session.client('sns')