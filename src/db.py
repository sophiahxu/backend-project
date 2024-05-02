from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table_users = db.Table('recipe_users_association', db.Model.metadata,
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

# your classes here
class Cuisine(db.Model):    
  __tablename__ = "cuisine"    
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#   description = db.Column(db.String, nullable=False)
  name = db.Column(db.String, nullable=False)
  recipes = db.relationship("Recipe", cascade="delete")

  def __init__(self, **kwargs):
    # self.description = kwargs.get("description", "")
    self.name = kwargs.get("name", "")

  def serialize(self):    
    return {        
        "id": self.id,
        # "description": self.description,
        "name": self.name,
        "recipes": [recipe.simple_serialize() for recipe in self.recipes]
    }
  
  # Serialize a cuisine without recipes, or user_cuisines fields
  def serialize_cuisine(self):
      return {
          "id": self.id,
        #   "description": self.description,
          "name": self.name
      }

class Recipe(db.Model):
  __tablename__ = "recipe"

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  title = db.Column(db.String, nullable=False)
  date_made = db.Column(db.Integer, nullable=False)
  description = db.Column(db.String, nullable=False)
  cuisine_id = db.Column(db.Integer, db.ForeignKey("cuisine.id"))
  recipe_user_creator = db.relationship("User", secondary='recipe_users_association', back_populates="created_recipes")

  def __init__(self, **kwargs):
        self.title= kwargs.get("title")
        self.date_made=kwargs.get("date_made")
        self.cuisine_id= kwargs.get("cuisine_id")

  def serialize(self):
    cuisine = Cuisine.query.filter_by(id=self.cuisine_id).first()
    return {
    'id': self.id,
    'title': self.title,
    'date_made': self.date_made,
    'cuisine': cuisine.serialize_cuisine(),
    "description": self.description,
    "recipe_user_creator": [x.simple_serialize() for x in self.recipe_user_creator ]
    }
  
  def simple_serialize(self):
     return {
        'id': self.id,
        'title': self.title,
        'date_made': self.date_made,
        "description": self.description,
     }

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    created_recipes = db.relationship("Recipe", secondary=association_table_users, back_populates="recipe_user_creator")

    def __init__(self,**kwargs):
        self.name= kwargs.get("name")

    def serialize(self):
        taught_recipe_ids = [recipe.id for recipe in self.created_recipes]
        
        recipes = []
        for recipe_id in taught_recipe_ids:
            recipe = Recipe.query.filter_by(id=recipe_id).first()
            if recipe:
                recipes.append(recipe.simple_serialize())
        
        return {
            "id": self.id,
            "name": self.name,
            "cuisines": recipes
        }
    
    def simple_serialize(self):
       return {
            "id": self.id,
            "name": self.name,
        }