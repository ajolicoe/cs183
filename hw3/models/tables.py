from datetime import datetime

db.define_table('presidents',
    Field('name'),
    Field('current_count', 'integer', default=0),
    Field('created_on', 'datetime', default=datetime.utcnow()),
)