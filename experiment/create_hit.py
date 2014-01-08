import os
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import Overview, Question, QuestionContent, QuestionForm, FormattedContent, AnswerSpecification, FreeTextAnswer, ExternalQuestion

ACCESS_ID = os.environ['AWS_ACCESS_KEY']
SECRET_KEY = os.environ['AWS_SECRET_KEY']
HOST = 'mechanicalturk.sandbox.amazonaws.com'

mtc = MTurkConnection(
        aws_access_key_id=ACCESS_ID,
        aws_secret_access_key=SECRET_KEY,
        host=HOST)


question_form = ExternalQuestion(external_url='https://murmuring-inlet-9267.herokuapp.com/', frame_height=800)
keywords=['boto', 'test', 'doctest']
create_hit_rs = mtc.create_hit(question=question_form, max_assignments=1,title="Boto External Question Test", keywords=keywords,reward = 0.05, duration=60*6,approval_delay=60*60)
assert(create_hit_rs.status == True)


