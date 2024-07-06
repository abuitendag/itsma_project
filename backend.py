from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


# initialise and connect to db
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskkeeper.db'
db = SQLAlchemy(app)

# allow for comms from different ports
CORS(app)

# task model
class TaskKeeper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Task {self.id}>'

# create the database tables (only create db table when api runs)
with app.app_context():
    db.create_all()

# routes
@app.route('/api/tasks', methods=['GET', 'POST'])

# endpoint, retrieve data with get method, return in JSON or
def tasks():
    if request.method == 'GET':
        tasks = TaskKeeper.query.all()
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'completed': task.completed
            })
        return jsonify({'tasks': task_list})
    
# receive data in JSON, creates new task and adds to db with post
    elif request.method == 'POST':
        data = request.json
        title = data['title']
        description = data.get('description', '')
        
        new_task = TaskKeeper(title=title, description=description)
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify({'message': 'Task created'}), 201

# endpoint, manage tasks in db with get, put, delete methods
@app.route('/api/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_task(task_id):
    task = TaskKeeper.query.get_or_404(task_id)

# return details in JSON
    if request.method == 'GET':
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed
        })
    
# update task from JSON
    elif request.method == 'PUT':
        data = request.json
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.completed = data.get('completed', task.completed)
        
        db.session.commit()
        return jsonify({'message': 'Task updated'})
    
# delete task
    elif request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted'})

# using different port to frontend, comms facilitated with CORS
if __name__ == '__main__':
    app.run(port=5000,debug=True)