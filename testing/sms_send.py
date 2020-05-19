# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = 'AC1d2df8994d4554d98626f7d0ec09bad1'
auth_token = '74ee91fc30b25e0b61615d14b7ca4d4c'
client = Client(account_sid, auth_token)

message = client.messages \
    .create(
         body="Your code for HiPAY is 333666",
         messaging_service_sid='MG7542ddd67230e5fb3984182107c5d93e',
         to='+917709744778'
     )

print(message.sid)
