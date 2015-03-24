# -*- coding: utf-8 -*-
@auth.requires_login()
def index():
    Files.user_id.readable = False
    Files.random.readable = False
    form=SQLFORM(Files)
        
    if (form.process().accepted):
        response.flash = 'file added'
        redirect(URL())
    elif form.errors:
        response.flash = 'form has errors'

    rows = db(Files.user_id == me)
    selects = rows.select()
    count = rows.count()
    myfiles = []
    if count > 0:
        for row in selects:
            myfile = dict()
            myfile['title'] = row.title
            myfile['user_id'] = row.user_id
            myfile['file_url'] = row.file_url
            myfile['description'] = row.description
            myfile['random'] = row.random
            myfiles.append(myfile)
    
    return dict(form=form,
                files=myfiles)

def view():
    rows = db(Files.random == a0)
    row = rows.select().first()
    
    if row is None:
        raise HTTP(404, "This page does not exist or was removed!")
    else:
        num_views = row.views + 1
        row.update_record(views=num_views)
    
    is_owner = True if row.user_id == me else False
    is_logged_in = True if me is not None else False
    
    return dict(row=row,
                is_owner=is_owner,
                is_logged_in=is_logged_in,
                num_views=num_views)

def edit():
    rows = db(Files.random == a0)
    row = rows.select().first()
    
    file_url = row.file_url
    is_owner = True if row.user_id == me else False
    if not is_owner:
        raise HTTP(403)
    
    '''Files.title.default = row.title
    Files.descripion.default = row.description
    form=SQLFORM(Files)
    '''
    form=FORM(TABLE(
                    TR("Title:", INPUT(_type="text", _name="title", value=row.title)),
                    TR("Description:", TEXTAREA(_name="description", value=row.description)),
                    TR("", INPUT(_type="submit", _value="Submit"))))
    
    if form.accepts(request, session) & is_owner:
        row.update_record(description=form.vars.description, title=form.vars.title)
        redirect(URL('default', 'view', args=[a0]))
    
    return dict(form=form,
                file_url=file_url,
                is_owner=is_owner)

def delete():
    rows = db(Files.random == a0)
    row = rows.select().first()
    
    is_owner = True if row.user_id == me else False
    if is_owner:
        db(Files.random == a0).delete()
    else:
        raise HTTP(403)
        
    redirect(URL('default', 'index'))
    return dict()

def user(): return dict(form=auth())

@cache.action()
def download(): return response.download(request, db)

def call(): return service()

@auth.requires_signature()
def data(): return dict(form=crud())
