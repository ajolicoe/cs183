from datetime import datetime

db.define_table('task',
    Field('assigner', 'string'),
    Field('assignee', 'string'),
    Field('title', 'string', length=64),
    Field('description', 'text'),
    Field('done', 'boolean', default=False),
    Field('accepted', 'boolean', default=False),
    Field('created_on', 'datetime', default=datetime.utcnow()),
)

db.task.assigner.writable = db.task.assigner.readable = False
db.task.created_on.writable = db.task.created_on.readable = False
db.task.assignee.requires = db.task.assigner.requires = [IS_EMAIL(), IS_IN_DB(db, 'auth_user.email')]

User, Task = db.auth_user, db.task
me = auth.user_id
a0, a1 = request.args(0), request.args(1)