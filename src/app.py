from db import Cuisine, User, Recipe, db
from flask import Flask, request, jsonify
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
    return json.dumps({"success": True, "cuisines": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

# your routes here
#get all cuisines
@app.route('/api/cuisines/', methods=['GET'])
def get_cuisines():
    cuisines = [t.serialize() for t in Cuisine.query.all()]
    return success_response(cuisines)

#create a cuisine
@app.route("/api/cuisines/", methods=["POST"])
def create_cuisine():
    body = json.loads(request.data)
    if not body or "description" not in body or "name" not in body:
        return failure_response("Description or name missing!", 400)
    
    new_cuisine = Cuisine(description=body['description'], name=body['name'])
    db.session.add(new_cuisine)
    db.session.commit()
    return json.dumps(new_cuisine.serialize()), 201

#get a specific cuisine
@app.route("/api/cuisines/<string:cuisine_name>/", methods=["GET"])
def get_cuisine(cuisine_name):
    cuisines = Cuisine.query.filter_by(name=cuisine_name).all()

    if cuisines is None:
        return failure_response("cuisine not found!")
    serialized_cuisines = [cuisine.serialize() for cuisine in cuisines]
    return jsonify(serialized_cuisines)

#delete a cuisine
@app.route("/api/cuisines/<int:cuisine_id>/", methods=["DELETE"])
def delete_cuisine(cuisine_id):
    cuisine = Cuisine.query.filter_by(id=cuisine_id).first()
    if cuisine is None:
        return failure_response("Task not found!")
    
    db.session.delete(cuisine)
    db.session.commit()
    return json.dumps(cuisine.serialize()), 200

# Create a new user
@app.route('/api/users/', methods=['POST'])
def create_user():
    body = json.loads(request.data)
    if not body or 'name' not in body:
        return failure_response("Missing required fields: name", 400)

    new_user = User(name=body['name'])
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

# Create a recipe for a cuisine
@app.route("/api/cuisines/<int:cuisine_id>/recipe/", methods=["POST"])
def create_recipe_for_cuisine(cuisine_id):
    body = json.loads(request.data)
    if not body or 'title' not in body or 'date_made' not in body:
        return failure_response("Missing required fields: title and date_made", 400)

    cuisine = Cuisine.query.filter_by(id=cuisine_id).first()
    if not cuisine or cuisine is None:
        return failure_response("cuisine not found", 404)

    date_made = body['date_made']

    new_recipe = Recipe(title=body['title'], date_made=date_made, cuisine_id=cuisine_id)
    db.session.add(new_recipe)
    db.session.commit()

    return json.dumps(new_recipe.serialize()), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
