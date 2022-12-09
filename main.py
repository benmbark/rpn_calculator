import os
import uuid
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Resource, Api, marshal_with, fields


basedir = os.path.abspath(os.path.dirname(__file__))

# create the app
app = Flask(__name__)

# Api
api = Api(app)

# create the extension
db = SQLAlchemy(app)
# configure the SQLite database, relative to the app instance folder
app.config['SQLALCHEMY_DATABASE_URI'] =\
           'sqlite:///' + os.path.join(basedir, 'database.db')

# Models
class Stack(db.Model):
    __tablename__ = "stack"

    id = db.Column(db.String, primary_key=True, default= str(uuid.uuid4()))
    items = db.relationship('StackItem', backref='stack')

    def __repr__(self):
        return f'<Stack "{self.id}">'


class StackItem(db.Model):
    __tablename__ = "stack_item"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String)
    stack_id = db.Column(db.String, db.ForeignKey('stack.id'))

    def __repr__(self):
        return self.value

db.create_all()

#DTOs:

stack_fields = api.model('stack_fields', {
        'id': fields.String(),
        'items':  fields.List(fields.String(required=False),  example=[]),
    }, required=False)


# Views
@api.route('/stack/create')
class StackPost(Resource):
    @marshal_with(stack_fields)
    def post(self):
        stack = Stack()
        db.session.add(stack)
        db.session.commit()
        return stack


@api.route('/stack/<string:stack_id>')
class StackGetById(Resource):
    @marshal_with(stack_fields)
    def get(self, stack_id):
        stack = Stack.query.get(stack_id)
        return stack

@api.route('/stack/delete/<string:stack_id>')
class StackDeleteById(Resource):
    @marshal_with(stack_fields)
    def delete(self, stack_id):
        stack = Stack.query.get(stack_id)
        db.session.delete(stack)
        db.session.commit()
        return {'deleted': True,
                'stack_id': stack.id}

@api.route('/stack/list')
class StackGetAll(Resource):
    @marshal_with(stack_fields)
    def get(self):
        stacks = Stack.query.all()
        return stacks

@api.route('/stack/add_item')
class StackAddItemToStack(Resource):
    @marshal_with(stack_fields)
    @api.expect(stack_fields)
    def post(self):
        payload = request.get_json()
        #Validate payload:
        #Get stack:
        stack_id = payload.get('id')
        items = payload.get('items')
        if stack_id and items:
            stack = Stack.query.get(stack_id)
            for item in items:
                item = StackItem(value=int(item), stack=stack)
                db.session.add(item)
            db.session.add(stack)
            db.session.commit()
            return stack


app.run(debug=True)