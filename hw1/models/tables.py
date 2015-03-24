import random

db.define_table(
    'files',
    Field('user_id', db.auth_user, default=auth.user_id),
    Field('title', 'string', length=64),
    Field('file_url', 'upload', uploadfield='file_content', requires=IS_NOT_EMPTY(error_message='No file path given')),
    Field('file_content', 'blob'),
    Field('description', 'text'),
    Field('random', 'string', default=str(random.getrandbits(60)), unique=True),
    Field('views', 'integer', default=0),
)
        
db.files.user_id.writable = False
db.files.views.writable = db.files.views.readable = False
db.files.random.writable = False

Files = db.files
me = auth.user_id
a0, a1 = request.args(0), request.args(1)