from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table_instructor = db.Table('course_instructor_association', db.Model.metadata,
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

association_table_student = db.Table('course_student_association', db.Model.metadata,
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

# your classes here
class Course(db.Model):    
  __tablename__ = "course"    
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  code = db.Column(db.String, nullable=False)
  name = db.Column(db.String, nullable=False)
  assignments = db.relationship("Assignment", cascade="delete")
  instructors = db.relationship("User", secondary='course_instructor_association', back_populates="courses_taught")
  students = db.relationship("User", secondary='course_student_association', back_populates="courses_enrolled")

  def __init__(self, **kwargs):
    self.code = kwargs.get("code", "")
    self.name = kwargs.get("name", "")

  def serialize(self):    
    return {        
        "id": self.id,
        "code": self.code,
        "name": self.name,
        "assignments": [assignment.simple_serialize() for assignment in self.assignments],
        "instructors": [instructor.simple_serialize() for instructor in self.instructors],
        "students": [student.simple_serialize() for student in self.students] 
    }
  
  # Serialize a course without assignments, students, or instructors fields
  def serialize_course(self):
      return {
          "id": self.id,
          "code": self.code,
          "name": self.name
      }

class Assignment(db.Model):
  __tablename__ = "assignment"

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  title = db.Column(db.String, nullable=False)
  due_date = db.Column(db.Integer, nullable=False)
  course_id = db.Column(db.Integer, db.ForeignKey("course.id"))

  def __init__(self, **kwargs):
        self.title= kwargs.get("title")
        self.due_date=kwargs.get("due_date")
        self.course_id= kwargs.get("course_id")

  def serialize(self):
    course = Course.query.filter_by(id=self.course_id).first()
    return {
    'id': self.id,
    'title': self.title,
    'due_date': self.due_date,
    'course': course.serialize_course()
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
    courses_taught = db.relationship("Course", secondary=association_table_instructor, back_populates="instructors")
    courses_enrolled = db.relationship("Course", secondary=association_table_student, back_populates="students")

    def __init__(self,**kwargs):
        self.name= kwargs.get("name")
        self.netid= kwargs.get("netid")

    def serialize(self):
        enrolled_course_ids = [course.id for course in self.courses_enrolled]
        taught_course_ids = [course.id for course in self.courses_taught]
        all_course_ids = enrolled_course_ids + taught_course_ids
        
        courses = []
        for course_id in all_course_ids:
            course = Course.query.filter_by(id=course_id).first()
            if course:
                courses.append(course.serialize_course())
        
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "courses": courses
        }
    
    def simple_serialize(self):
       return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid
        }