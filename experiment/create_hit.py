import os
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion

ACCESS_ID = os.environ['AWS_ACCESS_KEY']
SECRET_KEY = os.environ['AWS_SECRET_KEY']
HOST = 'mechanicalturk.sandbox.amazonaws.com'

mtc = MTurkConnection(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        host=HOST)



