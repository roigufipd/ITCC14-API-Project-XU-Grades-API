from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from flask_cors import CORS

app = Flask(__name__,
            static_folder='../Front-end',
            template_folder='../Front-end'
            )
CORS(app) # This will enable CORS for all routes and origins
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

#Models for each resource
class StudentModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(255), nullable=False)
    enrollment_status = db.Column(db.String(50), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semesters = db.relationship('SemesterModel', backref='student', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Student(name = {self.student_name}, course = {self.course})"

class SemesterModel(db.Model):
    id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_model.id'), nullable=False)

    classes = db.relationship('ClassModel', backref='semester', lazy=True, cascade="all, delete-orphan")

    __table_args__ = (db.PrimaryKeyConstraint('id', 'student_id'),)

    def __repr__(self):
        return f"Semester(name={self.name})"

class ClassModel(db.Model):
    id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    semester_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)

    grades = db.relationship('GradeModel', backref='class', lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        db.PrimaryKeyConstraint('id', 'semester_id', 'student_id'),
        db.ForeignKeyConstraint(['semester_id', 'student_id'], ['semester_model.id', 'semester_model.student_id']),
    )

class GradeModel(db.Model):
    id = db.Column(db.Integer, nullable=False)
    midterm_grade = db.Column(db.Integer, nullable=True)
    final_grade = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    class_id = db.Column(db.Integer, nullable=False)
    semester_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('id', 'class_id', 'semester_id', 'student_id'),
        db.ForeignKeyConstraint(['class_id', 'semester_id', 'student_id'], ['class_model.id', 'class_model.semester_id', 'class_model.student_id']),
    )

student_args = reqparse.RequestParser()
student_args.add_argument('student_name', type=str, required=True, help="Student name cannot be empty")
student_args.add_argument('enrollment_status', type=str, required=True, help="Enrollment status cannot be empty")
student_args.add_argument('course', type=str, required=True, help="Course cannot be empty")
student_args.add_argument('year', type=int, required=True, help="Year cannot be empty")

student_patch_args = reqparse.RequestParser()
student_patch_args.add_argument('student_name', type=str, required=False)
student_patch_args.add_argument('enrollment_status', type=str, required=False)
student_patch_args.add_argument('course', type=str, required=False)
student_patch_args.add_argument('year', type=int, required=False)

semester_args = reqparse.RequestParser()
semester_args.add_argument('name', type=str, required=True, help="Semester name cannot be empty")
semester_args.add_argument('description', type=str, required=False)

semester_patch_args = reqparse.RequestParser()
semester_patch_args.add_argument('name', type=str, required=False)
semester_patch_args.add_argument('description', type=str, required=False)

class_args = reqparse.RequestParser()
class_args.add_argument('name', type=str, required=True, help="Class name cannot be empty")
class_args.add_argument('description', type=str, required=False)

class_patch_args = reqparse.RequestParser()
class_patch_args.add_argument('name', type=str, required=False)
class_patch_args.add_argument('description', type=str, required=False)

grade_patch_args = reqparse.RequestParser()
grade_patch_args.add_argument('midterm_grade', type=int, required=False)
grade_patch_args.add_argument('final_grade', type=int, required=False)
grade_patch_args.add_argument('description', type=str, required=False)

grade_args = reqparse.RequestParser()
grade_args.add_argument('midterm_grade', type=int, required=False)
grade_args.add_argument('final_grade', type=int, required=False)
grade_args.add_argument('description', type=str, required=False)

gradeFields = {
    'id': fields.Integer,
    'midterm_grade': fields.Integer,
    'final_grade': fields.Integer,
    'description': fields.String
}

classFields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'grades': fields.List(fields.Nested(gradeFields))
}

semesterFields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'classes': fields.List(fields.Nested(classFields))
}

studentFields = {
    'student_id': fields.Integer(attribute='id'),
    'student_name': fields.String,
    'enrollment_status': fields.String,
    'course': fields.String,
    'year': fields.Integer,
    'semesters': fields.List(fields.Nested(semesterFields))
}

#CRUD Functionalities
class Students(Resource):
    @marshal_with(studentFields)
    def get(self):
        students = StudentModel.query.all()
        return students
    
    @marshal_with(studentFields)
    def post(self):
        args = student_args.parse_args()
        student = StudentModel(
            student_name=args["student_name"],
            enrollment_status=args["enrollment_status"],
            course=args["course"],
            year=args["year"]
        )
        db.session.add(student)
        db.session.commit()
        students = StudentModel.query.all()
        return students, 201
    
class Student(Resource):
    @marshal_with(studentFields)
    def get(self, id):
        student = StudentModel.query.filter_by(id=id).first()
        if not student:
            abort(404, "Student not found")
        return student
    
    @marshal_with(studentFields)
    def patch(self, id):
        args = student_patch_args.parse_args()
        student = StudentModel.query.filter_by(id=id).first()
        if not student:
            abort(404, "Student not found")
        if args['student_name'] is not None:
            student.student_name = args["student_name"]
        if args['enrollment_status'] is not None:
            student.enrollment_status = args["enrollment_status"]
        if args['course'] is not None:
            student.course = args["course"]
        if args['year'] is not None:
            student.year = args["year"]
        db.session.commit()
        return student
    
    @marshal_with(studentFields)
    def delete(self, id):
        student = StudentModel.query.filter_by(id=id).first()
        if not student:
            abort(404, "Student not found")
        db.session.delete(student)
        db.session.commit()
        students = StudentModel.query.all()
        return students, 200
    
class SemesterList(Resource):
    @marshal_with(semesterFields)
    def get(self, student_id):
        student = StudentModel.query.filter_by(id=student_id).first()
        if not student:
            abort(404, f"Student with id {student_id} not found")
        return student.semesters

    @marshal_with(semesterFields)
    def post(self, student_id):
        args = semester_args.parse_args()
        student = StudentModel.query.filter_by(id=student_id).first()
        if not student:
            abort(404, f"Student with id {student_id} not found")
        
        max_id = db.session.query(db.func.max(SemesterModel.id)).filter_by(student_id=student_id).scalar() or 0
        new_id = max_id + 1

        semester = SemesterModel(id=new_id, name=args['name'], description=args.get('description'), student_id=student_id)
        db.session.add(semester)
        db.session.commit()
        db.session.refresh(semester)
        return semester, 201

class Semester(Resource):
    @marshal_with(semesterFields)
    def patch(self, student_id, semester_id):
        args = semester_patch_args.parse_args()
        semester = SemesterModel.query.filter_by(id=semester_id, student_id=student_id).first()
        if not semester:
            abort(404, f"Semester with id {semester_id} for student {student_id} not found")

        if args['name'] is not None:
            semester.name = args['name']
        if args['description'] is not None:
            semester.description = args['description']
        
        db.session.commit()
        return semester

class ClassList(Resource):
    @marshal_with(classFields)
    def get(self, student_id, semester_id):
        semester = SemesterModel.query.filter_by(id=semester_id, student_id=student_id).first()
        if not semester:
            abort(404, f"Semester with id {semester_id} for student {student_id} not found")
        return semester.classes

    @marshal_with(classFields)
    def post(self, student_id, semester_id):
        args = class_args.parse_args()
        semester = SemesterModel.query.filter_by(id=semester_id, student_id=student_id).first()
        if not semester:
            abort(404, f"Semester with id {semester_id} for student {student_id} not found")

        max_id = db.session.query(db.func.max(ClassModel.id)).filter_by(semester_id=semester_id, student_id=semester.student_id).scalar() or 0
        new_id = max_id + 1

        new_class = ClassModel(
            id=new_id,
            name=args['name'],
            description=args.get('description'),
            semester_id=semester_id,
            student_id=semester.student_id
        )
        db.session.add(new_class)
        db.session.commit()
        db.session.refresh(new_class)
        return new_class, 201

class Class(Resource):
    @marshal_with(classFields)
    def patch(self, student_id, semester_id, class_id):
        args = class_patch_args.parse_args()
        target_class = ClassModel.query.filter_by(id=class_id, semester_id=semester_id, student_id=student_id).first()
        if not target_class:
            abort(404, f"Class with id {class_id} not found in this path")

        if args['name'] is not None:
            target_class.name = args['name']
        if args['description'] is not None:
            target_class.description = args['description']
        
        db.session.commit()
        return target_class

class GradeList(Resource):
    @marshal_with(gradeFields)
    def get(self, student_id, semester_id, class_id):
        target_class = ClassModel.query.filter_by(id=class_id, semester_id=semester_id, student_id=student_id).first()
        if not target_class:
            abort(404, f"Class with id {class_id} not found in this path")
        return target_class.grades

    @marshal_with(gradeFields)
    def post(self, student_id, semester_id, class_id):
        args = grade_args.parse_args()
        target_class = ClassModel.query.filter_by(id=class_id, semester_id=semester_id, student_id=student_id).first()
        if not target_class:
            abort(404, f"Class with id {class_id} not found in this path")

        max_id = db.session.query(db.func.max(GradeModel.id)).filter_by(class_id=class_id, semester_id=target_class.semester_id, student_id=target_class.student_id).scalar() or 0
        new_id = max_id + 1

        new_grade = GradeModel(
            id=new_id,
            midterm_grade=args.get('midterm_grade'),
            final_grade=args.get('final_grade'),
            description=args.get('description'),
            class_id=class_id,
            semester_id=target_class.semester_id,
            student_id=target_class.student_id
        )
        db.session.add(new_grade)
        db.session.commit()
        db.session.refresh(new_grade)
        return new_grade, 201

class Grade(Resource):
    @marshal_with(gradeFields)
    def patch(self, student_id, semester_id, class_id, grade_id):
        args = grade_patch_args.parse_args()
        grade = GradeModel.query.filter_by(id=grade_id, class_id=class_id, semester_id=semester_id, student_id=student_id).first()
        if not grade:
            abort(404, f"Grade with id {grade_id} not found in this path")

        if args['midterm_grade'] is not None:
            grade.midterm_grade = args['midterm_grade']
        if args['final_grade'] is not None:
            grade.final_grade = args['final_grade']
        if args['description'] is not None:
            grade.description = args['description']
        
        db.session.commit()
        return grade

api.add_resource(Students, '/api/students/semester/classes/grades/', '/api/students/')
api.add_resource(Student, '/api/students/<int:id>') // Displays the Student ID associated with the students
api.add_resource(SemesterList, '/api/students/<int:student_id>/semesters/') // Displays the Semesters
api.add_resource(Semester, '/api/students/<int:student_id>/semesters/<int:semester_id>') // Displays each Semester that the Student takes
api.add_resource(ClassList, '/api/students/<int:student_id>/semesters/<int:semester_id>/classes/') // Displays the Classes under Semesters
api.add_resource(Class, '/api/students/<int:student_id>/semesters/<int:semester_id>/classes/<int:class_id>') // Displays each Class
api.add_resource(GradeList, '/api/students/<int:student_id>/semesters/<int:semester_id>/classes/<int:class_id>/grades/') // Displays the grades
api.add_resource(Grade, '/api/students/<int:student_id>/semesters/<int:semester_id>/classes/<int:class_id>/grades/<int:grade_id>') // Displays grades of each student

@app.route('/')
def home():
    return render_template('index.html',
                           css_file=url_for('static', filename='styles.css'),
                           js_file=url_for('static', filename='script.js'),
                           logo_img=url_for('static', filename='img/XU_Logotype_Color.png'),
                           alt_logo_img=url_for('static', filename='img/XU_Logo_2.png')
                           )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
