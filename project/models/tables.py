from datetime import datetime

""" Get name of current logged in user """
def get_my_name():
    if auth.user_id == None: return None
    else:
        return db.auth_user[auth.user_id].first_name.capitalize() + " " + db.auth_user[auth.user_id].last_name.capitalize()

""" Get name of a user by user_id """
def get_name(user_id):
    if db.auth_user[user_id] is None: return None
    else:
        return db.auth_user[user_id].first_name.capitalize() + " " + db.auth_user[user_id].last_name.capitalize()
    
""" Get title of subject by subject_id """
def get_subject_title(subject_id):
    if db.subjects[subject_id] is None: return None
    else:
        return db.subjects[subject_id].title
    
db.define_table('categories',
    Field('title', 'string'),
    Field('create_date', 'datetime', default=datetime.utcnow()),
    format='%(title)s'
)
""" Categories constraints """
db.categories.create_date.writable = db.categories.create_date.readable = False

""" Represent subject's title as link to list of that subject's tutors. """
def represent_category_title(v, r): return A(v, _href=URL('default', 'category', vars=dict(id=r.id)))

db.categories.title.represent = represent_category_title
db.categories.title.label = "Category"

db.define_table('subjects',
    Field('title', 'string'),
    Field('create_date', 'datetime', default=datetime.utcnow()),
    Field('category', 'reference categories'),
    Field('num_tutors', 'integer', default=0),
    format='%(title)s'
)
""" Subjects constraints """
db.subjects.create_date.writable = db.subjects.create_date.readable = False

""" Represent subject's title as link to list of that subject's tutors. """
def represent_subject_title(v, r): return A(v, _href=URL('default', 'subject', vars=dict(id=r.id)))

db.subjects.title.represent = represent_subject_title
db.subjects.title.label = "Subject"

db.define_table('students',
    Field('student', db.auth_user, default=auth.user_id, unique=True),
    Field('is_tutor', 'boolean', default=False),
    Field('name', 'string', default=get_my_name()),
    Field('create_date', 'datetime', default=datetime.utcnow()),
    Field('description', 'text'),
    Field('phone_number', 'string', requires=IS_MATCH('^1?^(\(?\d{3}\)|\d{3})[- ]?\d{3}[- ]?\d{4}$',
         error_message='not a valid phone number')),
    Field('rating', 'double', default=0),
    Field('hourly_rate', 'double', default=None),
    Field('does_half_hour', 'string', requires=IS_IN_SET(['No', 'Yes'], zero=None)),
    Field('subjects', 'list:reference subjects'),
    Field('num_ratings', 'integer', default=0),
)
""" Student constraints """
db.students.id.writable = db.students.id.readable = False
db.students.student.writable = db.students.student.readable = False
db.students.create_date.writable = db.students.create_date.readable = False
db.students.rating.writable = db.students.rating.readable = False
db.students.num_ratings.writable = db.students.num_ratings.readable = False

""" Represent tutor's name as link to their profile. (in find_tutor) """
def represent_student_name(v, r): return A(v, _href=URL('default', 'profile', args=[r.student]))

db.students.name.represent = represent_student_name

db.define_table('ratings',
    Field('rater', db.auth_user),
    Field('ratee', db.auth_user),
    Field('create_date', 'datetime', default=datetime.utcnow()),
    Field('rating', 'double', default=0),
)
""" Rating constraints """
db.ratings.id.writable = db.ratings.id.readable = False
db.ratings.rater.writable = db.ratings.rater.readable = False
db.ratings.create_date.writable = db.ratings.create_date.readable = False

db.define_table('messages',
    Field('author', db.auth_user),
    Field('recipient', db.auth_user),
    Field('create_date', 'datetime', default=datetime.utcnow()),
    Field('body', 'text', requires=IS_NOT_EMPTY()),
    Field('accepted', 'boolean', default=False),
)
""" Message constraints """
db.messages.id.writable = db.messages.id.readable = False
db.messages.author.writable = db.messages.author.readable = False
db.messages.recipient.writable = db.messages.recipient.readable = False
db.messages.create_date.writable = db.messages.create_date.readable = False
db.messages.accepted.writable = db.messages.accepted.readable = False

# uncomment to use emailing messages functionality
# Set port as 993 for ssl support
#imapdb = DAL("imap://slugtutors@gmail.com:slug4lyfe@imap.gmail.com:993", pool_size=1)

# You need this command to access the server mailboxes CRUD
#imapdb.define_tables()

""" Table Shortcuts """
User, Students, Categories = db.auth_user, db.students, db.categories
Subjects, Messages, Ratings = db.subjects, db.messages, db.ratings

""" Variable/Argument Shortcuts """
me = auth.user_id
a0, a1 = request.args(0), request.args(1)

""" Custom menu """
if auth.user_id is not None:
    is_tutor_rows = db((db.students.student == auth.user_id) & (db.students.is_tutor == True))
    is_tutor = True if is_tutor_rows.count() > 0 else False
    if not is_tutor:
        response.menu.append((T('Be Tutor'), False, URL('default', 'be_tutor'), []))
    
    response.menu.append((T('Profile'), False, URL('default', 'profile', args=[auth.user_id]), []))

response.menu.append((T('About'), False, URL('default', 'about'), []))    
