# -*- coding: utf-8 -*-
import simplejson as json

def index():
    return dict()

def part_one():
    response.title = "Presidents"
    presidents = db().select(db.presidents.ALL, orderby=~db.presidents.current_count)
    return dict(presidents=presidents)

def part_one_nice():
    response.title = "Presidents"
    response.subtitle = "in an SQLFORM.grid"
    fields = [db.presidents.current_count, db.presidents.name]
    grid = SQLFORM.grid(db.presidents,
                        orderby=~db.presidents.current_count,
                        fields=fields,
                        searchable=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        csv=False,
                        )
    return dict(grid=grid)

def part_two():
    response.title = "Presidents"
    response.subtitle = "put them in the correct order!"
    presidents = db().select(db.presidents.ALL, orderby='<random>')
    return dict(presidents=presidents)

def inc_president():
    p_id = int(request.vars.id)
    president = db(db.presidents.id == p_id).select().first()
    new_count = president.current_count + 1
    president.update_record(current_count=new_count)
    session.flash = "+1 to " + president.name
    
    return dict()

def dec_president():
    p_id = int(request.vars.id)
    president = db(db.presidents.id == p_id).select().first()
    new_count = president.current_count - 1
    if new_count < 0:
        session.flash = "Cannot decrement below 0!"
        new_count = 0
    else:
        session.flash = "-1 to " + president.name
    president.update_record(current_count=new_count)
    
    return dict()

def test_order():
    order = request.vars.order
    correct = db().select(db.presidents.ALL, orderby=db.presidents.id)
    correct_order = []
    for president in correct:
        correct_order.append(president.name)
    
    win = json.loads(order) == correct_order
    if (win):
        print "YOU WIN!"
        response.flash = "YOU WIN!"
        
    return response.json(dict(result=win))

def user():
    return dict(form=auth())

@cache.action()
def download():
    return response.download(request, db)

def call():
    return service()

@auth.requires_signature()
def data():
    return dict(form=crud())
