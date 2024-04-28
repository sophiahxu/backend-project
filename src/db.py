from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table_instructor = db.Table('cuisine_instructor_association', db.Model.metadata,
    db.Column('cuisine_id', db.Integer, db.ForeignKey('cuisine.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

association_table_student = db.Table('cuisine_student_association', db.Model.metadata,
    db.Column('cuisine_id', db.Integer, db.ForeignKey('cuisine.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

# your classes here
class Cuisine(db.Model):    
  __tablename__ = "cuisine"    
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  description = db.Column(db.String, nullable=False)
  name = db.Column(db.String, nullable=False)
  recipes = db.relationship("Recipe", cascade="delete")
  instructors = db.relationship("User", secondary='cuisine_instructor_association', back_populates="cuisines_taught")
  students = db.relationship("User", secondary='cuisine_student_association', back_populates="cuisines_enrolled")

  def __init__(self, **kwargs):
    self.description = kwargs.get("description", "")
    self.name = kwargs.get("name", "")

  def serialize(self):    
    return {        
        "id": self.id,
        "description": self.description,
        "name": self.name,
        "recipes": [recipe.simple_serialize() for recipe in self.recipes],
        "instructors": [instructor.simple_serialize() for instructor in self.instructors],
        "students": [student.simple_serialize() for student in self.students] 
    }
  
  # Serialize a cuisine without recipes, students, or instructors fields
  def serialize_cuisine(self):
      return {
          "id": self.id,
          "description": self.description,
          "name": self.name
      }

class Recipe(db.Model):
  __tablename__ = "recipe"

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  title = db.Column(db.String, nullable=False)
  due_date = db.Column(db.Integer, nullable=False)
  cuisine_id = db.Column(db.Integer, db.ForeignKey("cuisine.id"))

  def __init__(self, **kwargs):
        self.title= kwargs.get("title")
        self.due_date=kwargs.get("due_date")
        self.cuisine_id= kwargs.get("cuisine_id")

  def serialize(self):
    cuisine = cuisine.query.filter_by(id=self.cuisine_id).first()
    return {
    'id': self.id,
    'title': self.title,
    'due_date': self.due_date,
    'cuisine': cuisine.serialize_cuisine()
    }
  
  def simple_serialize(self):
     return {
        'id': self.id,
        'title': self.title,
        'due_date': self.due_date
     }

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    cuisines_taught = db.relationship("Cuisine", secondary=association_table_instructor, back_populates="instructors")
    cuisines_enrolled = db.relationship("Cuisine", secondary=association_table_student, back_populates="students")

    def __init__(self,**kwargs):
        self.name= kwargs.get("name")
        self.netid= kwargs.get("netid")

    def serialize(self):
        enrolled_cuisine_ids = [cuisine.id for cuisine in self.cuisines_enrolled]
        taught_cuisine_ids = [cuisine.id for cuisine in self.cuisines_taught]
        all_cuisine_ids = enrolled_cuisine_ids + taught_cuisine_ids
        
        cuisines = []
        for cuisine_id in all_cuisine_ids:
            cuisine = cuisine.query.filter_by(id=cuisine_id).first()
            if cuisine:
                cuisines.append(cuisine.serialize_cuisine())
        
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "cuisines": cuisines
        }
    
    def simple_serialize(self):
       return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid
        }