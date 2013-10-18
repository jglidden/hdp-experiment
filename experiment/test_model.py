import app

participant = app.Participant('test')
user = app.User(participant)
user.finish_session()
assert len(user.participant.sessions) > 1

