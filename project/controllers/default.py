from contrib import simplejson as json
import math

def index():
    response.subtitle = "Welcome!"
    logged_in = True if auth.user_id is not None else False
    row = db(Students.student == me).select().first()
    
    if (logged_in and row is None):
        # user's info not found, first time login
        Students.insert(student=me)
        redirect(URL('default', 'index'))
    
    # user is a student if not a tutor, and found in Student table
    is_registered = True if row is not None else False
    if is_registered:
        is_tutor = row.is_tutor
    else:
        is_tutor = False
    
    return dict(is_tutor=is_tutor)

def about():
    return dict()

""" Display all subjects in categories. """
def find_tutor():
    rows = db((Subjects.id > 0) & (Students.subjects.contains(Subjects.id)))
    count = rows.count()
    response.subtitle = "Find a tutor"
    query = (Categories.id > 0)
    grid = SQLFORM.grid(query,
        searchable=False,
        fields=[Categories.title],
        csv=False, 
        details=False, create=False, editable=False, deletable=False,
        paginate=10,
        maxtextlength=100,
    )

    return dict(grid=grid, count=count)

""" Display all categories of subjects. """
def category():
    category_id = request.vars.id
    if category_id is None: redirect(URL('default', 'find_tutor'))
    response.subtitle = Categories[category_id].title + " Subjects"
    query = ((Subjects.category == category_id) & (Subjects.num_tutors > 0))
    grid = SQLFORM.grid(query,
        searchable=False,
        fields=[Subjects.title, Subjects.num_tutors],
        csv=False, 
        details=False, create=False, editable=False, deletable=False,
        paginate=20,
        maxtextlength=100,
    )
    
    return dict(grid=grid)

""" Display all tutors of this subject. """
def subject():
    
    subject_id = request.vars.id
    if subject_id is None: redirect(URL('default', 'find_tutor'))
    response.subtitle = Subjects[subject_id].title + " Tutors"
    Students.phone_number.readable = Students.is_tutor.readable = False
    Students.subjects.readable = Students.rating.readable = True
    
    # select registered tutors
    query = ((Students.is_tutor == True) & (Students.subjects.contains(subject_id)))
    fields = [Students.name, Students.description, Students.rating, Students.student]
    grid = SQLFORM.grid(query,
        searchable=False,
        fields=fields,
        csv=False, 
        details=False, create=False, editable=False, deletable=False,
        paginate=10,
        maxtextlength=100,
    )
    
    back = Subjects[subject_id].category
    
    return dict(grid=grid, back=back)

""" Update student to being a tutor. """
@auth.requires_login()
def be_tutor():
    row = db(Students.student == me).select().first()
    logged_in = True if auth.user_id is not None else False
    
    if (logged_in and row is None):
        # user's info not found, first time login
        Students.insert(student=me)
        new_row = db(Students.student == me).select().first()
        new_row.update_record(is_tutor=True)
        redirect(URL('default', 'edit_profile', args=[me], user_signature=True))
    
    if row is not None:
        if (row.is_tutor == True):
            session.flash = "You are already a tutor!"
            redirect(URL('default', 'profile', args=[me]))
        else:
            session.flash = "Congrats! You are now a tutor."
            row.update_record(is_tutor=True)
            redirect(URL('default', 'edit_profile', args=[me], user_signature=True))
        
    return dict()

""" Rate the tutor, called from Ajax on Profile page. """
def rate_tutor():
    value = float(request.vars.value)
    rater = int(request.vars.rater)
    ratee = int(request.vars.ratee)
    print value
    row = db(Students.student == int(ratee)).select().first()
    if row is not None:
        old_rating = row.rating
        old_rating_points = old_rating * row.num_ratings
        print old_rating_points
        new_num_ratings = row.num_ratings + 1
        print new_num_ratings
        new_rating = (old_rating_points + int(value)) / new_num_ratings
        print new_rating
        Ratings.insert(rater=int(rater), ratee=int(ratee), rating=int(value))
        row.update_record(rating=new_rating, num_ratings=new_num_ratings)
    
    return dict()
    
""" Display a student or tutor's profile.
    if it is your own profile, display tutoring
    requests and conversations with students or tutors. """
def profile():
    info = db(Students.student == a0).select().first() or redirect(URL('default', 'index'))
    student_of_rows = db((Messages.accepted == True) & ((Messages.author == me) & (Messages.recipient == a0)))
    has_rated_rows = db((Ratings.ratee == a0) & (Ratings.rater == me))
    has_requested_rows = db((Messages.accepted == False) & ((Messages.author == me) & (Messages.recipient == a0)))
    
    response.subtitle = get_name(info.student) + "'s profile"
    is_owner = True if info.student == me else False
    is_student_of = True if student_of_rows.count() > 0 and not is_owner else False
    has_rated = True if has_rated_rows.count() > 0 else False
    has_requested = True if has_requested_rows.count() > 0 else False
    
    if is_owner:
        # this is my profile, show me pending requests, and my conversations
        pending_query = (Messages.accepted == False) & ((Messages.recipient == me) | (Messages.author == me))
        pending_requests = db(pending_query).select()
        
        convos_query = (Messages.accepted == True) & (Messages.recipient == me)
        convos_with = db(convos_query).select(Messages.author, Messages.recipient, distinct=True)
    else:
        # not my profile, don't show me any private info
        pending_requests = None
        convos_with = None
    
    if(info.num_ratings > 0):
        floor_rating = math.floor(info.rating/info.num_ratings)
        left_over = (info.rating/info.num_ratings) - floor_rating
    else:
        floor_rating = left_over = None

    my_tutors = student_of_rows.select(Messages.author, distinct=True)
    
    return dict(info=info,
                is_owner=is_owner,
                is_student_of=is_student_of,
                has_requested=has_requested,
                my_tutors=my_tutors,
                has_rated=has_rated,
                floor_rating=floor_rating,
                left_over=left_over,
                pending_requests=pending_requests,
                convos_with=convos_with,
                )

""" Edit my profile. (tutors only) """
@auth.requires_signature()
def edit_profile():
            
    """ Trim spaces, parens, and dashes from phone number. """
    def trim_phone_number(form):
        form.vars.phone_number = form.vars.phone_number.translate(None, "- ()")
    
    record = db(Students.student == a0).select().first() or redirect(URL('default', 'index'))
    response.subtitle = "Editing My Profile"
    
    data = dict()
    data['description'] = record.description
    data['phone_number'] = record.phone_number
    data['hour_rate'] = record.hourly_rate
    data['half_hour'] = record.does_half_hour
    data['my_subjects'] = record.subjects
    
    is_new = True if record.subjects == None else False

    subjects = db().select(Subjects.ALL)
    """if (data['my_subjects'] is not None):
        for subject in data['my_subjects']:
            subjects.exclude(lambda row: row.id == subject.id)
    """
    categories = db().select(Categories.ALL)
    
    return dict(subjects=subjects, categories=categories, is_new=is_new, data=data)

""" Update tutor's profile. AJAX call from 'edit_profile' page. """
def update_profile():
    session.flash = "Profile updated!"
    description = request.vars.description
    phone = request.vars.phone
    rate = request.vars.rate
    half_hour = request.vars.half_hour
    subjects = json.loads(request.vars.subject_list)
    int_subjects = []
    for subject in subjects:
        int_subjects.append(int(subject))
        subject_row = db(Subjects.id == subject).select().first()
        new_count = subject_row.num_tutors + 1
        subject_row.update_record(num_tutors = new_count)

    tutor_row = db(Students.student == me).select().first()
    
    tutor_row.update_record(description=description, phone_number=phone, hourly_rate=rate, does_half_hour=half_hour)
    if subjects: tutor_row.update_record(subjects=int_subjects)
            
    return dict()

""" Request tutoring from a tutor. """
@auth.requires_login()
def request_tutoring():
    record = db(Students.student == a0).select().first() or redirect(URL('default', 'index'))
    response.subtitle = "Request Tutoring from " + record.name
    Messages.recipient.default = record.student
    Messages.author.default = me
    
    form = SQLFORM(Messages, labels=dict(body=''))
    form.add_button('Back', URL('default', 'profile', args=[a0]))
    
    if form.process().accepted:
        session.flash = "Request sent!"
        redirect(URL('default', 'profile', args=[a0]))
    elif form.errors:
        response.flash = "form has errors"
        
    return dict(form=form)

""" View a student's tutoring request. (tutors only) """
@auth.requires_signature()
def view_request():
    selects = db((Messages.author == a0) & (Messages.recipient == a1)).select()
    first = selects.first()
    
    response.subtitle = "Viewing " + get_name(first.author) + "'s Tutoring Request"
    can_accept = True if User[a1].id == me else False
    
    return dict(selects=selects, can_accept=can_accept)

""" Accept a student's tutoring request. (tutors only) """
@auth.requires_signature()
def accept_request():
    requests = db((Messages.author == a0) & (Messages.recipient == a1))
    requests.update(accepted=True)
    
    redirect(URL('default', 'view_conversation', args=[a0, a1], user_signature=True))
    
    return dict()

""" Parse incoming email from IMAP inbox, add to conversation """
def parse_emails():
    emails = []

    q = imapdb.INBOX.seen == False
    rows = imapdb(q).select()
    for row in rows:
        email = dict()
        email['sender'] = row.sender
        email['subject'] = row.subject
        body_index = row.content[0]['text'].find('\r\n\r\n')
        email['body'] = row.content[0]['text'][:body_index]
        subject_index = row.subject.find('-')
        email['conversation_id'] = row.subject[subject_index+1:]
        emails.append(email)
        row.update_record(seen=True)
        
        id_index = email['conversation_id'].find('-')
        who_from = email['conversation_id'][:id_index]
        who_to = email['conversation_id'][id_index+1:]
        Messages.insert(author=who_from, recipient=who_to, body=email['body'], accepted=True)

""" View conversation between you and the student or tutor. """
@auth.requires_signature()
def view_conversation():
    # uncomment this to parse incoming email messages        
    #emails = parse_emails()
    # remove this too
    emails = None
    
    query = ((Messages.accepted == True)
             & ((Messages.author == a0) & (Messages.recipient == a1))
             | ((Messages.author == a1) & (Messages.recipient == a0))
            ) 
    convo = db(query).select(orderby=~Messages.create_date) or redirect(URL('default', 'profile', args=[a1]))
    
    # get id of user I am conversing with
    not_me = a0 if (User[a1].id == me) else a1
    
    response.subtitle = "Your conversation with " + get_name(not_me)
    
    Messages.recipient.default = User[not_me].id
    Messages.author.default = me
    Messages.accepted.default = True
    
    form = SQLFORM(Messages, labels=dict(body=''))
    form.add_button('Back', URL('default', 'profile', args=[a1]))
    
    # uncomment these to add back emailing of message functionality
    #send_to = User[not_me].email
    #subject = "New message from " + get_name(me) + " in Conversation-"+a0+"-"+a1 # need a better way to pass the conversation id's
    
    if form.process().accepted:
        body = form.vars.body
        
        #if(mail.send(to="ajolicoe@ucsc.edu", subject=subject, message=body)):
        #    session.flash = "Message sent, and emailed: " + send_to
        #else:
        session.flash = "Message sent!"
        
        redirect(URL('default', 'view_conversation', args=[a0, a1], user_signature=True))
    elif form.errors:
        response.flash = "form has errors"
    
    return dict(convo=convo, form=form, emails=emails)

def user(): return dict(form=auth())

@cache.action()
def download(): return response.download(request, db)

def call(): return service()

@auth.requires_signature()
def data(): return dict(form=crud())