from datetime import date
import os
import sys
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
sys.path.append(os.path.relpath('../../../../app/'))
import app
app = app.app

app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app)
db.init_app(app)
app_ctxt = app.app_context().push()
current_app.name
db.create_all()

'''SQL Setup'''
def run():
    class name_node(db.Model):
        node_num = db.Column(db.Integer, primary_key = True)
        name = db.Column(db.String(120))
        child = db.Column(db.Integer)
        mtime = db.Column(db.Integer)

    db.create_all()
    db.session.commit()
    test = name_node(node_num = 2, name = 'test', child = 3, mtime = date.today())
    db.session.add(test)
    db.session.commit()
