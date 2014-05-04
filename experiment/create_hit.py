import os
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import Overview, Question, QuestionContent, QuestionForm, FormattedContent, AnswerSpecification, FreeTextAnswer, ExternalQuestion
from boto.mturk.qualification import Requirement, Qualifications

ACCESS_ID = os.environ['AWS_ACCESS_KEY']
SECRET_KEY = os.environ['AWS_SECRET_KEY']
HOST = 'mechanicalturk.sandbox.amazonaws.com'

mtc = MTurkConnection(
        aws_access_key_id=ACCESS_ID,
        aws_secret_access_key=SECRET_KEY,
        host=HOST)


ASSIGNMENTS = 2
DAYS = 2
QUALIFICATION_ID = '3VZVROTBN6J8Q5O3BFCWBA48H0P9XY'
for day in range(DAYS):
    requirements = []
    if day != 0:
        r = Requirement(QUALIFICATION_ID, 'EqualTo', day)
        requirements.append(r)
    title = 'Categorization Experiment Day {0}'.format(day)
    question_form = ExternalQuestion(external_url='https://fruitexp.dreamhosters.com', frame_height=1000)
    keywords=['boto', 'test', 'doctest']
    create_hit_rs = mtc.create_hit(question=question_form, max_assignments=2,title=title, keywords=keywords,reward = 0.05, duration=60*6, qualifications=Qualifications(requirements))
    assert(create_hit_rs.status == True)


