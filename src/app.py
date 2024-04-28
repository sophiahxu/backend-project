from db import Course, User, Assignment, db
from flask import Flask, request
import json

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

# generalized response formats
def success_response(data, code=200):
    return json.dumps({"success": True, "courses": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

# your routes here
#get all courses
@app.route('/api/courses/', methods=['GET'])
def get_courses():
    courses = [t.serialize() for t in Course.query.all()]
    return success_response(courses)

#create a course
@app.route("/api/courses/", methods=["POST"])
def create_course():
    body = json.loads(request.data)
    if not body or "code" not in body or "name" not in body:
        return failure_response("Code or name missing!", 400)
    
    new_course = Course(code=body['code'], name=body['name'])
    db.session.add(new_course)
    db.session.commit()
    return json.dumps(new_course.serialize()), 201

#get a specific course
@app.route("/api/courses/<int:course_id>/", methods=["GET"])
def get_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    
    return json.dumps(course.serialize()), 200

#delete a course
@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Task not found!")
    
    db.session.delete(course)
    db.session.commit()
    return json.dumps(course.serialize()), 200

# Create a new user
@app.route('/api/users/', methods=['POST'])
def create_user():
    body = json.loads(request.data)
    if not body or 'name' not in body or 'netid' not in body:
        return failure_response("Missing required fields: name and netid", 400)

    new_user = User(name=body['name'], netid=body['netid'])
    db.session.add(new_user)
    db.session.commit()

    return json.dumps(new_user.serialize()), 201

# Get a specific user
@app.route('/api/users/<int:user_id>/', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return failure_response("User not found")

    return json.dumps(user.serialize()), 200

# Add a user to a course
@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def add_user_to_course(course_id):
    body = json.loads(request.data)
    if not body or 'user_id' not in body or 'type' not in body:
        return failure_response("Missing required fields: user_id or type", 400)

    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return failure_response("Course not found", 404)

    user = User.query.get(body['user_id'])
    if not user:
        return failure_response("User not found", 404)

    # Add the user to the course whether student or instructor
    if body['type'] == 'student':
        course.students.append(user)
    elif body['type'] == 'instructor':
        course.instructors.append(user)
    else:
        return failure_response("Invalid user type", 400)

    db.session.commit()
    return json.dumps(course.serialize()), 200

# Create an assignment for a course
@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def create_assignment_for_course(course_id):
    body = json.loads(request.data)
    if not body or 'title' not in body or 'due_date' not in body:
        return failure_response("Missing required fields: title and due_date", 400)

    course = Course.query.filter_by(id=course_id).first()
    if not course or course is None:
        return failure_response("Course not found", 404)

    due_date = body['due_date']

    new_assignment = Assignment(title=body['title'], due_date=due_date, course_id=course_id)
    db.session.add(new_assignment)
    db.session.commit()

    return json.dumps(new_assignment.serialize()), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
