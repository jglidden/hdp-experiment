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


#
#overview = Overview()
#overview.append_field('Title', 'Psychology Experiment')
#overview.append(FormattedContent('<a target="_blank"'
#                                 ' href="http://murmuring-inlet-9267.herokuapp.com/">'
#                                 ' Click me</a>'))
#
#question_content = QuestionContent()
#question_content.append_field('Title','Your personal comments')
# 
#fta = FreeTextAnswer()
# 
#question = Question(identifier="comments",
#              content=question_content,
#              answer_spec=AnswerSpecification(fta))
#
#question_form = QuestionForm()
#question_form.append(overview)
#question_form.append(question)
question_form = ExternalQuestion(external_url='https://cocosci-cat-789.herokuapp.com/', frame_height=800)
keywords=['boto', 'test', 'doctest']
create_hit_rs = mtc.create_hit(question=question_form, max_assignments=10,title="Categorization Experiment", keywords=keywords,reward = 0.05, duration=60*6,approval_delay=60*60)
assert(create_hit_rs.status == True)


