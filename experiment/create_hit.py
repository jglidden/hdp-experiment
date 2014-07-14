import os
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import Overview, Question, QuestionContent, QuestionForm, FormattedContent, AnswerSpecification, FreeTextAnswer, ExternalQuestion
from boto.mturk.qualification import Requirement, Qualifications

ACCESS_ID = 'AKIAJGBULS6Q3DXYVK4Q'
SECRET_KEY = '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'
HOST = 'mturk.com'

mtc = MTurkConnection(
        aws_access_key_id=ACCESS_ID,
        aws_secret_access_key=SECRET_KEY,
        host=HOST)


ASSIGNMENTS = 2
DAYS = 5
QUALIFICATION_ID = '3SLCM7XLWH8WO61VD7YZPK4Q3U9T69'
for day in range(DAYS):
    requirements = []
    if day != 0:
        r = Requirement(QUALIFICATION_ID, 'EqualTo', day)
        requirements.append(r)
    worker_percent_assignments_approved = Requirement("000000000000000000L0", 'EqualTo', 95)
    requirements.append(worker_percent_assignments_approved)

    title = 'Hierarchical Categorization Learning {0}'.format(day)
    question_form = ExternalQuestion(external_url='https://fruitexp.dreamhosters.com', frame_height=1000)
    keywords=['psychology', 'experiment', 'categorization', 'learning', 'pictures']
    description='Learn a hierchary of categories by iterated guessing'
    create_hit_rs = mtc.create_hit(
            question=question_form,
            max_assignments=2,
            title=title,
            keywords=keywords,
            description=description,
            reward=3.00+day*.50,
            duration=2*60*60,
            lifetime=5*24*60*60,
            qualifications=Qualifications(requirements))
    assert(create_hit_rs.status == True)


