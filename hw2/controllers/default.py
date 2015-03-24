# -*- coding: utf-8 -*-

def index():
    response.title = "Task Maker"
    return dict()

""" Helper function for making similar SQLFORM.grids """
def make_task_grid(query, fields, links=None):
    return SQLFORM.grid(query,
                        fields=fields,
                        orderby=~Task.created_on,
                        searchable=False, create=False, editable=False, deletable=False, details=False,
                        paginate=5,
                        maxtextlength=1024,
                        csv=False,
                        links=links)

""" Display tasks assigned to the user in SQLFORM.grid(s) """
@auth.requires_login()
def my_tasks():
    response.title = "My Tasks"
    my_email = User[me].email # grab user's email address
    
    Task.assigner.readable = True
    fields = (Task.assigner, Task.title, Task.description)
    
    # task assigned to user, and has not been accepted.
    accept = ( (Task.assignee == my_email) & (Task.accepted == False) )
    
    if db(accept).count() > 0:
        # there are task's to be accepted show them in a grid
        accept_links=[
               dict(header=T('Accepted'),
                    body=lambda r: A(T('Accept'), _class='btn', _href=URL('default', 'accept_task', args=[r.id], user_signature=True))
                    ),
               dict(header=T('Rejected'),
                    body=lambda r: A(T('Reject'), _class='btn', _href=URL('default', 'reject_task', args=[r.id], user_signature=True))
                    )
               ]
        
        accept_grid = make_task_grid(accept, fields, accept_links)
        
    else:
        accept_grid = None    
            
    # task assigned to user, was accepted, and is marked 'not done'.        
    not_done = ( ( (Task.assignee == my_email) & (Task.done == False) ) & (Task.accepted == True) ) 
    
    if db(not_done).count() > 0:
        # there are task's that are not done yet, show them in a separate grid.
        not_done_links=[
               dict(header=T('Action'),
                    body=lambda r: A(T('Done'), _class='btn', _href=URL('default', 'toggle_done', args=[r.id], user_signature=True))
                    )
               ]
        
        not_done_grid = make_task_grid(not_done, fields, not_done_links)
        
    else:
        not_done_grid = None
     
    # task assigned to user, was accepted, and is marked 'done'.                
    done = ( ( (Task.assignee == my_email) & (Task.done == True) ) & (Task.accepted == True) ) 
    
    if db(done).count() > 0:
        # there are task's that are done, show them in a separate grid.
        done_links=[
               dict(header=T('Action'),
                    body=lambda r: A(T('Not Done'), _class='btn', _href=URL('default', 'toggle_done', args=[r.id], user_signature=True))
                    )
               ]
        
        done_grid = make_task_grid(done, fields, done_links) 
        
    else:
        done_grid = None
    
    return dict(not_done_grid=not_done_grid,
                done_grid=done_grid,
                accept_grid=accept_grid)

""" Display task's assigned by the user in an SQLFORM.grid """
@auth.requires_login()
def their_tasks():
    response.title = "Their Tasks"
    # grab user's email
    my_email = User[me].email
    
    # task's assigned by the user, but not assigned to the user.
    their_tasks = ( (Task.assigner == my_email) & (Task.assignee != my_email) ) 
    fields = (Task.assignee, Task.title, Task.description, Task.done)
    
    if db(their_tasks).count() > 0:
        # there are task's assigned by the user, show them in a grid.
        their_grid = make_task_grid(their_tasks, fields)
        
    else:
        their_grid= None
    
    return dict(their_grid=their_grid)

""" Toggle the status of the Task to either 'done' or 'not done' """
@auth.requires_signature()
def toggle_done():
    # get record from URL arg
    row = db(Task.id == a0).select().first()
    # get the status
    is_done = row.done
    # toggle and update the status
    row.update_record(done=not is_done)
    redirect(URL('default', 'my_tasks'))
        
    return dict()

""" Accept this Task. Function called by button in SQLFORM.grid link for unaccepted Task's """
@auth.requires_signature()
def accept_task():
    # get record from URL arg
    row = db(Task.id == a0).select().first()
    # accept the task
    row.update_record(accepted=True)
    redirect(URL('default', 'my_tasks'))

    return dict()

""" Reject this Task. Function also called by button in SQLFORM.grid link for unaccepted Task's """
@auth.requires_signature()
def reject_task():
    # get record from URL arg
    rows = db(Task.id == a0)
    # reject (delete) the task
    rows.delete()
    redirect(URL('default', 'my_tasks'))

    return dict()

""" Create a task for a user (by email address) """
@auth.requires_login()
def create_task():
    # Task is assigned by currently logged in user.
    Task.assigner.default = User[me].email
    # 'done' and 'accepted' fields should not be editable.
    Task.done.writable = Task.done.readable = False
    Task.accepted.writable = Task.accepted.readable = False
    
    form=SQLFORM(Task)
    form.add_button('Cancel', URL('default', 'index'))
    if form.process().accepted:
        if form.vars.assignee == User[me].email:
            # task was created for the user.
            session.flash = 'Task created for yourself!'
            row = db(Task.id == form.vars.id).select().first()
            # automatically accept this task, since it's for yourself.
            row.update_record(accepted=True)
            redirect(URL('default', 'my_tasks'))
        else:
            # task was created for another user.
            session.flash = 'Task created for ' + form.vars.assignee + "!"
            redirect(URL('default', 'their_tasks'))
            
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'
    
    return dict(form=form)

def user():
    response.title = "Task Maker"
    return dict(form=auth())

@cache.action()
def download():
    return response.download(request, db)

def call():
    return service()

@auth.requires_signature()
def data():
    return dict(form=crud())